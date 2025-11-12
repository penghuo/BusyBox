#!/usr/bin/env python3
"""
End-to-end pipeline that expands gzipped flow logs, converts them to JSONL-style
documents, and uploads them to an Amazon OpenSearch Serverless (AOSS) index.

For every *.gz file in the provided directory:
1. Stream-decompress the file.
2. Parse timestamp-prefixed JSON records (same layout handled by jsonl_builder.py).
3. Enrich each record with @timestamp/@message fields.
4. Send documents to the target index using the AOSS bulk API.
"""

from __future__ import annotations

import argparse
import gzip
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED, ALL_COMPLETED
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Tuple
from threading import Lock


DEFAULT_PATTERN = "*.gz"
MAX_AWSCURL_LOG_CHARS = 500
MAX_THROTTLE_RETRIES = 3

TIMESTAMP_RE = re.compile(
    r"(?P<ts>\d{4}-\d{2}-\d{2}T"
    r"\d{2}:\d{2}:\d{2}"
    r"(?:\.\d+)?"
    r"(?:Z|[+-]\d{2}:\d{2}))"
)

class BulkUploadError(RuntimeError):
    """Raised when the AOSS bulk API returns an error."""


def _trim_log(text: str) -> str:
    if len(text) <= MAX_AWSCURL_LOG_CHARS:
        return text
    return text[: MAX_AWSCURL_LOG_CHARS - 3] + "..."


class ProgressTracker:
    """Tracks total docs ingested across threads."""

    def __init__(self) -> None:
        self._lock = Lock()
        self.total = 0

    def add(self, count: int) -> int:
        with self._lock:
            self.total += count
            return self.total


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Decompress *.gz flow logs and upload them to AOSS using the bulk API.",
    )
    parser.add_argument(
        "--endpoint",
        required=True,
        help="AOSS collection endpoint, e.g. https://xxx.us-east-1.aoss.amazonaws.com",
    )
    parser.add_argument(
        "--index",
        required=True,
        help="Target index name inside the collection.",
    )
    parser.add_argument(
        "--input-dir",
        required=True,
        help="Directory containing gzipped log files.",
    )
    parser.add_argument(
        "--pattern",
        default=DEFAULT_PATTERN,
        help=f"Glob for selecting files under input-dir (default: {DEFAULT_PATTERN}).",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=500,
        help="Number of documents per bulk request.",
    )
    parser.add_argument(
        "--region",
        default=os.environ.get("AWS_REGION")
        or os.environ.get("AWS_DEFAULT_REGION"),
        help="AWS region for signing (defaults to AWS_REGION / AWS_DEFAULT_REGION env vars).",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=60,
        help="Timeout in seconds for each awscurl call.",
    )
    parser.add_argument(
        "--awscurl-path",
        default="awscurl",
        help="Path to the awscurl executable (default: awscurl).",
    )
    parser.add_argument(
        "--upload-workers",
        type=int,
        default=max(1, (os.cpu_count() or 2) // 2),
        help="Number of parallel bulk uploads per file.",
    )
    args = parser.parse_args()
    if args.batch_size <= 0:
        parser.error("--batch-size must be positive")
    if not args.region:
        parser.error(
            "--region is required (set flag or AWS_REGION / AWS_DEFAULT_REGION env var)"
        )
    return args


def gather_files(input_dir: Path, pattern: str) -> List[Path]:
    files = sorted(
        f for f in input_dir.glob(pattern) if f.is_file() and not f.name.startswith(".")
    )
    if not files:
        raise FileNotFoundError(
            f"No files found under {input_dir} for pattern '{pattern}'"
        )
    return files


def _update_brace_depth(
    line: str, depth: int, in_string: bool, escape_next: bool
) -> Tuple[int, bool, bool]:
    for char in line:
        if escape_next:
            escape_next = False
            continue
        if char == "\\":
            escape_next = True
            continue
        if char == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
    return depth, in_string, escape_next


def iter_records(stream: Iterable[str], source: Path) -> Iterator[Tuple[str, dict]]:
    """
    Stream timestamp-prefixed JSON blobs from a line iterator without loading it entirely.
    """
    timestamp: Optional[str] = None
    json_lines: List[str] = []
    depth = 0
    in_string = False
    escape_next = False
    for raw_line in stream:
        stripped = raw_line.strip()
        if timestamp is None:
            if not stripped:
                continue
            match = TIMESTAMP_RE.match(raw_line)
            if not match or match.start() != 0:
                raise ValueError(
                    f"Expected ISO8601 timestamp but saw '{stripped}' in {source}"
                )
            timestamp = match.group("ts")
            json_lines = []
            depth = 0
            in_string = False
            escape_next = False
            remainder = raw_line[match.end() :]
            if remainder.strip():
                json_lines.append(remainder)
                depth, in_string, escape_next = _update_brace_depth(
                    remainder, depth, in_string, escape_next
                )
                if depth == 0 and not in_string and not escape_next:
                    json_blob = "".join(json_lines).strip()
                    try:
                        payload = json.loads(json_blob)
                    except json.JSONDecodeError as exc:
                        raise ValueError(
                            f"Invalid JSON payload following {timestamp} in {source}"
                        ) from exc
                    yield timestamp, payload
                    timestamp = None
                    json_lines = []
            continue
        json_lines.append(raw_line)
        depth, in_string, escape_next = _update_brace_depth(
            raw_line, depth, in_string, escape_next
        )
        if depth == 0 and not in_string and not escape_next:
            json_blob = "".join(json_lines).strip()
            if not json_blob:
                raise ValueError(f"Empty JSON payload following {timestamp} in {source}")
            try:
                payload = json.loads(json_blob)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON payload following {timestamp} in {source}"
                ) from exc
            yield timestamp, payload
            timestamp = None
            json_lines = []
    if timestamp is not None:
        raise ValueError(f"Incomplete record at end of {source}")


