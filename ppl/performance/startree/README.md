# OpenSearch Star-tree Optimization for ClickBench

This project optimizes the ClickBench hits index using OpenSearch's star-tree feature to accelerate GROUP BY queries. It includes tools for creating optimized indexes, running benchmarks, and generating performance reports.

## Overview

Star-tree indexes in OpenSearch precompute aggregations, significantly improving the performance of GROUP BY queries. This project focuses on optimizing the following query:

```sql
SELECT UserID, SearchPhrase, COUNT(*) FROM hits GROUP BY UserID, SearchPhrase ORDER BY COUNT(*) DESC LIMIT 10;
```

The equivalent OpenSearch DSL query is:

```json
{
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
```

## Prerequisites

- OpenSearch 3.2.0 or higher
- Python 3.6 or higher with the `requests` package
- ClickBench hits dataset indexed in OpenSearch
- OpenSearch running on localhost:9200 (or specify a different URL)

## Components

### 1. Star-tree Index Optimizer

Creates a star-tree optimized index and reindexes data from the original hits index.

```bash
python startree_optimizer.py [options]
```

Options:
- `--url`: OpenSearch URL (default: http://localhost:9200)
- `--source`: Source index name (default: hits)
- `--target`: Target index name (default: hits_startree)
- `--mappings`: Mappings file (default: index_mappings.json)
- `--username`: OpenSearch username (default: admin)
- `--password`: OpenSearch password (default: admin)

### 2. Benchmark Runner

Runs performance benchmarks on both the original and optimized indexes.

```bash
python benchmark_runner.py [options]
```

Options:
- `--url`: OpenSearch URL (default: http://localhost:9200)
- `--original`: Original index name (default: hits)
- `--optimized`: Optimized index name (default: hits_startree)
- `--iterations`: Number of benchmark iterations (default: 5)
- `--warmup`: Number of warmup iterations (default: 2)
- `--output`: Output file for results (default: benchmark_results.json)
- `--disable-cache`: Disable OpenSearch query request cache (default: True)
- `--enable-cache`: Enable OpenSearch query request cache
- `--clear-cache-between-runs`: Clear cache between benchmark iterations (default: False)

### 3. Performance Report Generator

Generates detailed performance reports from benchmark results.

```bash
python performance_report.py [options]
```

Options:
- `--results`: Benchmark results file (default: benchmark_results.json)
- `--output-dir`: Output directory for reports (default: reports)
- `--name`: Base name for report files (default: star_tree_performance_report)

## Star-tree Configuration

The star-tree index is configured with:

- **Dimensions**: UserID and SearchPhrase (the GROUP BY fields)
- **Metrics**: _doc_count (for COUNT(*) aggregation)
- **Max Leaf Docs**: 5000 (tuned for performance)

This configuration is optimized for the target query pattern and can be customized in `index_mappings.json`.

## Usage Example

1. Create the star-tree optimized index:

```bash
python startree_optimizer.py
```

2. Run benchmarks to compare performance:

```bash
python benchmark_runner.py
```

3. Generate performance reports:

```bash
python performance_report.py
```

4. Test different cache configurations:

```bash
./test_cache_configurations.sh
```

This script runs benchmarks with different cache settings and saves the results to separate files for comparison.

## Expected Results

The star-tree optimization typically provides significant performance improvements for GROUP BY queries:

- **Response Time**: 5-50x faster query execution
- **CPU Usage**: Lower CPU utilization during aggregation queries
- **Scalability**: Better performance as data volume increases

## Benchmarking Considerations

### Query Cache Disabling

The benchmark runner automatically disables OpenSearch's query request cache to ensure accurate performance measurements. This is done by adding the `request_cache=false` parameter to all search requests.

Why disable the query cache?
- **Accurate Measurements**: Ensures each query execution is measured without cache interference
- **Consistent Results**: Provides consistent timing across iterations
- **Fair Comparison**: Allows fair comparison between original and optimized indexes

Without disabling the cache, subsequent identical queries might return cached results, which would skew benchmark results by measuring cache retrieval time rather than actual query execution time.

You can control cache behavior using command-line options:
```bash
# Default behavior - cache disabled
python benchmark_runner.py

# Explicitly disable cache
python benchmark_runner.py --disable-cache

# Enable cache (for comparison or special scenarios)
python benchmark_runner.py --enable-cache

# Enable cache but clear it between benchmark iterations
python benchmark_runner.py --enable-cache --clear-cache-between-runs
```

When cache is enabled, the benchmark results will include this information in the metadata section of the output file.

### Cache Clearing Strategy

The benchmark runner provides three cache management strategies:

1. **Fully Disabled Cache** (default): Adds `request_cache=false` parameter to all queries
2. **Enabled Cache**: Uses OpenSearch's default caching behavior
3. **Clear Between Runs**: Clears the cache between benchmark iterations while keeping caching enabled

The third option is useful for scenarios where you want to:
- Measure the performance of the first query execution (cold cache)
- Compare cold cache vs. warm cache performance
- Ensure consistent starting conditions for each benchmark iteration

To compare the performance impact of different cache configurations, you can use the included test script:

```bash
./test_cache_configurations.sh
```

This script runs the benchmark with three different cache configurations:
1. Cache disabled (default)
2. Cache enabled
3. Cache enabled but cleared between runs

The results are saved to separate files, allowing you to analyze and compare the performance characteristics of each configuration.

## Report Formats

The performance report generator creates reports in multiple formats:

- **HTML**: Interactive report with tables and styling
- **Markdown**: Clean, readable format for documentation
- **CSV**: Tabular data for spreadsheet analysis
- **JSON**: Structured data for programmatic analysis

## Troubleshooting

- **Connection Issues**: Ensure OpenSearch is running and accessible
- **Authentication Errors**: Verify username and password
- **Index Not Found**: Check that the source index exists
- **Reindexing Failures**: Ensure sufficient disk space and memory

## References

- [OpenSearch Star-tree Documentation](https://opensearch.org/docs/latest/field-types/supported-field-types/star-tree/)
- [ClickBench GitHub Repository](https://github.com/ClickHouse/ClickBench)
