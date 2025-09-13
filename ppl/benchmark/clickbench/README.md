# ClickBench Manager - Consolidated OpenSearch ClickBench Tool

This directory contains a consolidated Python script that replaces all the individual shell scripts and Python scripts for managing OpenSearch ClickBench operations.

## Overview

The `clickbench_manager.py` script consolidates all ClickBench benchmark operations into a single tool:

- **OpenSearch Setup**: Download, configure, and set up OpenSearch 3.2.0
- **Index Management**: Prepare ClickBench hits index with proper mapping
- **Data Loading**: Load ClickBench data into OpenSearch with bulk operations
- **Snapshot Management**: Create, restore, and manage snapshots
- **Monitoring**: Monitor snapshot progress and system status

## Prerequisites

### System Requirements

- **Python 3.6+** with the following packages:
  - `requests` - for HTTP operations
  - `argparse` - for command-line parsing (built-in)
  - Standard library modules: `json`, `gzip`, `os`, `sys`, `time`, `subprocess`, `shutil`, `tarfile`, `pathlib`

- **System Tools**:
  - `curl` - for HTTP requests
  - `git` - for cloning repositories
  - `tar` - for extracting archives
  - `java` - Java 11 or higher (for OpenSearch)

### Installing Python Dependencies

```bash
pip install requests
```

### Installing System Tools

**macOS (with Homebrew):**
```bash
brew install curl git openjdk@11
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install curl git openjdk-11-jdk
```

**CentOS/RHEL:**
```bash
sudo yum install curl git java-11-openjdk-devel
```

## Quick Start

### 1. Setup OpenSearch

Download and configure OpenSearch 3.2.0:

```bash
./clickbench_manager.py setup-opensearch
```

This will:
- Download OpenSearch 3.2.0
- Extract and configure it
- Remove unnecessary plugins (keep only `opensearch-sql` and `opensearch-job-scheduler`)
- Update JVM memory settings to 16GB
- Set appropriate permissions

### 2. Start OpenSearch

```bash
cd opensearch-3.2.0
./bin/opensearch
```

OpenSearch will be available at `http://localhost:9200` with default credentials `admin/admin`.

### 3. Prepare ClickBench Index

Create the hits index with proper mapping:

```bash
./clickbench_manager.py prepare-index
```

This will:
- Clone the ClickBench repository
- Validate the mapping file
- Create the hits index with proper settings

### 4. Load Data (Optional)

If you have the ClickBench data file (`hits.json.gz`):

```bash
./clickbench_manager.py load-data --data-file hits.json.gz
```

**Note**: You can download the data from: https://datasets.clickhouse.com/hits/tsv/hits.tsv.gz

## Command Reference

### Global Options

All commands support these global options:

- `--url URL`: OpenSearch URL (default: `http://localhost:9200`)
- `--index NAME`: Index name (default: `hits`)
- `--repo NAME`: Snapshot repository name (default: `hits_backup`)

### Available Commands

#### Setup and Configuration

**Setup OpenSearch**
```bash
./clickbench_manager.py setup-opensearch
```

**Prepare Index**
```bash
./clickbench_manager.py prepare-index [--force]
```
- `--force`: Force recreation of index if it exists

**Check Status**
```bash
./clickbench_manager.py status
```

#### Data Operations

**Load Data**
```bash
./clickbench_manager.py load-data [--data-file FILE] [--bulk-size SIZE]
```
- `--data-file FILE`: Data file to load (default: `hits.json.gz`)
- `--bulk-size SIZE`: Bulk request size (default: `10000`)

#### Snapshot Management

**Create Snapshot**
```bash
./clickbench_manager.py create-snapshot --snapshot-name NAME [--backup-dir DIR] [--monitor]
```
- `--snapshot-name NAME`: Name for the snapshot (required)
- `--backup-dir DIR`: Backup directory (default: `./snapshots`)
- `--monitor`: Monitor snapshot progress

**Note**: Use the global `--index` option to specify which index to snapshot (default: `hits`)

**List Snapshots**
```bash
./clickbench_manager.py list-snapshots
```

**Restore Snapshot**
```bash
./clickbench_manager.py restore-snapshot --snapshot-name NAME [--target-index INDEX] [--force] [--async]
```
- `--snapshot-name NAME`: Name of snapshot to restore (required)
- `--target-index INDEX`: Target index name (default: same as source)
- `--force`: Force restore (delete existing index)
- `--async`: Restore asynchronously

**Monitor Snapshot**
```bash
./clickbench_manager.py monitor-snapshot --snapshot-name NAME
```

