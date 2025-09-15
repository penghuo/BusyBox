#!/usr/bin/env python3
"""
Benchmark Runner for OpenSearch Star-tree Optimization

This script benchmarks the performance of GROUP BY queries on both the original
hits index and the star-tree optimized index.

It loads queries from JSON files, runs benchmarks, and collects timing data
including p90 and max latency metrics.
"""

import argparse
import json
import requests
import time
import sys
import os
import statistics
import glob
import csv
from pathlib import Path
from datetime import datetime

# Default configuration
DEFAULT_OPENSEARCH_URL = "http://localhost:9200"
DEFAULT_ORIGINAL_INDEX = "hits"
DEFAULT_OPTIMIZED_INDEX = "hits_startree"
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "admin"
DEFAULT_ITERATIONS = 10  # Changed from 5 to 10
DEFAULT_WARMUP_ITERATIONS = 2  # Fixed at 2
DEFAULT_OUTPUT_FILE = "benchmark_results.json"
DEFAULT_CSV_OUTPUT_FILE = "benchmark_results.csv"
DEFAULT_DISABLE_CACHE = False  # Changed to enable cache by default
DEFAULT_CLEAR_CACHE_BETWEEN_RUNS = True  # Changed to clear cache between runs by default

class BenchmarkRunner:
    """Runs performance benchmarks on OpenSearch indexes."""
    
    def __init__(self, opensearch_url, original_index, optimized_index, 
                 username, password, iterations, output_file, csv_output_file,
                 disable_cache=DEFAULT_DISABLE_CACHE):
        """Initialize the benchmark runner with connection parameters."""
        self.opensearch_url = opensearch_url
        self.original_index = original_index
        self.optimized_index = optimized_index
        self.iterations = iterations
        self.warmup_iterations = DEFAULT_WARMUP_ITERATIONS  # Fixed at 2
        self.output_file = output_file
        self.csv_output_file = csv_output_file
        self.disable_cache = disable_cache
        
        self.auth = (username, password)
        self.session = requests.Session()
        self.session.auth = self.auth
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Results storage
        self.results = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "opensearch_url": opensearch_url,
                "original_index": original_index,
                "optimized_index": optimized_index,
                "iterations": iterations,
                "warmup_iterations": self.warmup_iterations,
                "cache_disabled": disable_cache
            },
            "queries": {},
            "summary": {}
        }
    
    def check_connection(self):
        """Check if OpenSearch is accessible."""
        print(f"Checking connection to OpenSearch at {self.opensearch_url}...")
        try:
            response = self.session.get(self.opensearch_url, timeout=10)
            if response.status_code in [200, 201]:
                cluster_info = response.json()
                print(f"✓ Connected to OpenSearch cluster: {cluster_info.get('cluster_name', 'unknown')}")
                print(f"✓ Version: {cluster_info.get('version', {}).get('number', 'unknown')}")
                return True
            else:
                print(f"✗ OpenSearch returned status code: {response.status_code}")
                print(f"✗ Response: {response.text}")
                return False
        except Exception as e:
            print(f"✗ Failed to connect to OpenSearch: {e}")
            return False
    
    def clear_index_cache(self, index_name):
        """Clear cache for a specific index."""
        print(f"Clearing cache for index {index_name}...", end="", flush=True)
        try:
            url = f"{self.opensearch_url}/{index_name}/_cache/clear?request=true"
            response = self.session.post(url)
            if response.status_code in [200, 201]:
                print(" ✓")
                return True
            else:
                print(f" ✗ Failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except Exception as e:
            print(f" ✗ Error: {e}")
            return False
    
    def check_indexes(self):
        """Check if both indexes exist."""
        print("Checking indexes...")
        
        indexes_to_check = [self.original_index, self.optimized_index]
        all_exist = True
        
        for index_name in indexes_to_check:
            try:
                response = self.session.get(f"{self.opensearch_url}/{index_name}")
                if response.status_code == 200:
                    # Get document count
                    count_resp = self.session.get(f"{self.opensearch_url}/{index_name}/_count")
                    if count_resp.status_code == 200:
                        count = count_resp.json().get('count', 0)
                        print(f"✓ Index '{index_name}' exists with {count:,} documents")
                    else:
                        print(f"✓ Index '{index_name}' exists but couldn't get document count")
                else:
                    print(f"✗ Index '{index_name}' does not exist")
                    all_exist = False
            except Exception as e:
                print(f"✗ Error checking index '{index_name}': {e}")
                all_exist = False
        
        return all_exist
    
    def load_query_files(self):
        """Load Q15-Q17 query files (Q18 is ignored)."""
        query_files = [
            "Q15_group_by_userid.json",
            "Q16_group_by_userid_searchphrase_ordered.json",
            "Q17_group_by_userid_searchphrase.json"
            # Q18 is ignored as requested
        ]
        
        queries = {}
        
        for file_name in query_files:
            try:
                with open(file_name, 'r') as f:
                    query_data = json.load(f)
                    query_id = file_name.split('_')[0]  # Extract Q15, Q16, etc.
                    queries[query_id] = query_data
                    print(f"✓ Loaded query from {file_name}")
            except Exception as e:
                print(f"✗ Failed to load query from {file_name}: {e}")
        
        return queries
    
    def run_query(self, index_name, query_name, query_body, is_warmup=False):
        """Run a single query and measure execution time."""
        cache_param = "false" if self.disable_cache else "true"
        url = f"{self.opensearch_url}/{index_name}/_search?request_cache={cache_param}"
        
        prefix = "Warmup" if is_warmup else "Benchmark"
        print(f"{prefix} query '{query_name}' on index '{index_name}'...", end="", flush=True)
        
        try:
            # Execute the query without profiling
            start_time = time.time()
            response = self.session.post(url, json=query_body, timeout=120)
            end_time = time.time()
            
            execution_time = end_time - start_time
            
            if response.status_code in [200, 201]:
                result = response.json()
                
                # Extract aggregation results
                aggs_result = result.get('aggregations', {})
                
                # Get hit count
                hit_count = result.get('hits', {}).get('total', {}).get('value', 0)
                
                print(f" completed in {execution_time:.4f} seconds")
                
                if not is_warmup:
                    return {
                        "execution_time": execution_time,
                        "status_code": response.status_code,
                        "hit_count": hit_count
                    }
                else:
                    return None
            else:
                print(f" failed with status code {response.status_code}")
                print(f"Response: {response.text}")
                return None
        except Exception as e:
            print(f" failed with error: {e}")
            return None
    
    def run_benchmark_query(self, query_name, query_config):
        """Run benchmark for a specific query on both indexes."""
        print(f"\nRunning benchmark for query: {query_name}")
        print(f"Description: {query_config['description']}")
        print("-" * 80)
        
        query_body = query_config['query']
        query_results = {
            "description": query_config['description'],
            "original_index": {
                "iterations": []
            },
            "optimized_index": {
                "iterations": []
            }
        }
        
        # Run on both indexes
        for index_name in [self.original_index, self.optimized_index]:
            print(f"\nBenchmarking index: {index_name}")
            
            # Warmup runs
            print(f"Performing {self.warmup_iterations} warmup iterations...")
            for i in range(self.warmup_iterations):
                # Clear cache before each warmup run
                self.clear_index_cache(index_name)
                self.run_query(index_name, query_name, query_body, is_warmup=True)
            
            # Benchmark runs
            print(f"Performing {self.iterations} benchmark iterations...")
            iteration_times = []
            
            for i in range(self.iterations):
                # Clear cache before each benchmark run
                self.clear_index_cache(index_name)
                
                result = self.run_query(index_name, query_name, query_body)
                if result:
                    iteration_times.append(result["execution_time"])
                    
                    # Store iteration result
                    index_key = "original_index" if index_name == self.original_index else "optimized_index"
                    query_results[index_key]["iterations"].append(result)
            
            # Calculate statistics
            if iteration_times:
                # Basic statistics
                avg_time = statistics.mean(iteration_times)
                min_time = min(iteration_times)
                max_time = max(iteration_times)
                median_time = statistics.median(iteration_times)
                stdev_time = statistics.stdev(iteration_times) if len(iteration_times) > 1 else 0
                
                # Calculate p90 (90th percentile) manually
                sorted_times = sorted(iteration_times)
                idx = int(len(sorted_times) * 0.9)
                if idx == len(sorted_times):
                    idx = len(sorted_times) - 1
                p90_time = sorted_times[idx]
                
                index_key = "original_index" if index_name == self.original_index else "optimized_index"
                query_results[index_key]["stats"] = {
                    "avg_time": avg_time,
                    "min_time": min_time,
                    "max_time": max_time,
                    "median_time": median_time,
                    "p90_time": p90_time,
                    "stdev_time": stdev_time
                }
                
                print(f"Results for {index_name}:")
                print(f"  Average time: {avg_time:.4f} seconds")
                print(f"  P90 time: {p90_time:.4f} seconds")
                print(f"  Max time: {max_time:.4f} seconds")
                print(f"  Median time: {median_time:.4f} seconds")
                print(f"  Min time: {min_time:.4f} seconds")
                print(f"  Standard deviation: {stdev_time:.4f} seconds")
        
        # Calculate improvement
        if ("original_index" in query_results and 
            "optimized_index" in query_results and
            "stats" in query_results["original_index"] and
            "stats" in query_results["optimized_index"]):
            
            orig_avg = query_results["original_index"]["stats"]["avg_time"]
            opt_avg = query_results["optimized_index"]["stats"]["avg_time"]
            
            orig_p90 = query_results["original_index"]["stats"]["p90_time"]
            opt_p90 = query_results["optimized_index"]["stats"]["p90_time"]
            
            orig_max = query_results["original_index"]["stats"]["max_time"]
            opt_max = query_results["optimized_index"]["stats"]["max_time"]
            
            if orig_avg > 0:
                avg_improvement = ((orig_avg - opt_avg) / orig_avg) * 100
                avg_speedup = orig_avg / opt_avg if opt_avg > 0 else float('inf')
                
                p90_improvement = ((orig_p90 - opt_p90) / orig_p90) * 100
                p90_speedup = orig_p90 / opt_p90 if opt_p90 > 0 else float('inf')
                
                max_improvement = ((orig_max - opt_max) / orig_max) * 100
                max_speedup = orig_max / opt_max if opt_max > 0 else float('inf')
                
                query_results["improvement"] = {
                    "avg_percentage": avg_improvement,
                    "avg_speedup": avg_speedup,
                    "p90_percentage": p90_improvement,
                    "p90_speedup": p90_speedup,
                    "max_percentage": max_improvement,
                    "max_speedup": max_speedup
                }
                
                print(f"\nPerformance improvement:")
                print(f"  Average: {avg_improvement:.2f}% ({avg_speedup:.2f}x speedup)")
                print(f"  P90: {p90_improvement:.2f}% ({p90_speedup:.2f}x speedup)")
                print(f"  Max: {max_improvement:.2f}% ({max_speedup:.2f}x speedup)")
        
        return query_results
    
    def run_all_benchmarks(self):
        """Run all benchmark queries."""
        if not self.check_connection():
            return False
        
        if not self.check_indexes():
            return False
        
        # Load queries from JSON files
        queries = self.load_query_files()
        if not queries:
            print("No query files found. Exiting.")
            return False
        
        print("\nStarting benchmark runs...")
        
        for query_id, query_config in queries.items():
            query_results = self.run_benchmark_query(query_id, query_config)
            self.results["queries"][query_id] = query_results
        
        # Calculate overall summary
        self.calculate_summary()
        
        # Save results
        self.save_results()
        
        return True
    
    def calculate_summary(self):
        """Calculate overall summary statistics."""
        print("\nCalculating overall summary...")
        
        avg_improvements = []
        avg_speedups = []
        p90_improvements = []
        p90_speedups = []
        max_improvements = []
        max_speedups = []
        
        for query_name, query_results in self.results["queries"].items():
            if "improvement" in query_results:
                avg_improvements.append(query_results["improvement"]["avg_percentage"])
                avg_speedups.append(query_results["improvement"]["avg_speedup"])
                p90_improvements.append(query_results["improvement"]["p90_percentage"])
                p90_speedups.append(query_results["improvement"]["p90_speedup"])
                max_improvements.append(query_results["improvement"]["max_percentage"])
                max_speedups.append(query_results["improvement"]["max_speedup"])
        
        if avg_improvements and avg_speedups:
            self.results["summary"] = {
                "avg_improvement": {
                    "percentage": statistics.mean(avg_improvements),
                    "speedup": statistics.mean(avg_speedups)
                },
                "p90_improvement": {
                    "percentage": statistics.mean(p90_improvements),
                    "speedup": statistics.mean(p90_speedups)
                },
                "max_improvement": {
                    "percentage": statistics.mean(max_improvements),
                    "speedup": statistics.mean(max_speedups)
                },
                "query_count": len(avg_improvements)
            }
            
            print(f"Average improvement across all queries:")
            print(f"  Average: {self.results['summary']['avg_improvement']['percentage']:.2f}% ({self.results['summary']['avg_improvement']['speedup']:.2f}x speedup)")
            print(f"  P90: {self.results['summary']['p90_improvement']['percentage']:.2f}% ({self.results['summary']['p90_improvement']['speedup']:.2f}x speedup)")
            print(f"  Max: {self.results['summary']['max_improvement']['percentage']:.2f}% ({self.results['summary']['max_improvement']['speedup']:.2f}x speedup)")
            print(f"  Queries benchmarked: {len(avg_improvements)}")
    
    def save_results(self):
        """Save benchmark results to file."""
        print(f"\nSaving results to {self.output_file}...")
        
        try:
            with open(self.output_file, 'w') as f:
                json.dump(self.results, f, indent=2)
            print(f"✓ Results saved successfully")
            
            # Generate CSV output
            self.save_csv_results()
            
            return True
        except Exception as e:
            print(f"✗ Failed to save results: {e}")
            return False
    
    def save_csv_results(self):
        """Save benchmark results in CSV format with specific columns."""
        print(f"\nSaving CSV results to {self.csv_output_file}...")
        
        try:
            with open(self.csv_output_file, 'w', newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                
                # Write header
                csvwriter.writerow(['Query', 'hits_P90_ms', 'hits_Max_ms', 'hits_startree_P90_ms', 'hits_startree_Max_ms'])
                
                # Write data for each query
                for query_name, query_results in self.results["queries"].items():
                    if ("original_index" in query_results and 
                        "optimized_index" in query_results and
                        "stats" in query_results["original_index"] and
                        "stats" in query_results["optimized_index"]):
                        
                        # Get original index stats (hits)
                        orig_p90 = query_results["original_index"]["stats"]["p90_time"] * 1000  # Convert to ms
                        orig_max = query_results["original_index"]["stats"]["max_time"] * 1000  # Convert to ms
                        
                        # Get optimized index stats (hits_startree)
                        opt_p90 = query_results["optimized_index"]["stats"]["p90_time"] * 1000  # Convert to ms
                        opt_max = query_results["optimized_index"]["stats"]["max_time"] * 1000  # Convert to ms
                        
                        # Format to 2 decimal places
                        csvwriter.writerow([
                            query_name,
                            f"{orig_p90:.2f}",
                            f"{orig_max:.2f}",
                            f"{opt_p90:.2f}",
                            f"{opt_max:.2f}"
                        ])
                
            print(f"✓ CSV results saved successfully")
            return True
        except Exception as e:
            print(f"✗ Failed to save CSV results: {e}")
            return False

def main():
    """Parse command line arguments and run the benchmark."""
    parser = argparse.ArgumentParser(
        description="Run performance benchmarks for OpenSearch star-tree optimization"
    )
    
    parser.add_argument('--url', default=DEFAULT_OPENSEARCH_URL,
                       help=f'OpenSearch URL (default: {DEFAULT_OPENSEARCH_URL})')
    parser.add_argument('--original', default=DEFAULT_ORIGINAL_INDEX,
                       help=f'Original index name (default: {DEFAULT_ORIGINAL_INDEX})')
    parser.add_argument('--optimized', default=DEFAULT_OPTIMIZED_INDEX,
                       help=f'Optimized index name (default: {DEFAULT_OPTIMIZED_INDEX})')
    parser.add_argument('--username', default=DEFAULT_USERNAME,
                       help=f'OpenSearch username (default: {DEFAULT_USERNAME})')
    parser.add_argument('--password', default=DEFAULT_PASSWORD,
                       help=f'OpenSearch password (default: {DEFAULT_PASSWORD})')
    parser.add_argument('--iterations', type=int, default=DEFAULT_ITERATIONS,
                       help=f'Number of benchmark iterations (default: {DEFAULT_ITERATIONS})')
    parser.add_argument('--output', default=DEFAULT_OUTPUT_FILE,
                       help=f'Output file for results (default: {DEFAULT_OUTPUT_FILE})')
    parser.add_argument('--csv-output', default=DEFAULT_CSV_OUTPUT_FILE,
                       help=f'CSV output file for results (default: {DEFAULT_CSV_OUTPUT_FILE})')
    parser.add_argument('--disable-cache', dest='disable_cache', action='store_true',
                       help='Disable OpenSearch query request cache (default: False)')
    parser.add_argument('--enable-cache', dest='disable_cache', action='store_false',
                       help='Enable OpenSearch query request cache (default: True)')
    parser.set_defaults(disable_cache=DEFAULT_DISABLE_CACHE)
    
    args = parser.parse_args()
    
    runner = BenchmarkRunner(
        opensearch_url=args.url,
        original_index=args.original,
        optimized_index=args.optimized,
        username=args.username,
        password=args.password,
        iterations=args.iterations,
        output_file=args.output,
        csv_output_file=args.csv_output,
        disable_cache=args.disable_cache
    )
    
    success = runner.run_all_benchmarks()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