def build_row(timestamp: str, payload: dict) -> dict:
    row = {
        "@timestamp": timestamp,
        "@message": json.dumps(payload, separators=(",", ":"), ensure_ascii=False),
    }
    row.update(payload)
    return row


def build_bulk_payload(documents: List[dict], index_name: str) -> str:
    lines: List[str] = []
    for doc in documents:
        action: Dict[str, Dict[str, str]] = {"index": {"_index": index_name}}
        lines.append(json.dumps(action, separators=(",", ":")))
        lines.append(json.dumps(doc, separators=(",", ":")))
    return "\n".join(lines) + "\n"


def send_bulk_request(
    awscurl_path: str,
    url: str,
    payload: str,
    region: str,
    timeout: int,
) -> Dict:
    backoff = 1.0
    max_attempts = MAX_THROTTLE_RETRIES + 1
    for attempt in range(1, max_attempts + 1):
        parsed, throttle_message = _single_bulk_attempt(
            awscurl_path, url, payload, region, timeout
        )
        if throttle_message is None:
            return parsed
        if attempt >= max_attempts:
            raise BulkUploadError(
                f"{throttle_message} (exhausted {MAX_THROTTLE_RETRIES} retries)"
            )
        print(
            f"{throttle_message}. Retrying in {backoff:.1f}s "
            f"(attempt {attempt+1}/{max_attempts})"
        )
        time.sleep(backoff)
        backoff *= 2


