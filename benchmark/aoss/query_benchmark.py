#!/usr/bin/env python3
"""
Simple PPL benchmark runner for Amazon OpenSearch Serverless (AOSS).

Given a file where each non-comment line contains "<query_id> <query text>",
this script executes the supplied PPL exactly as written and measures how long
each query takes when executed via the PPL endpoint. Requests are dispatched
through awscurl so standard AWS credentials (or profiles) can be reused.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import statistics
import subprocess
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


DEFAULT_ITERATIONS = 100
DEFAULT_WARMUP = 1


@dataclass
class QueryResult:
    query_id: str
    query: str
    durations: List[float]
    error: Optional[str] = None

    def to_dict(self) -> dict:
        if self.error:
            return {
                "query_id": self.query_id,
                "query": self.query,
                "error": self.error,
            }
        stats = {
            "min_seconds": min(self.durations),
            "max_seconds": max(self.durations),
            "avg_seconds": sum(self.durations) / len(self.durations),
            "median_seconds": statistics.median(self.durations),
            "p90_seconds": percentile(self.durations, 90),
            "p99_seconds": percentile(self.durations, 99),
        }
        return {
            "query_id": self.query_id,
            "query": self.query,
            "iterations": len(self.durations),
            "timings_seconds": self.durations,
            **stats,
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Benchmark AOSS PPL queries loaded from a file."
    )
    parser.add_argument(
        "--endpoint",
        required=True,
        help="AOSS collection endpoint, e.g. https://xxx.us-east-1.aoss.amazonaws.com",
    )
    parser.add_argument(
        "--queries",
        required=True,
        type=Path,
        help="Path to a file containing 'query_id <query>' entries (one per line).",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=DEFAULT_ITERATIONS,
        help=f"Number of measured executions per query (default: {DEFAULT_ITERATIONS}).",
    )
    parser.add_argument(
        "--warmup-runs",
        type=int,
        default=DEFAULT_WARMUP,
        help=f"Number of warmup executions before benchmarking (default: {DEFAULT_WARMUP}).",
    )
    parser.add_argument(
        "--awscurl-path",
        default="awscurl",
        help="Path to the awscurl executable (default: awscurl).",
    )
    parser.add_argument(
        "--region",
        default=os.environ.get("AWS_REGION")
        or os.environ.get("AWS_DEFAULT_REGION"),
        help="AWS region for signing (defaults to AWS_REGION / AWS_DEFAULT_REGION).",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=60,
        help="Timeout in seconds for each query execution.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional path to write a JSON copy of the benchmark report.",
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        help="If provided, store each query response JSON under this directory.",
    )
    parser.add_argument(
        "--csv-output",
        type=Path,
        help="Optional path to write query_id,P90,max latency CSV.",
    )
    args = parser.parse_args()
    if not args.region:
        parser.error(
            "--region is required (set the flag or AWS_REGION / AWS_DEFAULT_REGION)"
        )
    if args.iterations < 100:
        parser.error("--iterations must be at least 100 to ensure stable latency stats")
    if args.warmup_runs < 0:
        parser.error("--warmup-runs must be zero or positive")
    return args


def load_queries(path: Path) -> List[tuple[str, str]]:
    """
    Read queries from file. Each non-empty, non-comment line must start with an ID
    followed by a space and the query text. Lines starting with # or -- are comments.
    """
    if not path.exists():
        raise FileNotFoundError(f"Queries file not found: {path}")

    queries: List[tuple[str, str]] = []
    with path.open(encoding="utf-8") as fh:
        for raw_line in fh:
            stripped = raw_line.strip()
            if not stripped:
                continue
            if stripped.startswith("#") or stripped.startswith("--"):
                continue
            parts = stripped.split(None, 1)
            if len(parts) < 2:
                raise ValueError(
                    f"Expected 'query_id <query>' format but found '{stripped}' in {path}"
                )
            query_id, query_body = parts[0], parts[1].strip()
            if not query_body:
                raise ValueError(f"Query body missing for identifier '{query_id}' in {path}")
            if query_body.endswith(";"):
                query_body = query_body[:-1].strip()
            queries.append((query_id, query_body))

    if not queries:
        raise ValueError(f"No queries parsed from {path}")

    return queries


def _safe_query_id(name: str) -> str:
    """Collapse query IDs into filesystem-friendly names."""
    return re.sub(r"[^A-Za-z0-9._-]", "_", name) or "query"


def dump_query_output(
    query_id: str,
    iteration: int,
    body: str,
    directory: Path,
) -> None:
    filename = f"{_safe_query_id(query_id)}_run{iteration:02d}.json"
    target = directory / filename
    target.write_text(body if body else "{}", encoding="utf-8")


def run_ppl_query(
    awscurl_path: str,
    url: str,
    region: str,
    query: str,
    timeout: int,
) -> Tuple[float, str]:
    """
    Execute a single PPL query via awscurl and return elapsed wall time.
    Raises RuntimeError when awscurl or the endpoint reports an error.
    """
    payload = json.dumps({"query": query}, separators=(",", ":"), ensure_ascii=False)
    tmp_path: Optional[Path] = None
    start = time.perf_counter()
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
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
            "Content-Type: application/json",
            "--data",
            f"@{tmp_path}",
            url,
        ]
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout, check=False
        )
    finally:
        if tmp_path and tmp_path.exists():
            tmp_path.unlink()
    elapsed = time.perf_counter() - start
    if result.returncode != 0:
        raise RuntimeError(
            f"awscurl exited with {result.returncode}: {result.stderr.strip()}"
        )

    stdout = result.stdout.strip()
    raw_body = stdout or "{}"

    try:
        parsed = json.loads(raw_body)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Invalid JSON returned by PPL endpoint") from exc
    status = parsed.get("status", 200)
    if isinstance(status, str):
        try:
            status = int(status)
        except ValueError:
            status = 500
    if status >= 400 or "error" in parsed:
        message = parsed.get("error") or parsed.get("message") or "Unknown error"
        raise RuntimeError(f"PPL query failed with status {status}: {message}")
    return elapsed, raw_body


def percentile(values: List[float], pct: float) -> float:
    """Return the percentile using linear interpolation."""
    if not values:
        raise ValueError("Cannot compute percentile of empty list")
    if pct <= 0:
        return min(values)
    if pct >= 100:
        return max(values)
    sorted_vals = sorted(values)
    k = (pct / 100.0) * (len(sorted_vals) - 1)
    lower = math.floor(k)
    upper = math.ceil(k)
    if lower == upper:
        return sorted_vals[int(k)]
    fraction = k - lower
    return sorted_vals[lower] + (sorted_vals[upper] - sorted_vals[lower]) * fraction


def write_csv_report(results: List[QueryResult], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["query_id", "p90_seconds", "max_seconds"])
        for res in results:
            if res.error or not res.durations:
                writer.writerow([res.query_id, "", ""])
                continue
            stats = res.to_dict()
            writer.writerow(
                [
                    res.query_id,
                    f"{stats['p90_seconds']:.6f}",
                    f"{stats['max_seconds']:.6f}",
                ]
            )


def main() -> None:
    args = parse_args()
    if args.results_dir:
        args.results_dir.mkdir(parents=True, exist_ok=True)
    query_defs = load_queries(args.queries)
    ppl_url = args.endpoint.rstrip("/") + "/_plugins/_ppl"
    results_map: Dict[str, QueryResult] = {
        query_id: QueryResult(query_id=query_id, query=query, durations=[])
        for query_id, query in query_defs
    }

    if args.warmup_runs:
        print(f"Running {args.warmup_runs} warmup pass(es)...")
        for warmup in range(1, args.warmup_runs + 1):
            print(f"  Warmup pass {warmup}")
            for query_id, query in query_defs:
                run_ppl_query(
                    args.awscurl_path,
                    ppl_url,
                    args.region,
                    query,
                    args.timeout,
                )

    for iteration in range(1, args.iterations + 1):
        print(f"\nIteration {iteration}/{args.iterations}")
        for query_id, query in query_defs:
            result = results_map[query_id]
            if result.error:
                print(f"  [{query_id}] Skipped (previous error: {result.error})")
                continue
            try:
                duration, response_body = run_ppl_query(
                    args.awscurl_path,
                    ppl_url,
                    args.region,
                    query,
                    args.timeout,
                )
                result.durations.append(duration)
                if args.results_dir:
                    dump_query_output(query_id, iteration, response_body, args.results_dir)
                print(f"  [{query_id}] {duration:.4f}s")
            except Exception as exc:  # noqa: BLE001
                result.error = str(exc)
                print(f"  [{query_id}] Error: {result.error}")

    results: List[QueryResult] = [results_map[qid] for qid, _ in query_defs]

    print("\nSummary per query:")
    for query_id, _ in query_defs:
        result = results_map[query_id]
        if result.error:
            print(f"[{query_id}] Error: {result.error}")
            continue
        if not result.durations:
            print(f"[{query_id}] No successful runs recorded.")
            continue
        stats = result.to_dict()
        print(
            f"[{query_id}] Avg {stats['avg_seconds']:.4f}s | "
            f"Min {stats['min_seconds']:.4f}s | "
            f"P90 {stats['p90_seconds']:.4f}s | "
            f"P99 {stats['p99_seconds']:.4f}s | "
            f"Max {stats['max_seconds']:.4f}s"
        )

    report = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "endpoint": args.endpoint,
        "queries_file": str(args.queries),
        "iterations": args.iterations,
        "warmup_runs": args.warmup_runs,
        "results": [res.to_dict() for res in results],
    }

    if args.results_dir:
        print(f"\nSaved raw query responses to {args.results_dir}")

    if args.csv_output:
        write_csv_report(results, args.csv_output)
        print(f"Saved CSV summary to {args.csv_output}")

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"\nSaved benchmark report to {args.output}")


if __name__ == "__main__":
    main()
