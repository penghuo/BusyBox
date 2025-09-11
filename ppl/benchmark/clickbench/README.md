# OpenSearch 3.2.0 Setup and ClickBench Scripts

This directory contains shell scripts to automatically download, configure, and set up OpenSearch 3.2.0 with specific plugin and memory configurations, plus prepare ClickBench benchmark data.

## Overview

The `setup_opensearch_3.2.sh` script performs the following operations:

1. **Downloads OpenSearch 3.2.0** from the official OpenSearch artifacts repository
2. **Extracts the archive** to a local directory
3. **Manages plugins** by removing all plugins except:
   - `opensearch-sql`
   - `opensearch-job-scheduler`
4. **Updates JVM memory settings** from 1GB to 16GB (both Xms and Xmx)
5. **Sets appropriate permissions** for executable files



## Configuration Details

### JVM Memory Settings

The script configures OpenSearch to use:
- **Initial heap size (Xms)**: 16GB
- **Maximum heap size (Xmx)**: 16GB

**Note**: Ensure your system has sufficient RAM. The recommended system RAM is at least 32GB when using 16GB heap size.

### Plugins Retained

Only these plugins are kept after setup:
- **opensearch-sql**: Enables SQL query support
- **opensearch-job-scheduler**: Provides job scheduling capabilities

All other default plugins are removed to minimize the installation footprint.


# ClickBench Hits Index Preparation Script

The `prepare_hits.sh` script automates the setup of ClickBench benchmark data for OpenSearch performance testing.

## Overview

The `prepare_hits.sh` script performs the following operations:

1. **Clones ClickBench Repository** from https://github.com/ClickHouse/ClickBench
2. **Validates mapping file** from the repository
3. **Checks OpenSearch connectivity** and cluster status
4. **Creates the hits index** with proper mapping and settings
5. **Verifies index creation** and displays configuration details

## Prerequisites for ClickBench Script

Before running the ClickBench preparation script, ensure you have:

- **OpenSearch running** (use `setup_opensearch_3.2.sh` first)
- **git** for cloning repositories
- **curl** for HTTP requests
- **jq** for JSON processing

### Installing jq

**macOS (with Homebrew):**
```bash
brew install jq
```

**Ubuntu/Debian:**
```bash
sudo apt-get install jq
```

**CentOS/RHEL:**
```bash
sudo yum install jq
```

## ClickBench Script Usage

### Basic Usage

```bash
cd opensearch
./prepare_hits.sh
```

### Advanced Usage

```bash
# Force recreate index if it exists
./prepare_hits.sh --force

# Use different OpenSearch URL
./prepare_hits.sh --url http://localhost:9201

# Use custom index name
./prepare_hits.sh --index my_hits_index

# Show help
./prepare_hits.sh --help
```

### Command Line Options

- `-f, --force`: Force recreation of index (delete existing if present)
- `-u, --url URL`: OpenSearch URL (default: http://localhost:9200)
- `-i, --index NAME`: Index name (default: hits)
- `-h, --help`: Show help message

## What the ClickBench Script Does

1. **System Requirements Check**: Verifies git, curl, and jq are available
2. **OpenSearch Connectivity**: Tests connection to OpenSearch cluster
3. **Repository Management**: Clones or updates ClickBench repository
4. **Mapping Validation**: Validates the Elasticsearch mapping.json file
5. **Index Management**: Creates or verifies the hits index with proper mapping
6. **Verification**: Confirms index structure and displays configuration

## ClickBench Index Details

The hits index is created with:

- **105 field mappings** from the ClickBench schema
- **Index sorting** on CounterID, EventDate, UserID, EventTime, WatchID (all descending)
- **Field types** including integers, longs, shorts, keywords, and dates
- **Date formats** supporting multiple timestamp formats

### Key Fields in the Hits Index

- **CounterID**: Website/application identifier
- **EventDate/EventTime**: Timestamp fields for events
- **UserID/WatchID**: User and session identifiers
- **URL/Referer**: Web page and referrer information
- **UserAgent**: Browser and device information
- **Geographic data**: RegionID, CountryID fields
- **Performance metrics**: Various timing measurements

## After ClickBench Setup

Once the script completes successfully, you can:

### Check Index Status
```bash
curl -u admin:admin 'http://localhost:9200/hits/_stats?pretty'
```

### View Index Mapping
```bash
curl -u admin:admin 'http://localhost:9200/hits/_mapping?pretty'
```

### Load ClickBench Data

Follow the ClickBench documentation to load the actual benchmark dataset:

1. Navigate to the cloned repository: `cd ClickBench`
2. Follow instructions in the `elasticsearch/` directory
3. Use the provided data loading scripts




