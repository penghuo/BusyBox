#!/usr/bin/env python3
"""
Benchmark Runner for OpenSearch Star-tree Optimization

This script benchmarks the performance of GROUP BY queries on both the original
hits index and the star-tree optimized index.

It collects timing data and saves results for later analysis.
"""

import argparse
import json
import requests
import time
import sys
import os
import statistics
from pathlib import Path
from datetime import datetime

# Default configuration
DEFAULT_OPENSEARCH_URL = "http://localhost:9200"
DEFAULT_ORIGINAL_INDEX = "hits"
DEFAULT_OPTIMIZED_INDEX = "hits_startree"
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "admin"
DEFAULT_ITERATIONS = 5
DEFAULT_WARMUP_ITERATIONS = 2
DEFAULT_OUTPUT_FILE = "benchmark_results.json"
DEFAULT_DISABLE_CACHE = True
DEFAULT_CLEAR_CACHE_BETWEEN_RUNS = False

class BenchmarkRunner:
    """Runs performance benchmarks on OpenSearch indexes."""
    
    def __init__(self, opensearch_url, original_index, optimized_index, 
                 username, password, iterations, warmup_iterations, output_file,
                 disable_cache=DEFAULT_DISABLE_CACHE, 
                 clear_cache_between_runs=DEFAULT_CLEAR_CACHE_BETWEEN_RUNS):
        """Initialize the benchmark runner with connection parameters."""
        self.opensearch_url = opensearch_url
        self.original_index = original_index
        self.optimized_index = optimized_index
        self.iterations = iterations
        self.warmup_iterations = warmup_iterations
        self.output_file = output_file
        self.disable_cache = disable_cache
        self.clear_cache_between_runs = clear_cache_between_runs
        
        self.auth = (username, password)
        self.session = requests.Session()
        self.session.auth = self.auth
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Define benchmark queries
        self.benchmark_queries = {
            "group_by_user_search": {
                "description": "GROUP BY UserID, SearchPhrase ORDER BY COUNT(*) DESC LIMIT 10",
                "query": {
                    "size": 0,
                    "aggs": {
                        "user_search_groups": {
                            "composite": {
                                "size": 10,
                                "sources": [
                                    {
                                        "user_id": {
                                            "terms": {
                                                "field": "UserID"
                                            }
                                        }
                                    },
                                    {
                                        "search_phrase": {
                                            "terms": {
                                                "field": "SearchPhrase"
                                            }
                                        }
                                    }
                                ]
                            }
                        }
                    }
                }
            }
        }
        
        # Results storage
        self.results = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "opensearch_url": opensearch_url,
                "original_index": original_index,
                "optimized_index": optimized_index,
                "iterations": iterations,
                "warmup_iterations": warmup_iterations,
                "cache_disabled": disable_cache,
                "clear_cache_between_runs": clear_cache_between_runs
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
    
    def clear_cache(self):
        """Clear OpenSearch request cache."""
        print("Clearing OpenSearch request cache...", end="", flush=True)
        try:
            url = f"{self.opensearch_url}/_cache/clear?request=true"
            response = self.session.post(url)
            if response.status_code in [200, 201]:
                print(" ✓ Cache cleared successfully")
                return True
            else:
                print(f" ✗ Failed to clear cache: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except Exception as e:
            print(f" ✗ Error clearing cache: {e}")
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
    
    def run_query(self, index_name, query_name, query_body, is_warmup=False):
        """Run a single query and measure execution time."""
        cache_param = "false" if self.disable_cache else "true"
        url = f"{self.opensearch_url}/{index_name}/_search?request_cache={cache_param}"
        
        prefix = "Warmup" if is_warmup else "Benchmark"
        print(f"{prefix} query '{query_name}' on index '{index_name}'...", end="", flush=True)
        
        try:
            # Add profile parameter to get detailed execution info
            query_body["profile"] = True
            
            start_time = time.time()
            response = self.session.post(url, json=query_body, timeout=120)
            end_time = time.time()
            
            execution_time = end_time - start_time
            
            if response.status_code in [200, 201]:
                result = response.json()
                
                # Extract profiling data
                profile_data = result.get('profile', {})
                
                # Extract aggregation results
                aggs_result = result.get('aggregations', {})
                
                # Get hit count
                hit_count = result.get('hits', {}).get('total', {}).get('value', 0)
                
                print(f" completed in {execution_time:.4f} seconds")
                
                if not is_warmup:
                    return {
                        "execution_time": execution_time,
                        "status_code": response.status_code,
                        "hit_count": hit_count,
                        "profile": profile_data
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
                self.run_query(index_name, query_name, query_body, is_warmup=True)
            
            # Benchmark runs
            print(f"Performing {self.iterations} benchmark iterations...")
            iteration_times = []
            
            for i in range(self.iterations):
                # Clear cache between runs if configured
                if self.clear_cache_between_runs and not self.disable_cache:
                    self.clear_cache()
                
                result = self.run_query(index_name, query_name, query_body)
                if result:
                    iteration_times.append(result["execution_time"])
                    
                    # Store full result for the first iteration
                    if i == 0:
                        query_results[f"{index_name}_first_result"] = result
                    
                    # Store iteration result
                    index_key = "original_index" if index_name == self.original_index else "optimized_index"
                    query_results[index_key]["iterations"].append(result)
            
            # Calculate statistics
            if iteration_times:
                avg_time = statistics.mean(iteration_times)
                min_time = min(iteration_times)
                max_time = max(iteration_times)
                median_time = statistics.median(iteration_times)
                stdev_time = statistics.stdev(iteration_times) if len(iteration_times) > 1 else 0
                
                index_key = "original_index" if index_name == self.original_index else "optimized_index"
                query_results[index_key]["stats"] = {
                    "avg_time": avg_time,
                    "min_time": min_time,
                    "max_time": max_time,
                    "median_time": median_time,
                    "stdev_time": stdev_time
                }
                
                print(f"Results for {index_name}:")
                print(f"  Average time: {avg_time:.4f} seconds")
                print(f"  Min time: {min_time:.4f} seconds")
                print(f"  Max time: {max_time:.4f} seconds")
                print(f"  Median time: {median_time:.4f} seconds")
                print(f"  Standard deviation: {stdev_time:.4f} seconds")
        
        # Calculate improvement
        if ("original_index" in query_results and 
            "optimized_index" in query_results and
            "stats" in query_results["original_index"] and
            "stats" in query_results["optimized_index"]):
            
            orig_avg = query_results["original_index"]["stats"]["avg_time"]
            opt_avg = query_results["optimized_index"]["stats"]["avg_time"]
            
            if orig_avg > 0:
                improvement = ((orig_avg - opt_avg) / orig_avg) * 100
                speedup = orig_avg / opt_avg if opt_avg > 0 else float('inf')
                
                query_results["improvement"] = {
                    "percentage": improvement,
                    "speedup": speedup
                }
                
                print(f"\nPerformance improvement:")
                print(f"  Original avg time: {orig_avg:.4f} seconds")
                print(f"  Optimized avg time: {opt_avg:.4f} seconds")
                print(f"  Improvement: {improvement:.2f}%")
                print(f"  Speedup: {speedup:.2f}x")
        
        return query_results
    
    def run_all_benchmarks(self):
        """Run all benchmark queries."""
        if not self.check_connection():
            return False
        
        if not self.check_indexes():
            return False
        
        print("\nStarting benchmark runs...")
        
        for query_name, query_config in self.benchmark_queries.items():
            query_results = self.run_benchmark_query(query_name, query_config)
            self.results["queries"][query_name] = query_results
        
        # Calculate overall summary
        self.calculate_summary()
        
        # Save results
        self.save_results()
        
        return True
    
    def calculate_summary(self):
        """Calculate overall summary statistics."""
        print("\nCalculating overall summary...")
        
        improvements = []
        speedups = []
        
        for query_name, query_results in self.results["queries"].items():
            if "improvement" in query_results:
                improvements.append(query_results["improvement"]["percentage"])
                speedups.append(query_results["improvement"]["speedup"])
        
        if improvements and speedups:
            avg_improvement = statistics.mean(improvements)
            avg_speedup = statistics.mean(speedups)
            
            self.results["summary"] = {
                "avg_improvement_percentage": avg_improvement,
                "avg_speedup": avg_speedup,
                "query_count": len(improvements)
            }
            
            print(f"Average improvement: {avg_improvement:.2f}%")
            print(f"Average speedup: {avg_speedup:.2f}x")
            print(f"Queries benchmarked: {len(improvements)}")
    
    def save_results(self):
        """Save benchmark results to file."""
        print(f"\nSaving results to {self.output_file}...")
        
        try:
            with open(self.output_file, 'w') as f:
                json.dump(self.results, f, indent=2)
            print(f"✓ Results saved successfully")
            return True
        except Exception as e:
            print(f"✗ Failed to save results: {e}")
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
    parser.add_argument('--warmup', type=int, default=DEFAULT_WARMUP_ITERATIONS,
                       help=f'Number of warmup iterations (default: {DEFAULT_WARMUP_ITERATIONS})')
    parser.add_argument('--output', default=DEFAULT_OUTPUT_FILE,
                       help=f'Output file for results (default: {DEFAULT_OUTPUT_FILE})')
    parser.add_argument('--disable-cache', dest='disable_cache', action='store_true',
                       help='Disable OpenSearch query request cache (default: True)')
    parser.add_argument('--enable-cache', dest='disable_cache', action='store_false',
                       help='Enable OpenSearch query request cache')
    parser.add_argument('--clear-cache-between-runs', dest='clear_cache_between_runs', action='store_true',
                       help='Clear cache between benchmark iterations (default: False)')
    parser.set_defaults(disable_cache=DEFAULT_DISABLE_CACHE)
    parser.set_defaults(clear_cache_between_runs=DEFAULT_CLEAR_CACHE_BETWEEN_RUNS)
    
    args = parser.parse_args()
    
    runner = BenchmarkRunner(
        opensearch_url=args.url,
        original_index=args.original,
        optimized_index=args.optimized,
        username=args.username,
        password=args.password,
        iterations=args.iterations,
        warmup_iterations=args.warmup,
        output_file=args.output,
        disable_cache=args.disable_cache,
        clear_cache_between_runs=args.clear_cache_between_runs
    )
    
    success = runner.run_all_benchmarks()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
