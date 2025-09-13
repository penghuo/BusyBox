#!/usr/bin/env python3
"""
ClickBench Manager - Consolidated OpenSearch ClickBench Management Tool

This script consolidates all ClickBench benchmark operations into a single tool:
- OpenSearch setup and configuration
- Index preparation and data loading
- Snapshot creation, restoration, and management
- Monitoring and status checking

Author: Generated for BusyBox project
"""

import argparse
import json
import gzip
import os
import sys
import time
import subprocess
import requests
import shutil
import tarfile
from pathlib import Path
from itertools import islice
from typing import Dict, List, Optional, Tuple
import tempfile
import base64

# Configuration constants
OPENSEARCH_VERSION = "3.2.0"
OPENSEARCH_DOWNLOAD_URL = f"https://artifacts.opensearch.org/releases/bundle/opensearch/{OPENSEARCH_VERSION}/opensearch-{OPENSEARCH_VERSION}-linux-x64.tar.gz"
CLICKBENCH_REPO = "https://github.com/ClickHouse/ClickBench"
DEFAULT_OPENSEARCH_URL = "http://localhost:9200"
DEFAULT_INDEX_NAME = "hits"
DEFAULT_SNAPSHOT_REPO = "hits_backup"
DEFAULT_BULK_SIZE = 10000
TOTAL_RECORDS = 99997497

# Colors for output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

def log_info(message: str):
    print(f"{Colors.BLUE}[INFO]{Colors.NC} {message}")

def log_success(message: str):
    print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {message}")

def log_warning(message: str):
    print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}")

def log_error(message: str):
    print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")

def command_exists(command: str) -> bool:
    """Check if a command exists in the system PATH."""
    return shutil.which(command) is not None

