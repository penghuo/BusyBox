#!/usr/bin/env python3
"""
Star-tree Optimizer for OpenSearch ClickBench

This script creates a star-tree optimized index for the ClickBench hits dataset
and reindexes data from the original index to the optimized one.

The star-tree index is configured to accelerate GROUP BY queries on UserID and SearchPhrase.
"""

import argparse
import json
import requests
import time
import sys
import os
from pathlib import Path

# Default configuration
DEFAULT_OPENSEARCH_URL = "http://localhost:9200"
DEFAULT_SOURCE_INDEX = "hits"
DEFAULT_TARGET_INDEX = "hits_startree"
DEFAULT_MAPPINGS_FILE = "index_mappings.json"
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "admin"

class StarTreeOptimizer:
    """Handles creation of star-tree optimized index and data migration."""
    
    def __init__(self, opensearch_url, source_index, target_index, 
                 mappings_file, username, password):
        """Initialize the optimizer with connection parameters."""
        self.opensearch_url = opensearch_url
        self.source_index = source_index
        self.target_index = target_index
        self.mappings_file = mappings_file
        self.auth = (username, password)
        self.session = requests.Session()
        self.session.auth = self.auth
        self.session.headers.update({"Content-Type": "application/json"})
    
    def check_connection(self):
        """Check if OpenSearch is accessible."""
        print(f"Checking connection to OpenSearch at {self.opensearch_url}...")
        try:
            response = self.session.get(self.opensearch_url, timeout=10)
            if response.status_code in [200, 201]:
                cluster_info = response.json()
                print(f"✓ Connected to OpenSearch cluster: {cluster_info.get('cluster_name', 'unknown')}")
                print(f"✓ Version: {cluster_info.get('version', {}).get('number', 'unknown')}")
                return True
            else:
                print(f"✗ OpenSearch returned status code: {response.status_code}")
                print(f"✗ Response: {response.text}")
                return False
        except Exception as e:
            print(f"✗ Failed to connect to OpenSearch: {e}")
            return False
    
    def check_source_index(self):
        """Check if source index exists and get document count."""
        print(f"Checking source index '{self.source_index}'...")
        try:
            response = self.session.get(f"{self.opensearch_url}/{self.source_index}")
            if response.status_code == 200:
                # Get document count
                count_resp = self.session.get(f"{self.opensearch_url}/{self.source_index}/_count")
                if count_resp.status_code == 200:
                    count = count_resp.json().get('count', 0)
                    print(f"✓ Source index '{self.source_index}' exists with {count:,} documents")
                    return True
                else:
                    print(f"✓ Source index '{self.source_index}' exists but couldn't get document count")
                    return True
            else:
                print(f"✗ Source index '{self.source_index}' does not exist")
                return False
        except Exception as e:
            print(f"✗ Error checking source index: {e}")
            return False
    
    def load_mappings(self):
        """Load index mappings from file."""
        print(f"Loading mappings from {self.mappings_file}...")
        try:
            with open(self.mappings_file, 'r') as f:
                mappings = json.load(f)
            print(f"✓ Mappings loaded successfully")
            return mappings
        except Exception as e:
            print(f"✗ Failed to load mappings: {e}")
            return None
    
    def create_target_index(self, mappings):
        """Create target index with star-tree configuration."""
        print(f"Creating target index '{self.target_index}'...")
        try:
            # Check if target index already exists
            response = self.session.get(f"{self.opensearch_url}/{self.target_index}")
            if response.status_code == 200:
                print(f"! Target index '{self.target_index}' already exists")
                user_input = input("Do you want to delete and recreate it? (y/n): ")
                if user_input.lower() != 'y':
                    print("Aborting index creation")
                    return False
                
                # Delete existing index
                delete_resp = self.session.delete(f"{self.opensearch_url}/{self.target_index}")
                if delete_resp.status_code not in [200, 404]:
                    print(f"✗ Failed to delete existing index: {delete_resp.text}")
                    return False
                print(f"✓ Existing index deleted")
            
            # Create new index with mappings
            create_resp = self.session.put(
                f"{self.opensearch_url}/{self.target_index}",
                json=mappings
            )
            
            if create_resp.status_code in [200, 201]:
                print(f"✓ Target index '{self.target_index}' created successfully")
                return True
            else:
                print(f"✗ Failed to create target index: {create_resp.status_code}")
                print(f"✗ Response: {create_resp.text}")
                return False
        except Exception as e:
            print(f"✗ Error creating target index: {e}")
            return False
    
    def reindex_data(self):
        """Reindex data from source to target index."""
        print(f"Reindexing data from '{self.source_index}' to '{self.target_index}'...")
        
        reindex_body = {
            "source": {
                "index": self.source_index
            },
            "dest": {
                "index": self.target_index
            }
        }
        
        try:
            # Start reindexing
            response = self.session.post(
                f"{self.opensearch_url}/_reindex?wait_for_completion=false",
                json=reindex_body
            )
            
            if response.status_code in [200, 201]:
                task_id = response.json().get('task')
                print(f"✓ Reindexing started with task ID: {task_id}")
                return self.monitor_reindex(task_id)
            else:
                print(f"✗ Failed to start reindexing: {response.status_code}")
                print(f"✗ Response: {response.text}")
                return False
        except Exception as e:
            print(f"✗ Error starting reindexing: {e}")
            return False
    
    def monitor_reindex(self, task_id):
        """Monitor reindexing progress."""
        print("Monitoring reindexing progress...")
        
        try:
            while True:
                response = self.session.get(f"{self.opensearch_url}/_tasks/{task_id}")
                
                if response.status_code != 200:
                    print(f"✗ Failed to get task status: {response.status_code}")
                    return False
                
                task_status = response.json()
                if task_status.get('completed', False):
                    print("✓ Reindexing completed!")
                    
                    # Get statistics
                    stats = task_status.get('response', {})
                    total = stats.get('total', 0)
                    created = stats.get('created', 0)
                    failures = len(stats.get('failures', []))
                    
                    print(f"✓ Total documents processed: {total:,}")
                    print(f"✓ Documents created: {created:,}")
                    
                    if failures > 0:
                        print(f"! There were {failures} failures during reindexing")
                    
                    return True
                
                # Get progress
                status = task_status.get('task', {}).get('status', {})
                total = status.get('total', 0)
                created = status.get('created', 0)
                
                if total > 0:
                    progress = (created / total) * 100
                    print(f"\rProgress: {progress:.2f}% ({created:,}/{total:,})", end="", flush=True)
                else:
                    print("\rWaiting for reindexing to start...", end="", flush=True)
                
                time.sleep(5)
                
        except KeyboardInterrupt:
            print("\nReindexing monitoring interrupted. The process continues in the background.")
            return True
        except Exception as e:
            print(f"\n✗ Error monitoring reindexing: {e}")
            return False
    
    def verify_optimization(self):
        """Verify that the star-tree index is properly configured."""
        print("Verifying star-tree optimization...")
        
        try:
            # Get index settings and mappings
            response = self.session.get(f"{self.opensearch_url}/{self.target_index}")
            
            if response.status_code != 200:
                print(f"✗ Failed to get index information: {response.status_code}")
                return False
            
            index_info = response.json()
            index_settings = index_info.get(self.target_index, {}).get('settings', {})
            index_mappings = index_info.get(self.target_index, {}).get('mappings', {})
            
            # Check for composite index setting
            composite_enabled = index_settings.get('index', {}).get('composite_index')
            if composite_enabled == 'true':
                print("✓ Composite index setting is enabled")
            else:
                print("! Composite index setting not found or not enabled")
            
            # Check for star-tree configuration
            composite_mappings = index_mappings.get('composite', {})
            if composite_mappings:
                print("✓ Composite mappings found")
                
                star_tree_config = None
                for name, config in composite_mappings.items():
                    if config.get('type') == 'star_tree':
                        star_tree_config = config
                        print(f"✓ Star-tree configuration found: {name}")
                        break
                
                if star_tree_config:
                    dimensions = star_tree_config.get('config', {}).get('ordered_dimensions', [])
                    metrics = star_tree_config.get('config', {}).get('metrics', [])
                    
                    print(f"✓ Dimensions: {', '.join(d.get('name', '') for d in dimensions)}")
                    print(f"✓ Metrics: {', '.join(m.get('name', '') for m in metrics)}")
                else:
                    print("! No star-tree configuration found in composite mappings")
            else:
                print("! No composite mappings found")
            
            # Get document count
            count_resp = self.session.get(f"{self.opensearch_url}/{self.target_index}/_count")
            if count_resp.status_code == 200:
                count = count_resp.json().get('count', 0)
                print(f"✓ Target index contains {count:,} documents")
            
            return True
            
        except Exception as e:
            print(f"✗ Error verifying optimization: {e}")
            return False
    
    def run(self):
        """Run the complete optimization process."""
        if not self.check_connection():
            return False
        
        if not self.check_source_index():
            return False
        
        mappings = self.load_mappings()
        if not mappings:
            return False
        
        if not self.create_target_index(mappings):
            return False
        
        if not self.reindex_data():
            return False
        
        if not self.verify_optimization():
            return False
        
        print("\n✓ Star-tree optimization completed successfully!")
        print(f"✓ Original index: {self.source_index}")
        print(f"✓ Optimized index: {self.target_index}")
        print("\nYou can now run benchmark tests to compare performance.")
        
        return True

