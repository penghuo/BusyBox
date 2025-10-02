# OpenSearch Index Creator and Data Loader

This script creates an OpenSearch index using predefined mappings and bulk loads data from NDJSON files.

## Prerequisites

1. **Python 3.6+** installed
2. **OpenSearch** running (default: localhost:9200)
3. **Dependencies** installed

## Installation

Install the required Python package:

```bash
pip install -r requirements.txt
```

Or install directly:
```bash
pip install opensearch-py
```

## Basic Usage

### Default Usage (Recommended)
The script is pre-configured for your specific use case:

```bash
python opensearch_loader.py
```

This will:
- Connect to OpenSearch at `localhost:9200`
- Create index `sso_logs-nginx-prod-2024.05.08` with 1 primary shard, 0 replicas
- Use mapping from `benchmark_index_mappings.json`
- Load data from `sso_logs-nginx-prod-2024.05.08_docs.ndjson`
- Process in batches of 1000 documents

### Advanced Usage

```bash
python opensearch_loader.py --host your-host --port 9200 --batch-size 500
```

## Command Line Options

| Option | Default | Description |
|--------|---------|-------------|
| `--host` | localhost | OpenSearch host |
| `--port` | 9200 | OpenSearch port |
| `--index-name` | sso_logs-nginx-prod-2024.05.08 | Target index name |
| `--mapping-file` | benchmark_index_mappings.json | JSON file with mappings |
| `--data-file` | sso_logs-nginx-prod-2024.05.08_docs.ndjson | NDJSON data file |
| `--batch-size` | 1000 | Documents per batch |
| `--primary-shards` | 1 | Number of primary shards |
| `--replica-shards` | 0 | Number of replica shards |
| `--username` | - | OpenSearch username |
| `--password` | - | OpenSearch password |
| `--ssl` | false | Use SSL connection |
| `--create-only` | false | Only create index, don't load data |
| `--load-only` | false | Only load data, don't create index |

## Examples

### Create index only (no data loading)
```bash
python opensearch_loader.py --create-only
```

### Load data only (assumes index exists)
```bash
python opensearch_loader.py --load-only
```

### Connect to remote OpenSearch with authentication
```bash
python opensearch_loader.py --host remote-host.example.com --port 443 --ssl --username admin --password secret
```

### Use different batch size for faster/slower processing
```bash
python opensearch_loader.py --batch-size 2000
```

## Output Example

```
🚀 OpenSearch Index Creator and Data Loader
==================================================
✓ Connected to OpenSearch at localhost:9200
✓ Loaded mappings from benchmark_index_mappings.json
✓ Created index 'sso_logs-nginx-prod-2024.05.08' with 1 primary shard(s) and 0 replica(s)
✓ Loaded 2000 lines from sso_logs-nginx-prod-2024.05.08_docs.ndjson
Starting bulk indexing with batch size: 1000
Indexed 1000 documents (1250.5 docs/sec)
✓ Bulk indexing completed!
  Total documents indexed: 1000
  Total time: 0.80 seconds
  Average rate: 1250.0 documents/second

📊 Index Information for 'sso_logs-nginx-prod-2024.05.08':
  Documents: 1,000
  Size: 0.85 MB
  Primary shards: 1
  Replica shards: 0

✅ Script completed successfully!
```

## Troubleshooting

### Connection Issues
- Ensure OpenSearch is running
- Check host and port settings
- Verify authentication credentials if using security

### Memory Issues
- Reduce `--batch-size` (try 500 or 250)
- Ensure sufficient system memory

### Permission Issues
- Make script executable: `chmod +x opensearch_loader.py`
- Check OpenSearch user permissions

### Data Issues
- Verify NDJSON file format (alternating action/document lines)
- Check mapping file contains the target index mapping
- Ensure JSON is valid in both files

## File Requirements

1. **benchmark_index_mappings.json** - Contains index mappings
2. **sso_logs-nginx-prod-2024.05.08_docs.ndjson** - Contains documents to index
3. Both files must be in the same directory as the script (unless specified otherwise)

## Notes

- The script will prompt before overwriting existing indices
- Progress is displayed during bulk loading
- Error handling includes retry logic for transient failures
- Index statistics are shown after completion
