import requests
import time

# Configuration
url = "http://localhost:9200/_plugins/_ppl/"
headers = {
    "Content-Type": "application/x-ndjson",
}

# List of PPL queries to test
queries = [
    {"query": "source=testindex | where v=1"},
    {"query": "source=testindex | stats count()"},
]

def send_query(query):
    data = query
    start = time.time()
    response = requests.post(url, headers=headers, json=data)
    end = time.time()
    latency_ms = (end - start) * 1000
    return latency_ms, response.status_code, response.text[:100]  # preview part of the response

def main():
    for i, query in enumerate(queries, start=1):
        latency, status, preview = send_query(query)
        print(f"Query {i}: {query['query']}")
        print(f"  Latency: {latency:.2f} ms")
        print(f"  Status:  {status}")
        print(f"  Response Preview: {preview.strip()}...\n")

if __name__ == "__main__":
    main()
