#!/usr/bin/env python3

import argparse
import json
import os
import time
import numpy as np
from datetime import datetime
from pyspark.sql import SparkSession

def init_spark(log_level="WARN", query_id="#"):
    """Initialize and return a new Spark session with Glue integration"""
    spark = (SparkSession.builder
             .appName(f"QueryBenchmark-{query_id}")
             .enableHiveSupport()
             .getOrCreate())
    
    spark.sparkContext.setLogLevel(log_level)
    return spark

def execute_phase(spark, query, phase, runs):
    """Execute a phase (warmup or test) and return timings"""
    timings = []
    for i in range(runs):
        try:
            start = time.perf_counter()
            spark.sql(query).show()  # Force execution
            elapsed = time.perf_counter() - start
            timings.append(elapsed)
            print(f"  {phase} run {i+1}/{runs}: {elapsed:.2f}s")
        except Exception as e:
            print(f"  {phase} failed: {str(e)}")
            return None
    return timings

def benchmark_query(query, query_id, args):
    """Benchmark a single query with isolated Spark context"""
    print(f"\nProcessing {query_id}: {query[:80]}...")
    
    result = {
        "query_id": query_id,
        "query": query,
        "warmup_runs": args.warmup_runs,
        "test_runs": args.iterations,
        "timings": [],
        "error": None
    }
    
    try:
        # Initialize fresh Spark context for each query
        spark = init_spark(args.log_level, query_id)
        
        # Warmup phase
        if args.warmup_runs > 0:
            warmup_timings = execute_phase(spark, "SELECT EventTime FROM sparkhits LIMIT 1", "Warmup", args.warmup_runs)
            if warmup_timings is None:
                result["error"] = "Warmup phase failed"
                return result
        
        # Test phase
        test_timings = execute_phase(spark, query, "Test", args.iterations)
        if test_timings:
            result.update({
                "avg_time": np.mean(test_timings),
                "p75_time": np.percentile(test_timings, 75),
                "min_time": np.min(test_timings),
                "max_time": np.max(test_timings),
                "individual_times": test_timings
            })
        
    except Exception as e:
        result["error"] = str(e)
    finally:
        spark.stop()
    
    return result

def main():
    """Main execution flow"""
    parser = argparse.ArgumentParser(description="Isolated Spark Query Benchmark")
    parser.add_argument("--queries", required=True, help="Path to SQL query file")
    parser.add_argument("--iterations", type=int, default=3, help="Test iterations per query")
    parser.add_argument("--warmup-runs", type=int, default=2, help="Warmup iterations per query")
    parser.add_argument("--output", required=True, help="Output JSON file path")
    parser.add_argument("--log-level", default="WARN", help="Spark log level")
    args = parser.parse_args()

    # Read queries
    with open(args.queries) as f:
        queries = [q.strip() for q in f if q.strip() and not q.startswith("--")]
    
    results = []
    
    # Benchmark each query in isolation
    for idx, query in enumerate(queries, 1):
        qid = f"Q{idx}"
        result = benchmark_query(query, qid, args)
        results.append(result)
        
        if result["error"]:
            print(f"  {qid} failed: {result['error']}")
        else:
            print(f"  {qid} summary:")
            print(f"    Avg: {result['avg_time']:.2f}s")
            print(f"    P75: {result['p75_time']:.2f}s")
            print(f"    Range: {result['min_time']:.2f}s - {result['max_time']:.2f}s")

    # Generate report
    report = {
        "timestamp": datetime.now().isoformat(),
        "config": {
            "warmup_runs": args.warmup_runs,
            "test_iterations": args.iterations,
            "log_level": args.log_level
        },
        "results": results
    }

    with open(args.output, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\nBenchmark complete. Report saved to {args.output}")

if __name__ == "__main__":
    main()