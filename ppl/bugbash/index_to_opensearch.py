#!/usr/bin/env python3
"""
OpenSearch Bulk Indexing Script

This script loads events from events.json and indexes them to OpenSearch using bulk requests.
"""

import argparse
import json
import sys
import time
from urllib.parse import urlparse

try:
    from opensearchpy import OpenSearch, helpers, RequestsHttpConnection
    from requests.auth import HTTPBasicAuth
except ImportError:
    print("Required packages not found. Installing opensearch-py...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "opensearch-py"])
    from opensearchpy import OpenSearch, helpers, RequestsHttpConnection
    from requests.auth import HTTPBasicAuth

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Index events to OpenSearch')
    parser.add_argument('--index', '-i', required=True, help='OpenSearch index name')
    parser.add_argument('--url', default='http://localhost:9200', help='OpenSearch URL (default: http://localhost:9200)')
    parser.add_argument('--username', required=True, help='OpenSearch username')
    parser.add_argument('--password', '-P', required=True, help='OpenSearch password')
    parser.add_argument('--file', '-f', default='events.json', help='Path to events.json file (default: events.json)')
    parser.add_argument('--batch-size', '-b', type=int, default=1000, 
                        help='Number of documents per bulk request (default: 1000)')
    
    return parser.parse_args()

def create_opensearch_client(args):
    """Create and return an OpenSearch client"""
    # Parse the URL to extract host, port, and protocol
    url = urlparse(args.url)
    host = url.hostname or 'localhost'
    port = url.port or (443 if url.scheme == 'https' else 9200)
    use_ssl = url.scheme == 'https'
    
    # Configure OpenSearch connection
    hosts = [{'host': host, 'port': port}]
    http_auth = (args.username, args.password)
    verify_certs = False  # In production, this should be True with proper certificates
    
    # Create the client
    client = OpenSearch(
        hosts=hosts,
        http_auth=http_auth,
        use_ssl=use_ssl,
        verify_certs=verify_certs,
        connection_class=RequestsHttpConnection
    )
    
    return client

def read_events(file_path, batch_size):
    """
    Generator function to read events from file in batches
    
    Args:
        file_path: Path to the events.json file
        batch_size: Number of events to yield in each batch
        
    Yields:
        List of events (batch_size or fewer)
    """
    batch = []
    
    try:
        with open(file_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    # Parse the JSON event
                    event = json.loads(line.strip())
                    batch.append(event)
                    
                    # Yield batch when it reaches the specified size
                    if len(batch) >= batch_size:
                        yield batch
                        batch = []
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON at line {line_num}: {e}")
                    continue
            
            # Yield any remaining events
            if batch:
                yield batch
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

def prepare_bulk_actions(events, index_name):
    """
    Prepare events for bulk indexing
    
    Args:
        events: List of event dictionaries
        index_name: Name of the index to use
        
    Returns:
        List of actions for bulk API
    """
    actions = []
    
    for event in events:
        # Create the action for this event
        action = {
            "_index": index_name,
            "_source": event
        }
        
        # Use @timestamp as document ID if available
        if "@timestamp" in event:
            action["_id"] = f"{event['@timestamp']}_{hash(json.dumps(event))}"
        
        actions.append(action)
    
    return actions

def bulk_index(client, events, index_name):
    """
    Index events using the bulk API
    
    Args:
        client: OpenSearch client
        events: List of event dictionaries
        index_name: Name of the index to use
        
    Returns:
        Tuple of (success_count, error_count)
    """
    actions = prepare_bulk_actions(events, index_name)
    
    try:
        # Use the helpers.bulk function to perform bulk indexing
        success, errors = helpers.bulk(
            client,
            actions,
            stats_only=True,
            raise_on_error=False
        )
        
        return success, len(errors) if errors else 0
    except Exception as e:
        print(f"Error during bulk indexing: {e}")
        return 0, len(actions)

def main():
    """Main function"""
    args = parse_args()
    
    # Create OpenSearch client
    client = create_opensearch_client(args)
    
    # Check if the client can connect to OpenSearch
    try:
        info = client.info()
        print(f"Connected to OpenSearch cluster: {info['cluster_name']}")
    except Exception as e:
        print(f"Error connecting to OpenSearch: {e}")
        sys.exit(1)
    
    # Initialize counters
    total_events = 0
    total_success = 0
    total_errors = 0
    batch_count = 0
    
    # Start timing
    start_time = time.time()
    
    # Process events in batches
    for batch in read_events(args.file, args.batch_size):
        batch_count += 1
        batch_size = len(batch)
        total_events += batch_size
        
        # Index the batch
        success, errors = bulk_index(client, batch, args.index)
        total_success += success
        total_errors += errors
        
        # Print progress
        print(f"Batch {batch_count}: Indexed {success} events, {errors} errors")
    
    # Calculate elapsed time
    elapsed_time = time.time() - start_time
    
    # Print summary
    print("\nIndexing Summary:")
    print(f"Total events processed: {total_events}")
    print(f"Successfully indexed: {total_success}")
    print(f"Errors: {total_errors}")
    print(f"Time elapsed: {elapsed_time:.2f} seconds")
    print(f"Indexing rate: {total_events / elapsed_time:.2f} events/second")

if __name__ == "__main__":
    main()
