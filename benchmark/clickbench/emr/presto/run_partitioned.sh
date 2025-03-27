#!/bin/bash

python3 -u benchmark.py /usr/bin/presto-cli queries_partitioned.sql 1 5 reports_partitioned.json