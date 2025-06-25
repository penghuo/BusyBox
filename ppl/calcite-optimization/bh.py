import requests
import time
import statistics
from collections import defaultdict
from datetime import datetime

# Configuration
url = "http://localhost:9200/_plugins/_ppl/"
headers = {
    "Content-Type": "application/x-ndjson",
    "User-Agent": "vscode-restclient"
}

# List of PPL queries to test
queries = [
    {"query": "source=testindex | where v=1"},
    {"query": "source=testindex | stats count()"},
    {"query": "source=testindex | where v=1 | stats count()"}
]

def send_query(query):
    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S,%f")[:-3]
    start = time.time()
    response = requests.post(url, headers=headers, json=query)
    end = time.time()
    latency = (end - start) * 1000  # latency in milliseconds
    print(f"[{timestamp}] Query: {query['query']}, Latency: {latency:.2f} ms")
    return latency


def calculate_p90(latencies):
    sorted_latencies = sorted(latencies)
    index = int(0.9 * len(sorted_latencies)) - 1
    return sorted_latencies[max(index, 0)]

def main():
    print("Warm-up run: Sending each query once...\n")
    for query in queries:
        _ = send_query(query)

    print("Running full query set 10 times...\n")
    query_to_latencies = defaultdict(list)

    for round_num in range(10):
        for query in queries:
            latency = send_query(query)
            query_to_latencies[query["query"]].append(latency)

    print("\nLatency metrics per query (based on 10 full rounds):\n")
    for i, (query_str, latencies) in enumerate(query_to_latencies.items(), start=1):
        print(f"Query {i}: {query_str}")
        print(f"  Max latency: {max(latencies):.2f} ms")
        print(f"  P90 latency: {calculate_p90(latencies):.2f} ms")
        print(f"  Avg latency: {statistics.mean(latencies):.2f} ms\n")

if __name__ == "__main__":
    main()