**Register Repository**
```bash
./clickbench_manager.py register-repo --backup-dir DIR [--force]
```
- `--backup-dir DIR`: Backup directory path (required)
- `--force`: Force re-registration

## Usage Examples

### Complete Setup Workflow

```bash
# 1. Setup OpenSearch
./clickbench_manager.py setup-opensearch

# 2. Start OpenSearch (in another terminal)
cd opensearch-3.2.0 && ./bin/opensearch

# 3. Prepare the index
./clickbench_manager.py prepare-index

# 4. Check status
./clickbench_manager.py status

# 5. Load data (if available)
./clickbench_manager.py load-data --data-file hits.json.gz
```

### Snapshot Operations

```bash
# Create a snapshot
./clickbench_manager.py create-snapshot --snapshot-name backup_$(date +%Y%m%d) --monitor

# List all snapshots
./clickbench_manager.py list-snapshots

# Restore a snapshot to a different index
./clickbench_manager.py restore-snapshot --snapshot-name backup_20250912 --target-index hits_restored

# Monitor snapshot progress
./clickbench_manager.py monitor-snapshot --snapshot-name backup_20250912
```

### Different OpenSearch Configuration

```bash
# Use different OpenSearch URL and index name
./clickbench_manager.py --url http://localhost:9201 --index my_hits prepare-index

# Create snapshot of a specific index
./clickbench_manager.py --index my_custom_index create-snapshot --snapshot-name my_index_backup

# Create snapshot with custom repository
./clickbench_manager.py --repo my_backup create-snapshot --snapshot-name test_snapshot
```

## Configuration Details

### OpenSearch Configuration

The setup process configures OpenSearch with:

- **JVM Memory**: 16GB heap size (Xms16g, Xmx16g)
- **Plugins**: Only `opensearch-sql` and `opensearch-job-scheduler`
- **Version**: OpenSearch 3.2.0

**System Requirements**: Ensure your system has at least 32GB RAM when using 16GB heap size.

### ClickBench Index Configuration

The hits index is created with:

- **105 field mappings** from the ClickBench schema
- **Index sorting** on CounterID, EventDate, UserID, EventTime, WatchID (all descending)
- **Field types** including integers, longs, shorts, keywords, and dates
- **Date formats** supporting multiple timestamp formats

### Snapshot Configuration

Snapshots are configured with:

- **Repository type**: Filesystem (`fs`)
- **Compression**: Enabled
- **Chunk size**: 1GB
- **Transfer rates**: 40MB/s for both snapshot and restore operations

## Troubleshooting

### OpenSearch Path Repository Error

If you encounter a `path.repo` error when creating snapshots:

1. Stop OpenSearch
2. Edit `opensearch-3.2.0/config/opensearch.yml`
3. Add the following line:
   ```yaml
   path.repo: ["/path/to/your/snapshots/directory"]
   ```
4. Restart OpenSearch

### Java Version Issues

Ensure Java 11 or higher is installed:

```bash
java -version
```

If you need to install Java:
- **macOS**: `brew install openjdk@11`
- **Ubuntu**: `sudo apt-get install openjdk-11-jdk`
- **CentOS**: `sudo yum install java-11-openjdk-devel`

### Memory Issues

If OpenSearch fails to start due to memory issues:

1. Edit `opensearch-3.2.0/config/jvm.options`
2. Reduce heap size (e.g., change `-Xms16g` and `-Xmx16g` to `-Xms8g` and `-Xmx8g`)
3. Restart OpenSearch

### Connection Issues

If you can't connect to OpenSearch:

1. Check if OpenSearch is running: `curl http://localhost:9200`
2. Check the logs: `tail -f opensearch-3.2.0/logs/opensearch.log`
3. Verify the URL and port in your commands

## Migration from Individual Scripts

This consolidated script replaces the following individual scripts:

- `setup_opensearch_3.2.sh` → `clickbench_manager.py setup-opensearch`
- `prepare_hits.sh` → `clickbench_manager.py prepare-index`
- `load_fixed.py` → `clickbench_manager.py load-data`
- `snapshot_hits.sh` → `clickbench_manager.py create-snapshot`
- `restore_snapshot.sh` → `clickbench_manager.py restore-snapshot`
- `register_snapshot_repo.sh` → `clickbench_manager.py register-repo`
- `monitor_snapshot.sh` → `clickbench_manager.py monitor-snapshot`

The consolidated script provides the same functionality with improved error handling, better logging, and a consistent interface.

## Getting Help

For help with any command:

```bash
./clickbench_manager.py --help
./clickbench_manager.py COMMAND --help
```

For example:
```bash
./clickbench_manager.py create-snapshot --help
