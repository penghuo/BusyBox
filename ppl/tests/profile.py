import requests
import time
import statistics
import matplotlib.pyplot as plt
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed

url = "http://localhost:9200/_plugins/_ppl/"
headers = {
    "Content-Type": "application/x-ndjson",
    "User-Agent": "vscode-restclient"
}
payload = '{"query": "describe test*"}'

# Configuration
concurrency_levels = [1, 2, 4, 8, 16, 32, 64]  # Thread counts to test
requests_per_level = 100  # Total requests per concurrency level
warmup_requests = 10  # Warmup requests before collecting metrics

def run_query():
    start = time.perf_counter()
    response = requests.post(url, headers=headers, data=payload)
    end = time.perf_counter()
    latency = (end - start) * 1000  # in milliseconds
    return latency, response.status_code

def test_concurrency(concurrent_requests):
    print(f"\nTesting with {concurrent_requests} concurrent threads")
    
    # Run warmup requests
    print(f"Running {warmup_requests} warmup requests...")
    with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
        list(executor.map(lambda _: run_query(), range(warmup_requests)))
    
    latencies = []
    successful_requests = 0
    failed_requests = 0
    
    # Run actual test
    print(f"Running {requests_per_level} test requests...")
    start_time = time.perf_counter()
    
    with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
        futures = [executor.submit(run_query) for _ in range(requests_per_level)]
        
        for i, future in enumerate(as_completed(futures)):
            latency, status = future.result()
            latencies.append(latency)
            
            if status == 200:
                successful_requests += 1
            else:
                failed_requests += 1
                
            if (i+1) % 20 == 0:
                print(f"Progress: {i+1}/{requests_per_level} requests completed")
    
    end_time = time.perf_counter()
    total_duration = end_time - start_time
    
    # Calculate statistics
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    median_latency = statistics.median(latencies) if latencies else 0
    p95_latency = np.percentile(latencies, 95) if latencies else 0
    p99_latency = np.percentile(latencies, 99) if latencies else 0
    min_latency = min(latencies) if latencies else 0
    max_latency = max(latencies) if latencies else 0
    rps = len(latencies) / total_duration
    
    print(f"\nCompleted {len(latencies)} requests in {total_duration:.2f} seconds")
    print(f"Requests per second: {rps:.2f}")
    print(f"Successful requests: {successful_requests}, Failed requests: {failed_requests}")
    print(f"Latency (ms): Avg: {avg_latency:.2f}, Median: {median_latency:.2f}")
    print(f"Min: {min_latency:.2f}, Max: {max_latency:.2f}")
    print(f"p95: {p95_latency:.2f}, p99: {p99_latency:.2f}")
    
    return {
        "concurrency": concurrent_requests,
        "avg_latency": avg_latency,
        "median_latency": median_latency,
        "p95_latency": p95_latency,
        "p99_latency": p99_latency,
        "min_latency": min_latency,
        "max_latency": max_latency,
        "rps": rps
    }

def plot_results(results, filename_base="pressure_test_results"):
    plt.figure(figsize=(10, 6))
    
    # Extract data for plotting
    concurrency = [r["concurrency"] for r in results]
    avg_latency = [r["avg_latency"] for r in results]
    p95_latency = [r["p95_latency"] for r in results]
    p99_latency = [r["p99_latency"] for r in results]
    
    # Create plot
    plt.plot(concurrency, avg_latency, 'o-', label='Average Latency')
    plt.plot(concurrency, p95_latency, 's--', label='p95 Latency')
    plt.plot(concurrency, p99_latency, '^:', label='p99 Latency')
    
    # Set x-axis to use logarithmic scale but show actual values
    plt.xscale('log', base=2)
    plt.xticks(concurrency, [str(c) for c in concurrency])
    
    plt.xlabel('Concurrency Level (threads)')
    plt.ylabel('Latency (ms)')
    plt.title('Latency vs Concurrency')
    plt.grid(True)
    plt.legend()
    
    plt.tight_layout()
    
    # Save in multiple formats
    plt.savefig(f'{filename_base}.png', dpi=300)
    plt.savefig(f'{filename_base}.pdf')
    
    print(f"\nResults saved as '{filename_base}.png' and '{filename_base}.pdf'")

def main():
    results = []
    
    try:
        print(f"Starting pressure test with concurrency levels: {concurrency_levels}")
        for concurrency in concurrency_levels:
            result = test_concurrency(concurrency)
            results.append(result)
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
    except Exception as e:
        print(f"Error during testing: {str(e)}")
    
    # Plot results if we have data
    if results:
        plot_results(results)

if __name__ == "__main__":
    main()