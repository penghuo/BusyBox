import json
from pathlib import Path

def convert(input_path: str, output_path: str, index_name: str = "opensearch_flights") -> None:
    input_file = Path(input_path)
    output_file = Path(output_path)

    with input_file.open("r", encoding="utf-8") as f:
        data = json.load(f)

    hits = data.get("hits", {}).get("hits", [])
    with output_file.open("w", encoding="utf-8") as out:
        for idx, hit in enumerate(hits):
            action = {"index": {"_index": index_name, "_id": str(idx)}}
            json.dump(action, out)
            out.write("\n")
            # store only the _source payload for reindexing
            source_doc = hit.get("_source", {})
            json.dump(source_doc, out)
            out.write("\n")

if __name__ == "__main__":
    convert("opensearch_results.json", "data.ndjson")
