import boto3
import json
import time
import statistics
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure these variables
FUNCTION_NAME = "flint-spark-on-aws-lambda:3"
REGION = "us-west-2"
ITERATIONS = 10
WARM_UP_ITERATIONS = 3

# Load the query set
with open('query_set.json', 'r') as f:
    QUERY_SET = json.load(f)

lambda_client = boto3.client('lambda', region_name=REGION)

def invoke_lambda(query):
    start_time = time.time()
    response = lambda_client.invoke(
        FunctionName=FUNCTION_NAME,
        InvocationType='RequestResponse',
        Payload=json.dumps({"query": query})
    )
    end_time = time.time()
    latency = (end_time - start_time) * 1000  # Convert to milliseconds
    
    if response['StatusCode'] != 200:
        raise Exception(f"Lambda invocation failed with status code: {response['StatusCode']}")
    
    return latency, response

def run_query(query, warm_up=False):
    print(f"Running query: {query[:50]}..." if len(query) > 50 else f"Running query: {query}")
    latency, response = invoke_lambda(query)
    print(f"Query completed. Latency: {latency:.2f} ms")
    if warm_up:
        print("Warm-up query completed")
        return latency
    return latency

def warm_up():
    print("Warming up the Lambda function...")
    for _ in range(WARM_UP_ITERATIONS):
        run_query(QUERY_SET['test'][0]['query'], warm_up=True)
    print("Warm-up complete.")

def run_benchmarks():
    results = []

    warm_up()

    for test in QUERY_SET['test']:
        query = test['query']
        iterations = test['iterations'] * ITERATIONS  # Multiply by ITERATIONS to ensure each query runs at least 10 times
        print(f"Running benchmark for query ID {test['id']}: {query}")
        query_results = []

        query_results = []
        for _ in range(iterations):
            latency = run_query(query)
            query_results.append(latency)

        latencies = query_results

        results.append({
            "id": test['id'],
            "query": query,
            "latency_p50": statistics.median(latencies),
            "latency_max": max(latencies)
        })

    return results

if __name__ == "__main__":
    benchmark_results = run_benchmarks()

    # Write results to CSV
    csv_filename = 'benchmark_results.csv'
    with open(csv_filename, 'w', newline='') as csvfile:
        fieldnames = ['id', 'query', 'latency_p50', 'latency_max']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for result in benchmark_results:
            writer.writerow({
                'id': result['id'],
                'query': result['query'],
                'latency_p50': f"{result['latency_p50']:.2f}",
                'latency_max': f"{result['latency_max']:.2f}"
            })

    print(f"\nBenchmark results saved to {csv_filename}")

    # Print results to console
    print("\nBenchmark Results:")
    for result in benchmark_results:
        print(f"\nQuery ID: {result['id']}")
        print(f"Query: {result['query']}")
        print(f"Latency (ms) - P50: {result['latency_p50']:.2f}, Max: {result['latency_max']:.2f}")

    # Optionally, save full results to a JSON file
    with open('benchmark_results_full.json', 'w') as f:
        json.dump(benchmark_results, f, indent=2)
