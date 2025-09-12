#!/usr/bin/env python3

import requests
import json
import gzip
from itertools import islice

# Number of documents per bulk request
BULK_SIZE = 10000
ES_URL = "http://localhost:9200/_bulk"
INDEX = "hits"
TOTAL_RECORDS = 99997497

# Precompute action metadata line once
ACTION_META_LINE = json.dumps({"index": {"_index": INDEX}}) + "\n"

REQUEST_TIMEOUT = 30  # seconds

def bulk_stream(docs):
    """Generate bulk request body as bytes"""
    for doc in docs:
        # Yield action metadata line
        yield ACTION_META_LINE.encode("utf-8")
        # Yield document line (ensure it's properly encoded)
        doc_line = doc.strip() + "\n"
        yield doc_line.encode("utf-8")

def send_bulk(session, docs, batch_num):
    """Send a bulk request to OpenSearch/Elasticsearch"""
    # Convert generator to bytes
    bulk_data = b''.join(bulk_stream(docs))
    
    resp = session.post(ES_URL, data=bulk_data, timeout=REQUEST_TIMEOUT)
    
    if resp.status_code >= 300:
        print(f"\nSent batch {batch_num} ({len(docs)} docs) - Warning: HTTP {resp.status_code}")
        print(f"Response: {resp.text[:500]}")  # Show first 500 chars of error
        return 0
    
    try:
        body = resp.json()
        if body.get("errors"):
            items = body.get("items", [])
            err = sum(1 for i in items if "error" in i.get("index", {}))
            if err:
                print(f"\nBatch {batch_num}: {err} item errors")
                # Show first error for debugging
                for item in items[:3]:  # Show first 3 errors
                    if "error" in item.get("index", {}):
                        error_info = item["index"]["error"]
                        print(f"  Error: {error_info.get('type', 'unknown')} - {error_info.get('reason', 'no reason')}")
    except json.JSONDecodeError:
        print(f"\nBatch {batch_num}: Could not parse response as JSON")
        print(f"Response: {resp.text[:200]}")
    
    return len(docs)

def main():
    """Main function to load data into OpenSearch"""
    total_docs = 0
    batch_num = 0
    
    print(f"Loading data into OpenSearch at {ES_URL}")
    print(f"Target index: {INDEX}")
    print(f"Batch size: {BULK_SIZE}")
    print(f"Expected total records: {TOTAL_RECORDS:,}")
    print("-" * 50)
    
    with requests.Session() as session:
        # Set proper headers for bulk requests
        session.headers.update({
            "Content-Type": "application/x-ndjson",
            "Authorization": "Basic YWRtaW46YWRtaW4="  # admin:admin base64 encoded
        })
        
        # Test connection first
        try:
            test_resp = session.get("http://localhost:9200", timeout=5)
            if test_resp.status_code == 200:
                cluster_info = test_resp.json()
                print(f"Connected to: {cluster_info.get('cluster_name', 'unknown')} "
                      f"(version: {cluster_info.get('version', {}).get('number', 'unknown')})")
            else:
                print(f"Warning: OpenSearch responded with status {test_resp.status_code}")
        except Exception as e:
            print(f"Warning: Could not connect to OpenSearch: {e}")
            print("Continuing anyway...")
        
        # Read compressed NDJSON directly from hits.json.gz, decompressing on the fly
        try:
            with gzip.open("hits.json.gz", mode="rt", encoding="utf-8") as f:
                print("Reading from hits.json.gz")
                
                while True:
                    docs = list(islice(f, BULK_SIZE))
                    if not docs:
                        break
                    
                    batch_num += 1
                    docs_sent = send_bulk(session, docs, batch_num)
                    total_docs += docs_sent
                    
                    pct = (total_docs / TOTAL_RECORDS) * 100 if TOTAL_RECORDS else 0
                    print(f"\rProgress: {pct:.2f}% ({total_docs:,}/{TOTAL_RECORDS:,}) - Batch {batch_num}", end="", flush=True)
                    
                    # Print newline every 10 batches for readability
                    if batch_num % 10 == 0:
                        print()
                
        except FileNotFoundError:
            print("Error: hits.json.gz file not found!")
            print("Please ensure the ClickBench data file is in the current directory.")
            print("You can download it from: https://datasets.clickhouse.com/hits/tsv/hits.tsv.gz")
            return 1
        except Exception as e:
            print(f"\nError reading data file: {e}")
            return 1
    
    print(f"\n\nCompleted!")
    print(f"Total documents sent: {total_docs:,}")
    
    # Verify the index
    try:
        with requests.Session() as session:
            session.headers.update({"Authorization": "Basic YWRtaW46YWRtaW4="})
            count_resp = session.get(f"http://localhost:9200/{INDEX}/_count", timeout=10)
            if count_resp.status_code == 200:
                count_data = count_resp.json()
                indexed_count = count_data.get("count", 0)
                print(f"Documents in index: {indexed_count:,}")
                if indexed_count != total_docs:
                    print(f"Warning: Mismatch between sent ({total_docs:,}) and indexed ({indexed_count:,}) documents")
            else:
                print(f"Could not verify index count (HTTP {count_resp.status_code})")
    except Exception as e:
        print(f"Could not verify index: {e}")
    
    return 0

if __name__ == "__main__":
    exit(main())
