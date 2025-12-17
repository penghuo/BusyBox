import argparse
import json
from itertools import cycle, islice
from pathlib import Path

DEFAULT_DOC_COUNT = 20000
DEFAULT_INDEX_NAME = "osi-otel-logs"


def load_hits(input_path: Path) -> list:
    raw = input_path.read_text(encoding="utf-8")
    if not raw.strip():
        raise ValueError(f"Input file {input_path} is empty")

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {input_path}: {exc}") from exc

    # If the payload looks like a search response, use its hits; otherwise treat the whole payload as one document.
    hits = data.get("hits", {}).get("hits", []) if isinstance(data, dict) else []
    if hits:
        return hits

    if isinstance(data, dict):
        return [{"_source": data}]

    raise ValueError(f"No hits found in {input_path}")


def write_ndjson(
    hits: list, output_path: Path, index_name: str, doc_count: int
) -> None:
    if doc_count <= 0:
        raise ValueError("doc_count must be positive")

    with output_path.open("w", encoding="utf-8") as out:
        # Repeat the available hits until we emit the requested doc_count.
        for idx, hit in enumerate(islice(cycle(hits), doc_count)):
            action = {"index": {"_index": index_name, "_id": str(idx)}}
            json.dump(action, out)
            out.write("\n")

            source = hit.get("_source")
            if source is None:
                raise ValueError("Hit is missing _source; cannot build document body")
            json.dump(source, out)
            out.write("\n")


def convert(
    input_path: str,
    output_path: str,
    index_name: str = DEFAULT_INDEX_NAME,
    doc_count: int = DEFAULT_DOC_COUNT,
) -> None:
    input_file = Path(input_path)
    output_file = Path(output_path)

    hits = load_hits(input_file)
    write_ndjson(hits, output_file, index_name, doc_count)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert an OpenSearch search response into bulk NDJSON."
    )
    parser.add_argument(
        "--input",
        default="opensearch_results.json",
        help="Search response JSON to read (default: opensearch_results.json)",
    )
    parser.add_argument(
        "--output",
        default="data.ndjson",
        help="NDJSON output path (default: data.ndjson)",
    )
    parser.add_argument(
        "--index",
        default=DEFAULT_INDEX_NAME,
        help=f"Index name to use in bulk actions (default: {DEFAULT_INDEX_NAME})",
    )
    parser.add_argument(
        "--doc-count",
        type=int,
        default=DEFAULT_DOC_COUNT,
        help=f"Number of documents to emit (default: {DEFAULT_DOC_COUNT})",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    convert(args.input, args.output, args.index, args.doc_count)
