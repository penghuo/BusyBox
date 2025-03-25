#!/usr/bin/env python3

import argparse
import json
import time
import numpy as np
from datetime import datetime
from pyspark.sql import SparkSession

def init_spark(log_level="WARN"):
    """Initialize Spark once with dynamic allocation disabled"""
    spark = (SparkSession.builder
             .appName("QueryBenchmark")
             .enableHiveSupport()
             .config("spark.dynamicAllocation.enabled", "false")
             .config("spark.sql.dataprefetch.filescan.checkInstanceType", "false")
             .getOrCreate())
    spark.sparkContext.setLogLevel(log_level)
    return spark

def execute_phase(spark, query, phase, runs):
    """Generic phase executor"""
    timings = []
    for i in range(runs):
        try:
            start = time.perf_counter()
            spark.sql(query).show()  # Original execution method
            elapsed = time.perf_counter() - start
            timings.append(elapsed)
            print(f"  {phase} run {i+1}/{runs}: {elapsed:.2f}s")
        except Exception as e:
            print(f"  {phase} failed: {str(e)}")
            return None
    return timings

def benchmark_query(spark, query, query_id, args):
    """Benchmark single query using existing context"""
    print(f"\nProcessing {query_id}: {query[:80]}...")
    
    result = {
        "query_id": query_id,
        "query": query,
        "test_runs": args.iterations,
        "timings": [],
        "error": None
    }
    
    try:
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
    
    return result

def main():
    """Main flow with single context initialization"""
    parser = argparse.ArgumentParser(description="Spark Query Benchmark")
    parser.add_argument("--queries", required=True)
    parser.add_argument("--iterations", type=int, default=3)
    parser.add_argument("--warmup-runs", type=int, default=1)
    parser.add_argument("--output", required=True)
    parser.add_argument("--log-level", default="WARN")
    args = parser.parse_args()

    # Initialize Spark once
    spark = init_spark(args.log_level)
    
    try:
        # Single warmup run for all queries
        if args.warmup_runs > 0:
            print("Running global warmup...")
            execute_phase(spark, 
                "SELECT EventTime FROM sparkhits LIMIT 1", 
                "Global Warmup", 
                args.warmup_runs
            )

        # Process all queries with same context
        with open(args.queries) as f:
            queries = [q.strip() for q in f if q.strip() and not q.startswith("--")]
        
        results = []
        for idx, query in enumerate(queries, 1):
            result = benchmark_query(spark, query, f"Q{idx}", args)
            results.append(result)
            
            if result["error"]:
                print(f"  Q{idx} failed: {result['error']}")
            else:
                print(f"  Q{idx} summary: {result['avg_time']:.2f}s avg")

        # Generate report
        report = {
            "timestamp": datetime.now().isoformat(),
            "config": vars(args),
            "results": results
        }

        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)

    finally:
        spark.stop()

if __name__ == "__main__":
    main()