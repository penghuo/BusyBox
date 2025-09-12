#!/bin/bash

# Quick Snapshot Progress Checker
# Shows snapshot progress percentage in a simple format

OPENSEARCH_URL="http://localhost:9200"
SNAPSHOT_REPO="hits_backup"
SNAPSHOT_NAME="$1"

if [[ -z "$SNAPSHOT_NAME" ]]; then
    echo "Usage: $0 <snapshot_name>"
    echo "Example: $0 hits_snapshot_20250912_152630"
    exit 1
fi

echo "Checking progress for: $SNAPSHOT_REPO/$SNAPSHOT_NAME"
echo "=============================================="

# Get basic snapshot info
SNAPSHOT_INFO=$(curl -s "$OPENSEARCH_URL/_snapshot/$SNAPSHOT_REPO/$SNAPSHOT_NAME")
STATE=$(echo "$SNAPSHOT_INFO" | jq -r '.snapshots[0].state // "UNKNOWN"')

echo "State: $STATE"

if [[ "$STATE" == "IN_PROGRESS" ]]; then
    # Try to get detailed status
    STATUS_INFO=$(curl -s "$OPENSEARCH_URL/_snapshot/$SNAPSHOT_REPO/$SNAPSHOT_NAME/_status")
    
    if [[ -n "$STATUS_INFO" ]]; then
        echo
        echo "Raw status response:"
        echo "$STATUS_INFO" | jq '.'
        
        # Try to extract progress info
        SHARDS_TOTAL=$(echo "$STATUS_INFO" | jq -r '.snapshots[0].shards_stats.total // 0')
        SHARDS_DONE=$(echo "$STATUS_INFO" | jq -r '.snapshots[0].shards_stats.done // 0')
        SHARDS_STARTED=$(echo "$STATUS_INFO" | jq -r '.snapshots[0].shards_stats.started // 0')
        PROCESSED_BYTES=$(echo "$STATUS_INFO" | jq -r '.snapshots[0].stats.processed.size_in_bytes // 0')
        TOTAL_BYTES=$(echo "$STATUS_INFO" | jq -r '.snapshots[0].stats.total.size_in_bytes // 0')
        PROCESSED_FILES=$(echo "$STATUS_INFO" | jq -r '.snapshots[0].stats.processed.file_count // 0')
        TOTAL_FILES=$(echo "$STATUS_INFO" | jq -r '.snapshots[0].stats.total.file_count // 0')
        
        echo
        echo "Extracted Progress Data:"
        echo "Shards: $SHARDS_DONE done, $SHARDS_STARTED started / $SHARDS_TOTAL total"
        echo "Files: $PROCESSED_FILES / $TOTAL_FILES"
        echo "Bytes: $PROCESSED_BYTES / $TOTAL_BYTES"
        
        if [[ $SHARDS_TOTAL -gt 0 ]]; then
            SHARD_PERCENT=$((SHARDS_DONE * 100 / SHARDS_TOTAL))
            echo "Shard Completion: $SHARD_PERCENT%"
        fi
        
        if [[ $TOTAL_FILES -gt 0 ]]; then
            FILE_PERCENT=$((PROCESSED_FILES * 100 / TOTAL_FILES))
            echo "File Progress: $FILE_PERCENT%"
        fi
        
        if [[ $TOTAL_BYTES -gt 0 ]]; then
            SIZE_PERCENT=$((PROCESSED_BYTES * 100 / TOTAL_BYTES))
            SIZE_GB=$((PROCESSED_BYTES / 1024 / 1024 / 1024))
            TOTAL_GB=$((TOTAL_BYTES / 1024 / 1024 / 1024))
            echo "Size Progress: $SIZE_PERCENT% ($SIZE_GB GB / $TOTAL_GB GB)"
        fi
    else
        echo "Could not get detailed status"
    fi
    
elif [[ "$STATE" == "SUCCESS" ]]; then
    echo "Snapshot completed successfully!"
    TOTAL_SIZE=$(echo "$SNAPSHOT_INFO" | jq -r '.snapshots[0].stats.total.size_in_bytes // 0')
    DURATION=$(echo "$SNAPSHOT_INFO" | jq -r '.snapshots[0].duration_in_millis // 0')
    echo "Total size: $((TOTAL_SIZE / 1024 / 1024)) MB"
    echo "Duration: $((DURATION / 1000)) seconds"
    
elif [[ "$STATE" == "FAILED" ]]; then
    echo "Snapshot failed!"
    FAILURES=$(echo "$SNAPSHOT_INFO" | jq -r '.snapshots[0].failures // []')
    if [[ "$FAILURES" != "[]" ]]; then
        echo "Failures: $FAILURES"
    fi
else
    echo "Snapshot state: $STATE"
fi
