import subprocess
import time
import json
import re
import sys
import numpy as np
from datetime import datetime

def parse_queries(query_file):
    """Parse SQL queries from file using semicolon as delimiter"""
    with open(query_file, 'r') as f:
        content = f.read()
    return [q.strip() for q in re.split(r';\s*\n', content) if q.strip()]

def execute_presto_query(presto_cli_path, query, catalog, schema, iterations, warmup_runs):
    """Execute query with warmup runs and collect timings"""
    # Warmup executions (not recorded)
    for _ in range(warmup_runs):
        subprocess.run([
            presto_cli_path,
            "--catalog", catalog,
            "--schema", schema,
            "--execute", query,
            "--output-format", "CSV_HEADER"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Actual measurement
    timings = []
    for _ in range(iterations):
        start = time.perf_counter()
        result = subprocess.run([
            presto_cli_path,
            "--catalog", catalog,
            "--schema", schema,
            "--execute", query,
            "--output-format", "CSV_HEADER"
        ], capture_output=True, text=True)
        latency = time.perf_counter() - start
        
        if result.returncode != 0:
            return {"error": result.stderr}
        
        timings.append(latency)
    
    return {
        "timings": timings,
        "avg_time": np.mean(timings),
        "p75_time": np.percentile(timings, 75),
        "min_time": np.min(timings),
        "max_time": np.max(timings)
    }

def main():
    if len(sys.argv) != 6:
        print("Usage: python presto_benchmark.py <presto-cli-path> <query-file> <warmup-runs> <iterations> <output-json>")
        sys.exit(1)
    
    presto_cli_path = sys.argv[1]
    query_file = sys.argv[2]
    warmup_runs = int(sys.argv[3])
    iterations = int(sys.argv[4])
    output_json = sys.argv[5]
    
    queries = parse_queries(query_file)
    results = []
    
    for idx, query in enumerate(queries, 1):
        query_id = f"Q{idx}"
        print(f"Executing {query_id} ({idx}/{len(queries)})")
        
        try:
            result = execute_presto_query(
                presto_cli_path,
                query,
                "awsdatacatalog",
                "default",
                iterations,
                warmup_runs
            )
            
            if "error" in result:
                query_result = {
                    "query_id": query_id,
                    "query": query,
                    "error": result["error"]
                }
            else:
                query_result = {
                    "query_id": query_id,
                    "query": query,
                    "iterations": iterations,
                    "avg_time": result["avg_time"],
                    "p75_time": result["p75_time"],
                    "min_time": result["min_time"],
                    "max_time": result["max_time"],
                    "individual_times": result["timings"]
                }
            
            results.append(query_result)
            print(f"  Avg: {result['avg_time']:.2f}s | Min: {result['min_time']:.2f}s | Max: {result['max_time']:.2f}s")
        
        except Exception as e:
            results.append({
                "query_id": query_id,
                "query": query,
                "error": str(e)
            })
            print(f"  Failed: {str(e)}")
    
    # Generate final report
    report = {
        "timestamp": datetime.now().isoformat(),
        "results": results
    }
    
    with open(output_json, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nReport saved to {output_json}")

if __name__ == "__main__":
    main()