def main():
    """Parse command line arguments and run the optimizer."""
    parser = argparse.ArgumentParser(
        description="Create a star-tree optimized index for ClickBench hits dataset"
    )
    
    parser.add_argument('--url', default=DEFAULT_OPENSEARCH_URL,
                       help=f'OpenSearch URL (default: {DEFAULT_OPENSEARCH_URL})')
    parser.add_argument('--source', default=DEFAULT_SOURCE_INDEX,
                       help=f'Source index name (default: {DEFAULT_SOURCE_INDEX})')
    parser.add_argument('--target', default=DEFAULT_TARGET_INDEX,
                       help=f'Target index name (default: {DEFAULT_TARGET_INDEX})')
    parser.add_argument('--mappings', default=DEFAULT_MAPPINGS_FILE,
                       help=f'Mappings file (default: {DEFAULT_MAPPINGS_FILE})')
    parser.add_argument('--username', default=DEFAULT_USERNAME,
                       help=f'OpenSearch username (default: {DEFAULT_USERNAME})')
    parser.add_argument('--password', default=DEFAULT_PASSWORD,
                       help=f'OpenSearch password (default: {DEFAULT_PASSWORD})')
    
    args = parser.parse_args()
    
    # Resolve mappings file path
    script_dir = Path(__file__).parent.absolute()
    mappings_file = script_dir / args.mappings
    
    optimizer = StarTreeOptimizer(
        opensearch_url=args.url,
        source_index=args.source,
        target_index=args.target,
        mappings_file=mappings_file,
        username=args.username,
        password=args.password
    )
    
    success = optimizer.run()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
