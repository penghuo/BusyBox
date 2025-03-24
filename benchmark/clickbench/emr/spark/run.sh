#!/bin/bash

spark-submit --conf spark.dynamicAllocation.enabled=false benchmark.py --queries queries.sql --iterations 5 --warmup-runs 1 --output /home/ec2-user/benchmark/clickbench/emr/spark/reports.json