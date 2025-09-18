# OpenSearch Tools

## Index Template Loader

Examples:
```bash
# Run without authentication
./load_template.sh

# Run with authentication
./load_template.sh -u admin -p admin
```

## Event Generator

Generate sample events based on a template:

```bash
# Generate 1000 events starting from a specific timestamp
python generate_events.py --count 1000 --start-timestamp "2025-09-04T16:17:39.133Z"

# Generate events with custom field distributions
python generate_events.py --count 1000 --start-timestamp "2025-09-04T16:17:39.133Z" --config sample_config.json
```

## OpenSearch Bulk Indexer

Index events from events.json to OpenSearch using bulk requests:

```bash
# Basic usage with required parameters
./index_to_opensearch.py --index logs-test --username admin --password admin

# Specify OpenSearch URL
./index_to_opensearch.py --index logs-test --url https://opensearch-host:9200 --username admin --password admin

# Custom batch size
./index_to_opensearch.py --index logs-test --batch-size 500 --username admin --password admin

# Specify a different events file
./index_to_opensearch.py --index logs-test --file /path/to/events.json --username admin --password admin
```

### Parameters

- `--index`, `-i`: OpenSearch index name (required)
- `--url`: OpenSearch URL (default: http://localhost:9200)
- `--username`: OpenSearch username (required)
- `--password`, `-P`: OpenSearch password (required)
- `--file`, `-f`: Path to events.json file (default: events.json)
- `--batch-size`, `-b`: Number of documents per bulk request (default: 1000)


