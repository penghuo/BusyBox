import requests
import json

OPENSEARCH_HOST = "http://localhost:9200"
INDEX_PREFIX = "test"
INDEX_COUNT = 1000
DEPTH = 15
FIELDS_PER_LEVEL = 10

def prepare_recursive_map(depth, fields_count, prefix, index_id):
    if depth == 0:
        return {
            f"{prefix}_field{i}_idx{index_id}": {"type": "text"}
            for i in range(fields_count)
        }
    else:
        result = {}
        for i in range(fields_count):
            field_name = f"{prefix}_field{i}_depth{depth}"
            result[field_name] = {
                "type": "object",
                "properties": prepare_recursive_map(depth - 1, 1, field_name, index_id)
            }
        return result

def create_index(index_name, mapping_body):
    url = f"{OPENSEARCH_HOST}/{index_name}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        },
        "mappings": {
            "properties": mapping_body
        }
    }
    response = requests.put(url, headers=headers, data=json.dumps(payload))
    if response.status_code not in (200, 201):
        print(f"❌ Failed to create {index_name}: {response.status_code} - {response.text}")
    else:
        print(f"✅ Created index: {index_name}")

def main():
    for i in range(INDEX_COUNT):
        index_name = f"{INDEX_PREFIX}-{i}"
        mapping = prepare_recursive_map(DEPTH, FIELDS_PER_LEVEL, "root", i)
        create_index(index_name, mapping)

if __name__ == "__main__":
    main()