def run_command(command: List[str], cwd: Optional[str] = None, check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(command, cwd=cwd, check=check, capture_output=True, text=True)
        return result
    except subprocess.CalledProcessError as e:
        log_error(f"Command failed: {' '.join(command)}")
        log_error(f"Error: {e.stderr}")
        raise

class OpenSearchManager:
    """Manages OpenSearch installation and configuration."""
    
    def __init__(self, opensearch_url: str = DEFAULT_OPENSEARCH_URL):
        self.opensearch_url = opensearch_url
        self.opensearch_dir = f"opensearch-{OPENSEARCH_VERSION}"
        self.opensearch_archive = f"opensearch-{OPENSEARCH_VERSION}-linux-x64.tar.gz"
    
    def check_requirements(self) -> bool:
        """Check system requirements for OpenSearch setup."""
        log_info("Checking system requirements...")
        
        required_commands = ["curl", "tar", "java"]
        for cmd in required_commands:
            if not command_exists(cmd):
                log_error(f"Required command '{cmd}' not found. Please install it first.")
                return False
        
        # Check Java version
        try:
            result = run_command(["java", "-version"], check=False)
            java_output = result.stderr if result.stderr else result.stdout
            
            # Extract Java version
            import re
            version_match = re.search(r'"(\d+)\.', java_output)
            if not version_match:
                version_match = re.search(r'version "(\d+)', java_output)
            
            if version_match:
                java_version = int(version_match.group(1))
                if java_version >= 11:
                    log_info(f"Java version check passed: {java_version}")
                    return True
            
            log_error(f"Java 11 or higher is required. Detected: {java_output}")
            return False
            
        except Exception as e:
            log_error(f"Failed to check Java version: {e}")
            return False
    
    def download_opensearch(self) -> bool:
        """Download OpenSearch if not already present."""
        log_info(f"Downloading OpenSearch {OPENSEARCH_VERSION}...")
        
        if os.path.exists(self.opensearch_archive):
            log_warning(f"Archive {self.opensearch_archive} already exists. Skipping download.")
            return True
        
        try:
            import urllib.request
            urllib.request.urlretrieve(OPENSEARCH_DOWNLOAD_URL, self.opensearch_archive)
            log_success("OpenSearch downloaded successfully")
            return True
        except Exception as e:
            log_error(f"Failed to download OpenSearch: {e}")
            return False
    
    def extract_opensearch(self) -> bool:
        """Extract OpenSearch archive."""
        log_info("Extracting OpenSearch archive...")
        
        if os.path.exists(self.opensearch_dir):
            log_warning(f"Directory {self.opensearch_dir} already exists. Removing it...")
            shutil.rmtree(self.opensearch_dir)
        
        try:
            with tarfile.open(self.opensearch_archive, 'r:gz') as tar:
                tar.extractall()
            log_success("OpenSearch extracted successfully")
            return True
        except Exception as e:
            log_error(f"Failed to extract OpenSearch archive: {e}")
            return False
    
    def manage_plugins(self) -> bool:
        """Remove unnecessary plugins, keep only required ones."""
        log_info("Managing OpenSearch plugins...")
        
        plugins_dir = Path(self.opensearch_dir) / "plugins"
        if not plugins_dir.exists():
            log_error(f"Plugins directory not found: {plugins_dir}")
            return False
        
        keep_plugins = {"opensearch-sql", "opensearch-job-scheduler"}
        
        for plugin_dir in plugins_dir.iterdir():
            if plugin_dir.is_dir():
                plugin_name = plugin_dir.name
                if plugin_name in keep_plugins:
                    log_success(f"Keeping plugin: {plugin_name}")
                else:
                    log_warning(f"Removing plugin: {plugin_name}")
                    shutil.rmtree(plugin_dir)
        
        # Verify required plugins exist
        for required_plugin in keep_plugins:
            if not (plugins_dir / required_plugin).exists():
                log_error(f"Required plugin '{required_plugin}' not found in OpenSearch distribution")
                return False
        
        log_success("Plugin management completed")
        return True
    
    def update_jvm_options(self) -> bool:
        """Update JVM memory settings to 16GB."""
        log_info("Updating JVM options...")
        
        jvm_options_file = Path(self.opensearch_dir) / "config" / "jvm.options"
        if not jvm_options_file.exists():
            log_error(f"JVM options file not found: {jvm_options_file}")
            return False
        
        # Create backup
        backup_file = jvm_options_file.with_suffix('.options.backup')
        shutil.copy2(jvm_options_file, backup_file)
        log_info(f"Created backup: {backup_file}")
        
        # Update memory settings
        try:
            with open(jvm_options_file, 'r') as f:
                content = f.read()
            
            content = content.replace('-Xms1g', '-Xms16g')
            content = content.replace('-Xmx1g', '-Xmx16g')
            
            with open(jvm_options_file, 'w') as f:
                f.write(content)
            
            log_success("JVM options updated successfully")
            return True
        except Exception as e:
            log_error(f"Failed to update JVM options: {e}")
            return False
    
    def set_permissions(self) -> bool:
        """Set appropriate permissions for OpenSearch scripts."""
        log_info("Setting appropriate permissions...")
        
        bin_dir = Path(self.opensearch_dir) / "bin"
        if not bin_dir.exists():
            log_error(f"Bin directory not found: {bin_dir}")
            return False
        
        try:
            for script in bin_dir.iterdir():
                if script.is_file():
                    script.chmod(0o755)
            log_success("Permissions set successfully")
            return True
        except Exception as e:
            log_error(f"Failed to set permissions: {e}")
            return False
    
    def setup_opensearch(self) -> bool:
        """Complete OpenSearch setup process."""
        log_info("Starting OpenSearch setup...")
        
        steps = [
            self.check_requirements,
            self.download_opensearch,
            self.extract_opensearch,
            self.manage_plugins,
            self.update_jvm_options,
            self.set_permissions
        ]
        
        for step in steps:
            if not step():
                return False
        
        self.display_setup_summary()
        return True
    
    def display_setup_summary(self):
        """Display setup completion summary."""
        log_success("OpenSearch setup completed successfully!")
        print()
        print("Summary:")
        print(f"  - OpenSearch version: {OPENSEARCH_VERSION}")
        print(f"  - Installation directory: {self.opensearch_dir}")
        
        plugins_dir = Path(self.opensearch_dir) / "plugins"
        if plugins_dir.exists():
            print("  - Remaining plugins:")
            for plugin in plugins_dir.iterdir():
                if plugin.is_dir():
                    print(f"    - {plugin.name}")
        
        print("  - JVM heap size: 16GB (Xms16g, Xmx16g)")
        print()
        print("To start OpenSearch:")
        print(f"  cd {self.opensearch_dir}")
        print("  ./bin/opensearch")
        print()
        print("OpenSearch will be available at: http://localhost:9200")
        print("Default credentials: admin/admin")

class ClickBenchManager:
    """Manages ClickBench index preparation and data operations."""
    
    def __init__(self, opensearch_url: str = DEFAULT_OPENSEARCH_URL, index_name: str = DEFAULT_INDEX_NAME):
        self.opensearch_url = opensearch_url
        self.index_name = index_name
        self.clickbench_dir = "ClickBench"
        self.mapping_file = "elasticsearch/mapping_tuned.json"
    
    def check_requirements(self) -> bool:
        """Check system requirements for ClickBench operations."""
        log_info("Checking system requirements...")
        
        required_commands = ["git", "curl"]
        for cmd in required_commands:
            if not command_exists(cmd):
                log_error(f"Required command '{cmd}' not found. Please install it first.")
                return False
        
        log_success("System requirements check passed")
        return True
    
    def check_opensearch_connectivity(self) -> bool:
        """Check if OpenSearch is accessible."""
        log_info("Checking OpenSearch connectivity...")
        
        try:
            response = requests.get(self.opensearch_url, timeout=5)
            if response.status_code in [200, 401]:
                log_success(f"OpenSearch is accessible at {self.opensearch_url}")
                
                if response.status_code == 200:
                    cluster_info = response.json()
                    cluster_name = cluster_info.get('cluster_name', 'unknown')
                    version = cluster_info.get('version', {}).get('number', 'unknown')
                    log_info(f"Connected to OpenSearch cluster: {cluster_name} (version: {version})")
                
                return True
            else:
                log_error(f"OpenSearch returned status code: {response.status_code}")
                return False
        except Exception as e:
            log_error(f"Cannot connect to OpenSearch at {self.opensearch_url}: {e}")
            return False
    
    def clone_clickbench_repo(self) -> bool:
        """Clone or update ClickBench repository."""
        log_info("Cloning ClickBench repository...")
        
        if os.path.exists(self.clickbench_dir):
            log_warning("ClickBench directory already exists. Updating...")
            try:
                run_command(["git", "pull", "origin", "main"], cwd=self.clickbench_dir)
                log_success("ClickBench repository updated")
                return True
            except:
                log_warning("Failed to update repository. Removing and re-cloning...")
                shutil.rmtree(self.clickbench_dir)
        
        try:
            run_command(["git", "clone", CLICKBENCH_REPO, self.clickbench_dir])
            log_success("ClickBench repository cloned successfully")
            return True
        except Exception as e:
            log_error(f"Failed to clone ClickBench repository: {e}")
            return False
    
    def validate_mapping_file(self) -> bool:
        """Validate the ClickBench mapping file."""
        log_info("Validating mapping file...")
        
        mapping_path = Path(self.clickbench_dir) / self.mapping_file
        if not mapping_path.exists():
            log_error(f"Mapping file not found: {mapping_path}")
            return False
        
        try:
            with open(mapping_path, 'r') as f:
                mapping_data = json.load(f)
            
            if 'mappings' not in mapping_data:
                log_error("Mapping file missing 'mappings' section")
                return False
            
            if 'settings' not in mapping_data:
                log_warning("Mapping file missing 'settings' section")
            
            field_count = len(mapping_data['mappings'].get('properties', {}))
            log_info(f"Mapping file validated: {field_count} fields defined")
            log_success("Mapping file validation passed")
            return True
            
        except json.JSONDecodeError as e:
            log_error(f"Invalid JSON in mapping file: {e}")
            return False
        except Exception as e:
            log_error(f"Failed to validate mapping file: {e}")
            return False
    
    def index_exists(self) -> bool:
        """Check if the index exists."""
        try:
            response = requests.get(f"{self.opensearch_url}/{self.index_name}")
            return response.status_code == 200
        except:
            return False
    
    def delete_index(self) -> bool:
        """Delete existing index."""
        log_warning(f"Deleting existing index: {self.index_name}")
        
        try:
            response = requests.delete(f"{self.opensearch_url}/{self.index_name}")
            if response.status_code == 200:
                log_success("Existing index deleted successfully")
                return True
            else:
                log_error(f"Failed to delete existing index (HTTP {response.status_code})")
                return False
        except Exception as e:
            log_error(f"Failed to delete index: {e}")
            return False
    
    def create_index(self) -> bool:
        """Create index with mapping and settings."""
        log_info(f"Creating index: {self.index_name}")
        
        mapping_path = Path(self.clickbench_dir) / self.mapping_file
        
        try:
            with open(mapping_path, 'r') as f:
                mapping_data = json.load(f)
            
            response = requests.put(
                f"{self.opensearch_url}/{self.index_name}",
                headers={"Content-Type": "application/json"},
                json=mapping_data
            )
            
            if response.status_code == 200:
                log_success("Index created successfully")
                
                # Display index information
                try:
                    index_info = requests.get(f"{self.opensearch_url}/{self.index_name}").json()
                    field_count = len(index_info[self.index_name]['mappings']['properties'])
                    log_info(f"Index created with {field_count} field mappings")
                except:
                    pass
                
                return True
            else:
                log_error(f"Failed to create index (HTTP {response.status_code})")
                log_error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            log_error(f"Failed to create index: {e}")
            return False
    
    def prepare_index(self, force_recreate: bool = False) -> bool:
        """Prepare the ClickBench hits index."""
        log_info("Starting ClickBench hits index preparation...")
        
        steps = [
            self.check_requirements,
            self.check_opensearch_connectivity,
            self.clone_clickbench_repo,
            self.validate_mapping_file
        ]
        
        for step in steps:
            if not step():
                return False
        
        # Handle existing index
        if self.index_exists():
            if force_recreate:
                if not self.delete_index():
                    return False
                if not self.create_index():
                    return False
            else:
                log_warning(f"Index '{self.index_name}' already exists")
                log_info("Use --force to recreate the index")
        else:
            if not self.create_index():
                return False
        
        log_success("ClickBench hits index preparation completed!")
        return True
    
    def load_data(self, data_file: str = "hits.json.gz", bulk_size: int = DEFAULT_BULK_SIZE) -> bool:
        """Load ClickBench data into the index."""
        log_info(f"Loading data into OpenSearch at {self.opensearch_url}")
        log_info(f"Target index: {self.index_name}")
        log_info(f"Batch size: {bulk_size}")
        log_info(f"Expected total records: {TOTAL_RECORDS:,}")
        print("-" * 50)
        
        if not os.path.exists(data_file):
            log_error(f"Data file not found: {data_file}")
            log_error("Please ensure the ClickBench data file is in the current directory.")
            log_error("You can download it from: https://datasets.clickhouse.com/hits/tsv/hits.tsv.gz")
            return False
        
        # Prepare bulk request components
        action_meta_line = json.dumps({"index": {"_index": self.index_name}}) + "\n"
        
        session = requests.Session()
        session.headers.update({
            "Content-Type": "application/x-ndjson",
            "Authorization": "Basic " + base64.b64encode(b"admin:admin").decode()
        })
        
        # Test connection
        try:
            test_resp = session.get(self.opensearch_url, timeout=5)
            if test_resp.status_code == 200:
                cluster_info = test_resp.json()
                log_info(f"Connected to: {cluster_info.get('cluster_name', 'unknown')} "
                         f"(version: {cluster_info.get('version', {}).get('number', 'unknown')})")
        except Exception as e:
            log_warning(f"Could not connect to OpenSearch: {e}")
            log_info("Continuing anyway...")
        
        total_docs = 0
        batch_num = 0
        
        try:
            with gzip.open(data_file, mode="rt", encoding="utf-8") as f:
                log_info(f"Reading from {data_file}")
                
                while True:
                    docs = list(islice(f, bulk_size))
                    if not docs:
                        break
                    
                    batch_num += 1
                    
                    # Build bulk request body
                    bulk_data = ""
                    for doc in docs:
                        bulk_data += action_meta_line
                        bulk_data += doc.strip() + "\n"
                    
                    # Send bulk request
                    try:
                        resp = session.post(
                            f"{self.opensearch_url}/_bulk",
                            data=bulk_data.encode("utf-8"),
                            timeout=30
                        )
                        
                        if resp.status_code >= 300:
                            log_warning(f"Batch {batch_num} ({len(docs)} docs) - Warning: HTTP {resp.status_code}")
                            log_warning(f"Response: {resp.text[:500]}")
                        else:
                            try:
                                body = resp.json()
                                if body.get("errors"):
                                    items = body.get("items", [])
                                    err_count = sum(1 for i in items if "error" in i.get("index", {}))
                                    if err_count:
                                        log_warning(f"Batch {batch_num}: {err_count} item errors")
                            except json.JSONDecodeError:
                                log_warning(f"Batch {batch_num}: Could not parse response as JSON")
                        
                        total_docs += len(docs)
                        pct = (total_docs / TOTAL_RECORDS) * 100 if TOTAL_RECORDS else 0
                        print(f"\rProgress: {pct:.2f}% ({total_docs:,}/{TOTAL_RECORDS:,}) - Batch {batch_num}", 
                              end="", flush=True)
                        
                        if batch_num % 10 == 0:
                            print()
                            
                    except Exception as e:
                        log_error(f"Failed to send batch {batch_num}: {e}")
                        return False
        
        except Exception as e:
            log_error(f"Error reading data file: {e}")
            return False
        
        print(f"\n\nCompleted!")
        print(f"Total documents sent: {total_docs:,}")
        
        # Verify the index
        try:
            count_resp = session.get(f"{self.opensearch_url}/{self.index_name}/_count", timeout=10)
            if count_resp.status_code == 200:
                count_data = count_resp.json()
                indexed_count = count_data.get("count", 0)
                print(f"Documents in index: {indexed_count:,}")
                if indexed_count != total_docs:
                    log_warning(f"Mismatch between sent ({total_docs:,}) and indexed ({indexed_count:,}) documents")
            else:
                log_warning(f"Could not verify index count (HTTP {count_resp.status_code})")
        except Exception as e:
            log_warning(f"Could not verify index: {e}")
        
        return True

class SnapshotManager:
    """Manages OpenSearch snapshots for ClickBench data."""
    
    def __init__(self, opensearch_url: str = DEFAULT_OPENSEARCH_URL, 
                 repo_name: str = DEFAULT_SNAPSHOT_REPO, index_name: str = DEFAULT_INDEX_NAME):
        self.opensearch_url = opensearch_url
        self.repo_name = repo_name
        self.index_name = index_name
    
    def check_opensearch_connectivity(self) -> bool:
        """Check if OpenSearch is accessible."""
        try:
            response = requests.get(self.opensearch_url, timeout=5)
            return response.status_code in [200, 401]
        except:
            return False
    
    def repository_exists(self) -> bool:
        """Check if snapshot repository exists."""
        try:
            response = requests.get(f"{self.opensearch_url}/_snapshot/{self.repo_name}")
            return response.status_code == 200
        except:
            return False
    
    def create_repository(self, backup_dir: str) -> bool:
        """Create snapshot repository."""
        log_info(f"Creating snapshot repository: {self.repo_name}")
        
        # Ensure backup directory exists
        os.makedirs(backup_dir, exist_ok=True)
        backup_dir = os.path.abspath(backup_dir)
        
        repo_config = {
            "type": "fs",
            "settings": {
                "location": backup_dir,
                "compress": True,
                "chunk_size": "1gb",
                "max_restore_bytes_per_sec": "40mb",
                "max_snapshot_bytes_per_sec": "40mb"
            }
        }
        
        try:
            response = requests.put(
                f"{self.opensearch_url}/_snapshot/{self.repo_name}",
                headers={"Content-Type": "application/json"},
                json=repo_config
            )
            
            if response.status_code == 200:
                log_success("Snapshot repository created successfully")
                return True
            else:
                log_error(f"Failed to create snapshot repository (HTTP {response.status_code})")
                log_error(f"Response: {response.text}")
                
                if "path.repo" in response.text:
                    log_error("")
                    log_error("OpenSearch path.repo configuration issue detected!")
                    log_error("You need to configure OpenSearch to allow filesystem snapshots:")
                    log_error("1. Stop OpenSearch if it's running")
                    log_error("2. Edit opensearch.yml configuration file and add:")
                    log_error(f"   path.repo: [\"{backup_dir}\"]")
                    log_error("3. Restart OpenSearch")
                
                return False
                
        except Exception as e:
            log_error(f"Failed to create repository: {e}")
            return False
    
    def create_snapshot(self, snapshot_name: str) -> bool:
        """Create a snapshot of the index."""
        log_info(f"Creating snapshot: {snapshot_name}")
        
        snapshot_config = {
            "indices": self.index_name,
            "ignore_unavailable": False,
            "include_global_state": False,
            "metadata": {
                "taken_by": "clickbench_manager.py",
                "taken_because": "Manual backup of hits index for ClickBench",
                "creation_date": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
            }
        }
        
        try:
            response = requests.put(
                f"{self.opensearch_url}/_snapshot/{self.repo_name}/{snapshot_name}?wait_for_completion=false",
                headers={"Content-Type": "application/json"},
                json=snapshot_config
            )
            
            if response.status_code == 200:
                log_success("Snapshot creation initiated successfully")
                return True
            else:
                log_error(f"Failed to create snapshot (HTTP {response.status_code})")
                log_error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            log_error(f"Failed to create snapshot: {e}")
            return False
    
    def monitor_snapshot(self, snapshot_name: str, timeout: int = 300) -> bool:
        """Monitor snapshot progress."""
        log_info("Monitoring snapshot progress...")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{self.opensearch_url}/_snapshot/{self.repo_name}/{snapshot_name}")
                if response.status_code == 200:
                    snapshot_info = response.json()
                    if snapshot_info.get("snapshots"):
                        state = snapshot_info["snapshots"][0].get("state", "UNKNOWN")
                        
                        if state == "SUCCESS":
                            log_success("Snapshot completed successfully!")
                            return True
                        elif state == "FAILED":
                            log_error("Snapshot failed!")
                            return False
                        elif state == "IN_PROGRESS":
                            log_info("Snapshot in progress...")
                        else:
                            log_info(f"Snapshot state: {state}")
                
                time.sleep(5)
                
            except Exception as e:
                log_warning(f"Error checking snapshot status: {e}")
                time.sleep(5)
        
        log_warning("Snapshot monitoring timed out")
        return False
    
    def list_snapshots(self) -> List[Dict]:
        """List all snapshots in the repository."""
        try:
            response = requests.get(f"{self.opensearch_url}/_snapshot/{self.repo_name}/_all")
            if response.status_code == 200:
                return response.json().get("snapshots", [])
            else:
                log_error(f"Failed to list snapshots (HTTP {response.status_code})")
                return []
        except Exception as e:
            log_error(f"Failed to list snapshots: {e}")
            return []
    
    def restore_snapshot(self, snapshot_name: str, target_index: Optional[str] = None, 
                        wait_for_completion: bool = True) -> bool:
        """Restore a snapshot."""
        target_index = target_index or self.index_name
        log_info(f"Restoring snapshot: {snapshot_name} to index: {target_index}")
        
        restore_config = {
            "indices": self.index_name,
            "ignore_unavailable": False,
            "include_global_state": False,
            "include_aliases": True
        }
        
        if target_index != self.index_name:
            restore_config.update({
                "rename_pattern": self.index_name,
                "rename_replacement": target_index,
                "include_aliases": False
            })
        
        wait_param = "?wait_for_completion=true" if wait_for_completion else ""
        
        try:
            response = requests.post(
                f"{self.opensearch_url}/_snapshot/{self.repo_name}/{snapshot_name}/_restore{wait_param}",
                headers={"Content-Type": "application/json"},
                json=restore_config
            )
            
            if response.status_code == 200:
                log_success("Restore completed successfully" if wait_for_completion else "Restore initiated successfully")
                return True
            else:
                log_error(f"Failed to restore snapshot (HTTP {response.status_code})")
                log_error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            log_error(f"Failed to restore snapshot: {e}")
            return False

def main():
    """Main function to handle command line arguments and execute operations."""
    parser = argparse.ArgumentParser(
        description="ClickBench Manager - Consolidated OpenSearch ClickBench Management Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Setup OpenSearch
  %(prog)s setup-opensearch
  
  # Prepare ClickBench index
  %(prog)s prepare-index
  
  # Load data into index
  %(prog)s load-data --data-file hits.json.gz
  
  # Create snapshot
  %(prog)s create-snapshot --snapshot-name my_snapshot
  
  # List snapshots
  %(prog)s list-snapshots
  
  # Restore snapshot
  %(prog)s restore-snapshot --snapshot-name my_snapshot
  
  # Monitor snapshot progress
  %(prog)s monitor-snapshot --snapshot-name my_snapshot
        """
    )
    
    # Global options
    parser.add_argument('--url', default=DEFAULT_OPENSEARCH_URL,
                       help=f'OpenSearch URL (default: {DEFAULT_OPENSEARCH_URL})')
    parser.add_argument('--index', default=DEFAULT_INDEX_NAME,
                       help=f'Index name (default: {DEFAULT_INDEX_NAME})')
    parser.add_argument('--repo', default=DEFAULT_SNAPSHOT_REPO,
                       help=f'Snapshot repository name (default: {DEFAULT_SNAPSHOT_REPO})')
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Setup OpenSearch command
    setup_parser = subparsers.add_parser('setup-opensearch', help='Download and setup OpenSearch')
    
    # Prepare index command
    prepare_parser = subparsers.add_parser('prepare-index', help='Prepare ClickBench hits index')
    prepare_parser.add_argument('--force', action='store_true',
                               help='Force recreation of index if it exists')
    
    # Load data command
    load_parser = subparsers.add_parser('load-data', help='Load ClickBench data into index')
    load_parser.add_argument('--data-file', default='hits.json.gz',
                            help='Data file to load (default: hits.json.gz)')
    load_parser.add_argument('--bulk-size', type=int, default=DEFAULT_BULK_SIZE,
                            help=f'Bulk request size (default: {DEFAULT_BULK_SIZE})')
    
    # Snapshot commands
    snapshot_parser = subparsers.add_parser('create-snapshot', help='Create snapshot of index')
    snapshot_parser.add_argument('--snapshot-name', required=True,
                                help='Name for the snapshot')
    snapshot_parser.add_argument('--backup-dir', default='./snapshots',
                                help='Backup directory (default: ./snapshots)')
    snapshot_parser.add_argument('--monitor', action='store_true',
                                help='Monitor snapshot progress')
    
    # List snapshots command
    list_parser = subparsers.add_parser('list-snapshots', help='List available snapshots')
    
    # Restore snapshot command
    restore_parser = subparsers.add_parser('restore-snapshot', help='Restore snapshot')
    restore_parser.add_argument('--snapshot-name', required=True,
                               help='Name of snapshot to restore')
    restore_parser.add_argument('--target-index',
                               help='Target index name (default: same as source)')
    restore_parser.add_argument('--force', action='store_true',
                               help='Force restore (delete existing index)')
    restore_parser.add_argument('--async', dest='async_restore', action='store_true',
                               help='Restore asynchronously')
    
    # Monitor snapshot command
    monitor_parser = subparsers.add_parser('monitor-snapshot', help='Monitor snapshot progress')
    monitor_parser.add_argument('--snapshot-name', required=True,
                               help='Name of snapshot to monitor')
    
    # Register repository command
    register_parser = subparsers.add_parser('register-repo', help='Register snapshot repository')
    register_parser.add_argument('--backup-dir', required=True,
                                help='Backup directory path')
    register_parser.add_argument('--force', action='store_true',
                                help='Force re-registration')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show OpenSearch and index status')
    
    args = parser.parse_args()
    
    # If no command specified, show help
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        # Execute commands
        if args.command == 'setup-opensearch':
            manager = OpenSearchManager(args.url)
            success = manager.setup_opensearch()
            return 0 if success else 1
            
        elif args.command == 'prepare-index':
            manager = ClickBenchManager(args.url, args.index)
            success = manager.prepare_index(args.force)
            return 0 if success else 1
            
        elif args.command == 'load-data':
            manager = ClickBenchManager(args.url, args.index)
            success = manager.load_data(args.data_file, args.bulk_size)
            return 0 if success else 1
            
        elif args.command == 'create-snapshot':
            snapshot_manager = SnapshotManager(args.url, args.repo, args.index)
            
            if not snapshot_manager.check_opensearch_connectivity():
                log_error("Cannot connect to OpenSearch")
                return 1
            
            # Create repository if it doesn't exist
            if not snapshot_manager.repository_exists():
                if not snapshot_manager.create_repository(args.backup_dir):
                    return 1
            
            # Create snapshot
            if not snapshot_manager.create_snapshot(args.snapshot_name):
                return 1
            
            # Monitor if requested
            if args.monitor:
                snapshot_manager.monitor_snapshot(args.snapshot_name)
            
            return 0
            
        elif args.command == 'list-snapshots':
            snapshot_manager = SnapshotManager(args.url, args.repo, args.index)
            
            if not snapshot_manager.check_opensearch_connectivity():
                log_error("Cannot connect to OpenSearch")
                return 1
            
            if not snapshot_manager.repository_exists():
                log_error(f"Repository '{args.repo}' does not exist")
                return 1
            
            snapshots = snapshot_manager.list_snapshots()
            if snapshots:
                print(f"\nSnapshots in repository '{args.repo}':")
                print("=" * 50)
                for snapshot in snapshots:
                    state = snapshot.get('state', 'UNKNOWN')
                    name = snapshot.get('snapshot', 'unknown')
                    start_time = snapshot.get('start_time', 'unknown')
                    
                    if state == 'SUCCESS':
                        print(f"  ✓ {name} - {state} - {start_time}")
                    elif state == 'FAILED':
                        print(f"  ✗ {name} - {state} - {start_time}")
                    elif state == 'IN_PROGRESS':
                        print(f"  ⏳ {name} - {state} - {start_time}")
                    else:
                        print(f"  ? {name} - {state} - {start_time}")
                print()
            else:
                log_info("No snapshots found")
            
            return 0
            
        elif args.command == 'restore-snapshot':
            snapshot_manager = SnapshotManager(args.url, args.repo, args.index)
            
            if not snapshot_manager.check_opensearch_connectivity():
                log_error("Cannot connect to OpenSearch")
                return 1
            
            if not snapshot_manager.repository_exists():
                log_error(f"Repository '{args.repo}' does not exist")
                return 1
            
            # Check if target index exists and handle force option
            target_index = args.target_index or args.index
            if args.force:
                try:
                    response = requests.get(f"{args.url}/{target_index}")
                    if response.status_code == 200:
                        log_warning(f"Deleting existing index: {target_index}")
                        requests.delete(f"{args.url}/{target_index}")
                except:
                    pass
            
            success = snapshot_manager.restore_snapshot(
                args.snapshot_name, 
                target_index, 
                wait_for_completion=not args.async_restore
            )
            return 0 if success else 1
            
        elif args.command == 'monitor-snapshot':
            snapshot_manager = SnapshotManager(args.url, args.repo, args.index)
            
            if not snapshot_manager.check_opensearch_connectivity():
                log_error("Cannot connect to OpenSearch")
                return 1
            
            success = snapshot_manager.monitor_snapshot(args.snapshot_name)
            return 0 if success else 1
            
        elif args.command == 'register-repo':
            snapshot_manager = SnapshotManager(args.url, args.repo, args.index)
            
            if not snapshot_manager.check_opensearch_connectivity():
                log_error("Cannot connect to OpenSearch")
                return 1
            
            if snapshot_manager.repository_exists() and not args.force:
                log_warning(f"Repository '{args.repo}' already exists. Use --force to re-register.")
                return 1
            
            success = snapshot_manager.create_repository(args.backup_dir)
            return 0 if success else 1
            
        elif args.command == 'status':
            # Show OpenSearch status
            try:
                response = requests.get(args.url, timeout=5)
                if response.status_code == 200:
                    cluster_info = response.json()
                    log_success(f"OpenSearch is running at {args.url}")
                    print(f"  Cluster: {cluster_info.get('cluster_name', 'unknown')}")
                    print(f"  Version: {cluster_info.get('version', {}).get('number', 'unknown')}")
                else:
                    log_error(f"OpenSearch returned status {response.status_code}")
                    return 1
            except Exception as e:
                log_error(f"Cannot connect to OpenSearch: {e}")
                return 1
            
            # Show index status
            try:
                response = requests.get(f"{args.url}/{args.index}")
                if response.status_code == 200:
                    log_success(f"Index '{args.index}' exists")
                    
                    # Get document count
                    count_resp = requests.get(f"{args.url}/{args.index}/_count")
                    if count_resp.status_code == 200:
                        count = count_resp.json().get('count', 0)
                        print(f"  Documents: {count:,}")
                    
                    # Get index size
                    stats_resp = requests.get(f"{args.url}/{args.index}/_stats")
                    if stats_resp.status_code == 200:
                        stats = stats_resp.json()
                        size_bytes = stats.get('indices', {}).get(args.index, {}).get('total', {}).get('store', {}).get('size_in_bytes', 0)
                        size_mb = size_bytes // (1024 * 1024)
                        print(f"  Size: {size_mb} MB")
                else:
                    log_warning(f"Index '{args.index}' does not exist")
            except Exception as e:
                log_error(f"Error checking index status: {e}")
            
            return 0
            
        else:
            log_error(f"Unknown command: {args.command}")
            return 1
            
    except KeyboardInterrupt:
        log_warning("Operation cancelled by user")
        return 1
    except Exception as e:
        log_error(f"Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
