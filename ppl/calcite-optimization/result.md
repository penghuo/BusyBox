# Calcite Optimization Test Results

This document compares query performance with Calcite optimization enabled vs. disabled.

## Query 1: `source=testindex | where v=1`

| Metric | Calcite Disabled | Calcite Enabled |
|--------|-----------------|----------------|
| **Total Latency** | 4.95 ms | 8.60 ms |
| **Breakdown** | | |
| Parse | 0.10 ms | 0.09 ms |
| AST | 0.04 ms | 0.04 ms |
| Analyze | 0.32 ms | 0.50 ms |
| Optimize | 0.61 ms | 0.00 ms |
| Convert | - | 0.00 ms |
| Prepare Execution | 0.35 ms | 3.30 ms |
| Execute | 1.41 ms | 1.35 ms |
| Build Result | 0.08 ms | 0.71 ms |

## Query 2: `source=testindex | stats count()`

| Metric | Calcite Disabled | Calcite Enabled |
|--------|-----------------|----------------|
| **Total Latency** | 3.34 ms | 7.47 ms |
| **Breakdown** | | |
| Parse | 0.07 ms | 0.06 ms |
| AST | 0.05 ms | 0.05 ms |
| Analyze | 0.33 ms | 0.50 ms |
| Optimize | 0.10 ms | 0.00 ms |
| Convert | - | 0.00 ms |
| Prepare Execution | 0.10 ms | 2.21 ms |
| Execute | 0.63 ms | 1.90 ms |
| Build Result | 0.04 ms | 0.19 ms |

## Query 3: `source=testindex | where v=1 | stats count()`

| Metric | Calcite Disabled | Calcite Enabled |
|--------|-----------------|----------------|
| **Total Latency** | 3.38 ms | 7.14 ms |
| **Breakdown** | | |
| Parse | 0.07 ms | 0.09 ms |
| AST | 0.05 ms | 0.05 ms |
| Analyze | 0.33 ms | 0.51 ms |
| Optimize | 0.21 ms | 0.00 ms |
| Convert | - | 0.00 ms |
| Prepare Execution | 0.07 ms | 3.17 ms |
| Execute | 0.66 ms | 0.98 ms |
| Build Result | 0.05 ms | 0.15 ms |

## Summary

Overall, enabling Calcite optimization increased the total latency across all tested queries:
- Query 1: +3.65 ms (+74%)
- Query 2: +4.13 ms (+124%)
- Query 3: +3.76 ms (+111%)

The most significant increase in latency was observed in the "Prepare Execution" phase:
- Query 1: +2.95 ms
- Query 2: +2.11 ms
- Query 3: +3.10 ms

While some phases showed minor performance improvements with Calcite enabled (like Optimize phase), these were not sufficient to offset the increased preparation time.
