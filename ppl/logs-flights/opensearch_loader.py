#!/usr/bin/env python3
"""
OpenSearch Index Creation and Data Loading Script

This script creates an OpenSearch index using mappings from benchmark_index_mappings.json
and loads data from an NDJSON file using bulk indexing.

Requirements:
- opensearch-py
"""

import json
import argparse
import sys
from typing import Dict, Any, Generator, Tuple
import time

try:
    from opensearchpy import OpenSearch
    from opensearchpy.exceptions import RequestError, ConnectionError
except ImportError:
    print("Error: opensearch-py is not installed. Please install it with:")
    print("pip install opensearch-py")
    sys.exit(1)


class OpenSearchLoader:
    def __init__(self, host='localhost', port=9200, use_ssl=False, verify_certs=False, 
                 username=None, password=None):
        """Initialize OpenSearch client"""
        self.client_config = {
            'hosts': [{'host': host, 'port': port}],
            'use_ssl': use_ssl,
            'verify_certs': verify_certs,
            'ssl_show_warn': False
        }
        
        if username and password:
            self.client_config['http_auth'] = (username, password)
        
        try:
            self.client = OpenSearch(**self.client_config)
            # Test connection
            self.client.info()
            print(f"✓ Connected to OpenSearch at {host}:{port}")
        except ConnectionError as e:
            print(f"✗ Failed to connect to OpenSearch: {e}")
            sys.exit(1)
    
    def load_index_mappings(self, mapping_file: str) -> Dict[str, Any]:
        """Load index mappings from JSON file"""
        try:
            with open(mapping_file, 'r') as f:
                mappings = json.load(f)
            print(f"✓ Loaded mappings from {mapping_file}")
            return mappings
        except FileNotFoundError:
            print(f"✗ Mapping file not found: {mapping_file}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"✗ Invalid JSON in mapping file: {e}")
            sys.exit(1)
    
    def create_index(self, index_name: str, mapping: Dict[str, Any], 
                    primary_shards: int = 1, replica_shards: int = 0):
        """Create OpenSearch index with specified mapping and shard configuration"""
        
        # Prepare index configuration
        index_config = {
            "settings": {
                "number_of_shards": primary_shards,
                "number_of_replicas": replica_shards
            },
            "mappings": mapping.get("mappings", {})
        }
        
        # Check if index already exists
        if self.client.indices.exists(index=index_name):
            print(f"⚠ Index '{index_name}' already exists")
            response = input("Do you want to delete and recreate it? (y/N): ")
            if response.lower() == 'y':
                self.client.indices.delete(index=index_name)
                print(f"✓ Deleted existing index '{index_name}'")
            else:
                print("Skipping index creation")
                return False
        
        try:
            # Create the index
            response = self.client.indices.create(
                index=index_name,
                body=index_config
            )
            print(f"✓ Created index '{index_name}' with {primary_shards} primary shard(s) and {replica_shards} replica(s)")
            return True
        except RequestError as e:
            print(f"✗ Failed to create index: {e}")
            return False
    
    def read_ndjson_bulk_data(self, ndjson_file: str) -> Generator[Tuple[Dict, Dict], None, None]:
        """Read NDJSON file and yield (action, document) pairs for bulk indexing"""
        try:
            with open(ndjson_file, 'r') as f:
                lines = f.readlines()
            
            print(f"✓ Loaded {len(lines)} lines from {ndjson_file}")
            
            # Process pairs of lines (action + document)
            for i in range(0, len(lines), 2):
                if i + 1 >= len(lines):
                    break
                
                try:
                    action_line = json.loads(lines[i].strip())
                    doc_line = json.loads(lines[i + 1].strip())
                    yield action_line, doc_line
                except json.JSONDecodeError as e:
                    print(f"⚠ Skipping invalid JSON at line {i+1}: {e}")
                    continue
                    
        except FileNotFoundError:
            print(f"✗ Data file not found: {ndjson_file}")
            sys.exit(1)
    
    def bulk_index_data(self, ndjson_file: str, batch_size: int = 1000):
        """Bulk index data from NDJSON file"""
        
        print(f"Starting bulk indexing with batch size: {batch_size}")
        
        batch = []
        total_indexed = 0
        start_time = time.time()
        
        for action, document in self.read_ndjson_bulk_data(ndjson_file):
            # Add action
            batch.append(action)
            # Add document
            batch.append(document)
            
            # Process batch when it reaches the specified size
            if len(batch) >= batch_size * 2:  # *2 because each document has action + doc
                success_count = self._process_batch(batch)
                total_indexed += success_count
                batch = []
                
                # Progress update
                elapsed = time.time() - start_time
                rate = total_indexed / elapsed if elapsed > 0 else 0
                print(f"Indexed {total_indexed} documents ({rate:.1f} docs/sec)")
        
        # Process remaining batch
        if batch:
            success_count = self._process_batch(batch)
            total_indexed += success_count
        
        elapsed = time.time() - start_time
        avg_rate = total_indexed / elapsed if elapsed > 0 else 0
        print(f"✓ Bulk indexing completed!")
        print(f"  Total documents indexed: {total_indexed}")
        print(f"  Total time: {elapsed:.2f} seconds")
        print(f"  Average rate: {avg_rate:.1f} documents/second")
    
    def _process_batch(self, batch: list) -> int:
        """Process a batch of documents"""
        try:
            response = self.client.bulk(body=batch, refresh=False)
            
            # Count successful operations
            success_count = 0
            errors = []
            
            if 'items' in response:
                for item in response['items']:
                    for action, result in item.items():
                        if result.get('status') in [200, 201]:
                            success_count += 1
                        else:
                            errors.append(result.get('error', 'Unknown error'))
            
            if errors:
                print(f"⚠ Batch had {len(errors)} errors: {errors[:3]}...")  # Show first 3 errors
            
            return success_count
            
        except Exception as e:
            print(f"✗ Batch indexing failed: {e}")
            return 0
    
    def get_index_info(self, index_name: str):
        """Get and display index information"""
        try:
            # Get index stats
            stats = self.client.indices.stats(index=index_name)
            index_stats = stats['indices'][index_name]
            
            # Get index settings
            settings = self.client.indices.get_settings(index=index_name)
            index_settings = settings[index_name]['settings']['index']
            
            print(f"\n📊 Index Information for '{index_name}':")
            print(f"  Documents: {index_stats['total']['docs']['count']:,}")
            print(f"  Size: {index_stats['total']['store']['size_in_bytes'] / (1024*1024):.2f} MB")
            print(f"  Primary shards: {index_settings.get('number_of_shards', 'N/A')}")
            print(f"  Replica shards: {index_settings.get('number_of_replicas', 'N/A')}")
            
        except Exception as e:
            print(f"⚠ Could not retrieve index info: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Create OpenSearch index and load data from NDJSON file"
    )
    parser.add_argument(
        '--host', default='localhost',
        help='OpenSearch host (default: localhost)'
    )
    parser.add_argument(
        '--port', type=int, default=9200,
        help='OpenSearch port (default: 9200)'
    )
    parser.add_argument(
        '--index-name', default='opensearch_flights',
        help='Index name (default: opensearch_flights)'
    )
    parser.add_argument(
        '--mapping-file', default='index_mappings.json',
        help='JSON file containing index mappings (default: benchmark_index_mappings.json)'
    )
    parser.add_argument(
        '--data-file', default='data.ndjson',
        help='NDJSON file containing documents to index (default: sso_logs-nginx-prod-2024.05.08_docs.ndjson)'
    )
    parser.add_argument(
        '--batch-size', type=int, default=1000,
        help='Batch size for bulk indexing (default: 1000)'
    )
    parser.add_argument(
        '--primary-shards', type=int, default=1,
        help='Number of primary shards (default: 1)'
    )
    parser.add_argument(
        '--replica-shards', type=int, default=0,
        help='Number of replica shards (default: 0)'
    )
    parser.add_argument(
        '--username', help='OpenSearch username (optional)'
    )
    parser.add_argument(
        '--password', help='OpenSearch password (optional)'
    )
    parser.add_argument(
        '--ssl', action='store_true',
        help='Use SSL connection'
    )
    parser.add_argument(
        '--create-only', action='store_true',
        help='Only create index, do not load data'
    )
    parser.add_argument(
        '--load-only', action='store_true',
        help='Only load data, do not create index'
    )
    
    args = parser.parse_args()
    
    print("🚀 OpenSearch Index Creator and Data Loader")
    print("=" * 50)
    
    # Initialize OpenSearch loader
    loader = OpenSearchLoader(
        host=args.host,
        port=args.port,
        use_ssl=args.ssl,
        username=args.username,
        password=args.password
    )
    
    # Load mappings
    mappings = loader.load_index_mappings(args.mapping_file)
    
    # Check if the specified index mapping exists
    if args.index_name not in mappings:
        print(f"✗ Index mapping for '{args.index_name}' not found in {args.mapping_file}")
        print(f"Available mappings: {list(mappings.keys())}")
        sys.exit(1)
    
    index_mapping = mappings[args.index_name]
    
    # Create index (unless load-only mode)
    if not args.load_only:
        success = loader.create_index(
            args.index_name, 
            index_mapping,
            args.primary_shards,
            args.replica_shards
        )
        if not success:
            print("✗ Index creation failed")
            sys.exit(1)
    
    # Load data (unless create-only mode)
    if not args.create_only:
        loader.bulk_index_data(args.data_file, args.batch_size)
    
    # Show final index information
    loader.get_index_info(args.index_name)
    
    print("\n✅ Script completed successfully!")


if __name__ == "__main__":
    main()
