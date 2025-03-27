#!/bin/bash

spark-submit --conf spark.dynamicAllocation.enabled=false --conf spark.sql.dataprefetch.filescan.checkInstanceType=false benchmark.py --queries queries_partitioned.sql --iterations 5 --warmup-runs 1 --output /home/ec2-user/benchmark/clickbench/emr/spark/reports_partitioned.json