def _single_bulk_attempt(
    awscurl_path: str,
    url: str,
    payload: str,
    region: str,
    timeout: int,
) -> Tuple[Optional[Dict], Optional[str]]:
    tmp_path: Optional[Path] = None
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".jsonl", delete=False, encoding="utf-8"
    ) as tmp:
        tmp.write(payload)
        tmp.flush()
        tmp_path = Path(tmp.name)
    try:
        cmd = [
            awscurl_path,
            "--service",
            "aoss",
            "--region",
            region,
            "-X",
            "POST",
            "--header",
            "Content-Type: application/x-ndjson",
            "--data",
            f"@{tmp_path}",
            url,
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    finally:
        if tmp_path and tmp_path.exists():
            tmp_path.unlink()
    if result.returncode != 0:
        stderr = result.stderr.strip() if result.stderr else ""
        raise BulkUploadError(
            f"awscurl exited with {result.returncode}: {_trim_log(stderr)}"
        )
    if result.stdout:
        print(f"[awscurl] response: {_trim_log(result.stdout.strip())}")
    if result.stderr:
        print(f"[awscurl] stderr: {_trim_log(result.stderr.strip())}", file=sys.stderr)
    try:
        parsed = json.loads(result.stdout or "{}")
    except json.JSONDecodeError as exc:
        raise BulkUploadError("Unable to parse bulk response JSON") from exc
    if parsed.get("errors"):
        message, throttled = _summarize_bulk_error(parsed, result.stdout)
        if throttled:
            return None, message
        raise BulkUploadError(message)
    return parsed, None


def _summarize_bulk_error(parsed: Dict, raw_response: Optional[str]) -> Tuple[str, bool]:
    error_detail: Optional[Dict] = None
    error_status = None
    for item in parsed.get("items", []):
        index_info = item.get("index", {})
        err = index_info.get("error")
        if err:
            error_detail = err
            error_status = index_info.get("status")
            break
    message = "Bulk API reported errors"
    reason = ""
    err_type = ""
    if error_detail:
        err_type = error_detail.get("type") or ""
        reason = error_detail.get("reason") or ""
        message += f": status={error_status}, type={err_type}, reason={reason}"
    throttled = "throttl" in reason.lower() or "throttl" in err_type.lower()
    if not error_detail:
        message += " (no additional detail)"
    if raw_response:
        print(f"[bulk-error] full response: {raw_response}", file=sys.stderr)
    return message, throttled


def upload_batch(
    documents: List[dict],
    args: argparse.Namespace,
    bulk_url: str,
    progress: ProgressTracker,
) -> int:
    payload = build_bulk_payload(documents, args.index)
    send_bulk_request(
        args.awscurl_path,
        bulk_url,
        payload,
        args.region,
        args.timeout,
    )
    count = len(documents)
    new_total = progress.add(count)
    print(f"Bulk indexed {count} docs (total ingested {new_total})")
    return count


def decompress_gzip_to_file(source: Path) -> Path:
    tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
    tmp_path = Path(tmp.name)
    tmp.close()
    try:
        with gzip.open(source, "rb") as src_fh, tmp_path.open("wb") as dst_fh:
            shutil.copyfileobj(src_fh, dst_fh)
    except Exception:
        if tmp_path.exists():
            tmp_path.unlink()
        raise
    return tmp_path


def reshape_json_file(json_path: Path) -> Tuple[Path, int]:
    count = 0
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".jsonl", delete=False, encoding="utf-8"
    ) as tmp:
        tmp_path = Path(tmp.name)
        try:
            with json_path.open("r", encoding="utf-8") as reader:
                for timestamp, payload in iter_records(reader, json_path):
                    row = build_row(timestamp, payload)
                    tmp.write(json.dumps(row, ensure_ascii=False) + "\n")
                    count += 1
        except Exception:
            if tmp_path.exists():
                tmp_path.unlink()
            raise
    return tmp_path, count


def upload_jsonl_in_parallel(
    jsonl_path: Path,
    args: argparse.Namespace,
    bulk_url: str,
    progress: ProgressTracker,
) -> int:
    max_workers = max(1, args.upload_workers)
    pending = set()
    uploaded = 0

    def drain(block: bool) -> None:
        nonlocal pending, uploaded
        if not pending:
            return
        return_when = ALL_COMPLETED if block else FIRST_COMPLETED
        done, still_pending = wait(pending, return_when=return_when)
        pending = still_pending
        for future in done:
            uploaded += future.result()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        batch: List[dict] = []
        with jsonl_path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                doc = json.loads(line)
                batch.append(doc)
                if len(batch) >= args.batch_size:
                    future = executor.submit(
                        upload_batch, batch, args, bulk_url, progress
                    )
                    pending.add(future)
                    batch = []
                    if len(pending) >= max_workers * 2:
                        drain(block=False)
        if batch:
            future = executor.submit(
                upload_batch, batch, args, bulk_url, progress
            )
            pending.add(future)
        if pending:
            drain(block=True)
    return uploaded


def process_gzip_file(
    gz_path: Path,
    args: argparse.Namespace,
    bulk_url: str,
    progress: ProgressTracker,
) -> int:
    print(f"Processing {gz_path} ...")
    json_path = decompress_gzip_to_file(gz_path)
    try:
        jsonl_path, reshaped = reshape_json_file(json_path)
        try:
            uploaded = upload_jsonl_in_parallel(jsonl_path, args, bulk_url, progress)
        finally:
            if jsonl_path.exists():
                jsonl_path.unlink()
    finally:
        if json_path.exists():
            json_path.unlink()
    print(f"Finished {gz_path} (uploaded {uploaded} docs, reshaped {reshaped})")
    return uploaded


def ingest_gz_files(args: argparse.Namespace) -> None:
    input_dir = Path(args.input_dir).expanduser().resolve()
    if not input_dir.is_dir():
        raise NotADirectoryError(f"{input_dir} is not a directory")
    files = gather_files(input_dir, args.pattern)
    bulk_url = f"{args.endpoint.rstrip('/')}/_bulk"
    print(f"Bulk url {bulk_url}")

    progress = ProgressTracker()
    total_docs = 0
    for gz_path in files:
        total_docs += process_gzip_file(gz_path, args, bulk_url, progress)
    print(f"Successfully uploaded {total_docs} documents.")


def main() -> None:
    args = parse_args()
    try:
        ingest_gz_files(args)
    except Exception as exc:  # pylint: disable=broad-except
        print(str(exc), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
