#!/bin/bash

# ClickBench Hits Index Snapshot Script
# This script creates a snapshot of the hits index from OpenSearch to local file system
# Author: Generated for BusyBox project
# Date: $(date)

set -e  # Exit on any error

# Configuration
OPENSEARCH_URL="http://localhost:9200"
INDEX_NAME="hits"
SNAPSHOT_REPO="hits_backup"
SNAPSHOT_NAME="hits_snapshot_$(date +%Y%m%d_%H%M%S)"
BACKUP_DIR="./snapshots"
REPOSITORY_TYPE="fs"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check system requirements
check_requirements() {
    log_info "Checking system requirements..."
    
    # Check for required commands
    local required_commands=("curl" "jq")
    for cmd in "${required_commands[@]}"; do
        if ! command_exists "$cmd"; then
            log_error "Required command '$cmd' not found. Please install it first."
            if [[ "$cmd" == "jq" ]]; then
                log_info "To install jq:"
                log_info "  macOS: brew install jq"
                log_info "  Ubuntu/Debian: sudo apt-get install jq"
                log_info "  CentOS/RHEL: sudo yum install jq"
            fi
            exit 1
        fi
    done
    
    log_success "System requirements check passed"
}

# Function to check OpenSearch connectivity
check_opensearch() {
    log_info "Checking OpenSearch connectivity..."
    
    local response_code=$(curl -s -o /dev/null -w "%{http_code}" "$OPENSEARCH_URL" || echo "000")
    
    if [[ "$response_code" == "200" || "$response_code" == "401" ]]; then
        log_success "OpenSearch is accessible at $OPENSEARCH_URL"
        
        # Try to get cluster info
        local cluster_info=$(curl -s "$OPENSEARCH_URL" 2>/dev/null || echo "")
        if [[ -n "$cluster_info" ]]; then
            local cluster_name=$(echo "$cluster_info" | jq -r '.cluster_name // "unknown"' 2>/dev/null || echo "unknown")
            local version=$(echo "$cluster_info" | jq -r '.version.number // "unknown"' 2>/dev/null || echo "unknown")
            log_info "Connected to OpenSearch cluster: $cluster_name (version: $version)"
        fi
    else
        log_error "Cannot connect to OpenSearch at $OPENSEARCH_URL"
        log_error "Please ensure OpenSearch is running and accessible"
        log_info "You can start OpenSearch with: cd opensearch-3.2.0 && ./bin/opensearch"
        exit 1
    fi
}

# Function to check if index exists
check_index_exists() {
    log_info "Checking if index '$INDEX_NAME' exists..."
    
    local response_code=$(curl -s -o /dev/null -w "%{http_code}" "$OPENSEARCH_URL/$INDEX_NAME" || echo "000")
    
    if [[ "$response_code" == "200" ]]; then
        log_success "Index '$INDEX_NAME' found"
        
        # Get index stats
        local index_stats=$(curl -s "$OPENSEARCH_URL/$INDEX_NAME/_stats" 2>/dev/null || echo "")
        if [[ -n "$index_stats" ]]; then
            local doc_count=$(echo "$index_stats" | jq -r ".indices[\"$INDEX_NAME\"].total.docs.count // 0" 2>/dev/null || echo "0")
            local size_bytes=$(echo "$index_stats" | jq -r ".indices[\"$INDEX_NAME\"].total.store.size_in_bytes // 0" 2>/dev/null || echo "0")
            local size_mb=$((size_bytes / 1024 / 1024))
            log_info "Index contains $doc_count documents (~${size_mb}MB)"
        fi
    else
        log_error "Index '$INDEX_NAME' not found (HTTP $response_code)"
        log_error "Please ensure the hits index exists before creating a snapshot"
        log_info "You can create the index using: ./prepare_hits.sh"
        exit 1
    fi
}

# Function to create backup directory
create_backup_directory() {
    log_info "Creating backup directory: $BACKUP_DIR"
    
    # Create absolute path for backup directory
    local abs_backup_dir=$(realpath "$BACKUP_DIR" 2>/dev/null || echo "$(pwd)/$BACKUP_DIR")
    
    if [[ ! -d "$abs_backup_dir" ]]; then
        if ! mkdir -p "$abs_backup_dir"; then
            log_error "Failed to create backup directory: $abs_backup_dir"
            exit 1
        fi
        log_success "Backup directory created: $abs_backup_dir"
    else
        log_info "Backup directory already exists: $abs_backup_dir"
    fi
    
    # Update BACKUP_DIR to absolute path
    BACKUP_DIR="$abs_backup_dir"
    
    # Check write permissions
    if [[ ! -w "$BACKUP_DIR" ]]; then
        log_error "No write permission for backup directory: $BACKUP_DIR"
        exit 1
    fi
}

# Function to check if repository exists
repository_exists() {
    local response_code=$(curl -s -o /dev/null -w "%{http_code}" "$OPENSEARCH_URL/_snapshot/$SNAPSHOT_REPO" || echo "000")
    [[ "$response_code" == "200" ]]
}

# Function to create snapshot repository
create_snapshot_repository() {
    log_info "Creating snapshot repository: $SNAPSHOT_REPO"
    
    # Repository configuration
    local repo_config=$(cat <<EOF
{
  "type": "$REPOSITORY_TYPE",
  "settings": {
    "location": "$BACKUP_DIR",
    "compress": true,
    "chunk_size": "1gb",
    "max_restore_bytes_per_sec": "40mb",
    "max_snapshot_bytes_per_sec": "40mb"
  }
}
EOF
)
    
    local response=$(curl -s -X PUT \
        -H "Content-Type: application/json" \
        -d "$repo_config" \
        "$OPENSEARCH_URL/_snapshot/$SNAPSHOT_REPO")
    
    local response_code=$(curl -s -o /dev/null -w "%{http_code}" -X PUT \
        -H "Content-Type: application/json" \
        -d "$repo_config" \
        "$OPENSEARCH_URL/_snapshot/$SNAPSHOT_REPO")
    
    if [[ "$response_code" == "200" ]]; then
        log_success "Snapshot repository created successfully"
    else
        log_error "Failed to create snapshot repository (HTTP $response_code)"
        log_error "Response: $response"
        
        # Check if it's a path.repo configuration issue
        if echo "$response" | grep -q "path.repo"; then
            log_error ""
            log_error "OpenSearch path.repo configuration issue detected!"
            log_error ""
            log_error "To fix this, you need to configure OpenSearch to allow filesystem snapshots:"
            log_error ""
            log_error "1. Stop OpenSearch if it's running"
            log_error "2. Edit opensearch.yml configuration file and add:"
            log_error "   path.repo: [\"$BACKUP_DIR\"]"
            log_error ""
            log_error "3. Alternative: Add to opensearch.yml:"
            log_error "   path.repo: [\"/tmp/snapshots\", \"$BACKUP_DIR\"]"
            log_error ""
            log_error "4. Restart OpenSearch"
            log_error ""
            log_error "Example opensearch.yml entry:"
            log_error "# Snapshot repository paths"
            log_error "path.repo: [\"$BACKUP_DIR\"]"
            log_error ""
            log_error "For OpenSearch 3.2.0 setup, the config file is typically at:"
            log_error "opensearch-3.2.0/config/opensearch.yml"
        fi
        
        exit 1
    fi
}

# Function to create snapshot
create_snapshot() {
    log_info "Creating snapshot: $SNAPSHOT_NAME"
    
    # Snapshot configuration
    local snapshot_config=$(cat <<EOF
{
  "indices": "$INDEX_NAME",
  "ignore_unavailable": false,
  "include_global_state": false,
  "metadata": {
    "taken_by": "snapshot_hits.sh",
    "taken_because": "Manual backup of hits index for ClickBench",
    "creation_date": "$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)"
  }
}
EOF
)
    
    local response=$(curl -s -X PUT \
        -H "Content-Type: application/json" \
        -d "$snapshot_config" \
        "$OPENSEARCH_URL/_snapshot/$SNAPSHOT_REPO/$SNAPSHOT_NAME?wait_for_completion=false")
    
    local response_code=$(curl -s -o /dev/null -w "%{http_code}" -X PUT \
        -H "Content-Type: application/json" \
        -d "$snapshot_config" \
        "$OPENSEARCH_URL/_snapshot/$SNAPSHOT_REPO/$SNAPSHOT_NAME?wait_for_completion=false")
    
    if [[ "$response_code" == "200" ]]; then
        log_success "Snapshot creation initiated successfully"
        
        # Check if response contains accepted status
        local accepted=$(echo "$response" | jq -r '.accepted // false' 2>/dev/null || echo "false")
        if [[ "$accepted" == "true" ]]; then
            log_info "Snapshot is being created asynchronously"
        fi
    else
        log_error "Failed to create snapshot (HTTP $response_code)"
        log_error "Response: $response"
        exit 1
    fi
}

# Function to monitor snapshot progress
monitor_snapshot_progress() {
    log_info "Monitoring snapshot progress..."
    
    local max_attempts=60  # 5 minutes with 5-second intervals
    local attempt=0
    
    while [[ $attempt -lt $max_attempts ]]; do
        local snapshot_status=$(curl -s "$OPENSEARCH_URL/_snapshot/$SNAPSHOT_REPO/$SNAPSHOT_NAME" 2>/dev/null || echo "")
        
        if [[ -n "$snapshot_status" ]]; then
            local state=$(echo "$snapshot_status" | jq -r ".snapshots[0].state // \"UNKNOWN\"" 2>/dev/null || echo "UNKNOWN")
            local progress=$(echo "$snapshot_status" | jq -r ".snapshots[0].stats.total.size_in_bytes // 0" 2>/dev/null || echo "0")
            
            case "$state" in
                "SUCCESS")
                    log_success "Snapshot completed successfully!"
                    
                    # Display snapshot details
                    local start_time=$(echo "$snapshot_status" | jq -r ".snapshots[0].start_time // \"unknown\"" 2>/dev/null || echo "unknown")
                    local end_time=$(echo "$snapshot_status" | jq -r ".snapshots[0].end_time // \"unknown\"" 2>/dev/null || echo "unknown")
                    local duration=$(echo "$snapshot_status" | jq -r ".snapshots[0].duration_in_millis // 0" 2>/dev/null || echo "0")
                    local duration_sec=$((duration / 1000))
                    local size_bytes=$(echo "$snapshot_status" | jq -r ".snapshots[0].stats.total.size_in_bytes // 0" 2>/dev/null || echo "0")
                    local size_mb=$((size_bytes / 1024 / 1024))
                    
                    log_info "Snapshot details:"
                    log_info "  - Start time: $start_time"
                    log_info "  - End time: $end_time"
                    log_info "  - Duration: ${duration_sec} seconds"
                    log_info "  - Size: ${size_mb}MB"
                    
                    return 0
                    ;;
                "IN_PROGRESS")
                    log_info "Snapshot in progress... (attempt $((attempt + 1))/$max_attempts)"
                    ;;
                "PARTIAL")
                    log_warning "Snapshot completed with partial success"
                    local failures=$(echo "$snapshot_status" | jq -r ".snapshots[0].failures // []" 2>/dev/null || echo "[]")
                    if [[ "$failures" != "[]" ]]; then
                        log_warning "Failures: $failures"
                    fi
                    return 0
                    ;;
                "FAILED")
                    log_error "Snapshot failed!"
                    local failures=$(echo "$snapshot_status" | jq -r ".snapshots[0].failures // []" 2>/dev/null || echo "[]")
                    if [[ "$failures" != "[]" ]]; then
                        log_error "Failures: $failures"
                    fi
                    return 1
                    ;;
                *)
                    log_info "Snapshot state: $state (attempt $((attempt + 1))/$max_attempts)"
                    ;;
            esac
        else
            log_warning "Could not retrieve snapshot status (attempt $((attempt + 1))/$max_attempts)"
        fi
        
        sleep 5
        ((attempt++))
    done
    
    log_warning "Snapshot monitoring timed out after $((max_attempts * 5)) seconds"
    log_info "You can check snapshot status manually with:"
    log_info "curl '$OPENSEARCH_URL/_snapshot/$SNAPSHOT_REPO/$SNAPSHOT_NAME'"
    
    return 0
}

# Function to list snapshots
list_snapshots() {
    log_info "Listing existing snapshots in repository..."
    
    local snapshots=$(curl -s "$OPENSEARCH_URL/_snapshot/$SNAPSHOT_REPO/_all" 2>/dev/null || echo "")
    
    if [[ -n "$snapshots" ]]; then
        local snapshot_count=$(echo "$snapshots" | jq '.snapshots | length' 2>/dev/null || echo "0")
        
        if [[ "$snapshot_count" -gt 0 ]]; then
            log_info "Found $snapshot_count snapshot(s):"
            echo "$snapshots" | jq -r '.snapshots[] | "  - \(.snapshot) (\(.state)) - \(.start_time)"' 2>/dev/null || echo "  Could not parse snapshot list"
        else
            log_info "No snapshots found in repository"
        fi
    else
        log_warning "Could not retrieve snapshot list"
    fi
}

# Function to verify snapshot files
verify_snapshot_files() {
    log_info "Verifying snapshot files in backup directory..."
    
    if [[ -d "$BACKUP_DIR" ]]; then
        local file_count=$(find "$BACKUP_DIR" -type f | wc -l)
        local total_size=$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1 || echo "unknown")
        
        log_info "Backup directory contents:"
        log_info "  - Location: $BACKUP_DIR"
        log_info "  - Files: $file_count"
        log_info "  - Total size: $total_size"
        
        # List some key files
        if [[ $file_count -gt 0 ]]; then
            log_info "Key files:"
            find "$BACKUP_DIR" -name "index-*" -o -name "meta-*" -o -name "snap-*" | head -5 | while read -r file; do
                local filename=$(basename "$file")
                local filesize=$(ls -lh "$file" 2>/dev/null | awk '{print $5}' || echo "unknown")
                log_info "    $filename ($filesize)"
            done
            
            if [[ $file_count -gt 5 ]]; then
                log_info "    ... and $((file_count - 5)) more files"
            fi
        fi
    else
        log_error "Backup directory not found: $BACKUP_DIR"
    fi
}

# Function to display usage information
display_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "  -u, --url URL       OpenSearch URL (default: $OPENSEARCH_URL)"
    echo "  -i, --index NAME    Index name to snapshot (default: $INDEX_NAME)"
    echo "  -r, --repo NAME     Snapshot repository name (default: $SNAPSHOT_REPO)"
    echo "  -d, --dir PATH      Backup directory path (default: $BACKUP_DIR)"
    echo "  -n, --name NAME     Snapshot name (default: auto-generated with timestamp)"
    echo "  -l, --list          List existing snapshots and exit"
    echo "  -h, --help          Show this help message"
    echo
    echo "Examples:"
    echo "  $0                                    # Create snapshot with default settings"
    echo "  $0 --dir /backup/opensearch          # Use custom backup directory"
    echo "  $0 --name my_hits_backup             # Use custom snapshot name"
    echo "  $0 --list                            # List existing snapshots"
}

# Function to display summary
display_summary() {
    log_success "Hits index snapshot completed!"
    echo
    echo "Summary:"
    echo "  - OpenSearch URL: $OPENSEARCH_URL"
    echo "  - Index: $INDEX_NAME"
    echo "  - Repository: $SNAPSHOT_REPO"
    echo "  - Snapshot: $SNAPSHOT_NAME"
    echo "  - Backup location: $BACKUP_DIR"
    echo
    echo "Useful commands:"
    echo "  # List all snapshots"
    echo "  curl '$OPENSEARCH_URL/_snapshot/$SNAPSHOT_REPO/_all?pretty'"
    echo
    echo "  # Check snapshot status"
    echo "  curl '$OPENSEARCH_URL/_snapshot/$SNAPSHOT_REPO/$SNAPSHOT_NAME?pretty'"
    echo
    echo "  # Restore snapshot (example)"
    echo "  curl -X POST '$OPENSEARCH_URL/_snapshot/$SNAPSHOT_REPO/$SNAPSHOT_NAME/_restore' \\"
    echo "       -H 'Content-Type: application/json' \\"
    echo "       -d '{\"indices\": \"$INDEX_NAME\", \"rename_pattern\": \"$INDEX_NAME\", \"rename_replacement\": \"${INDEX_NAME}_restored\"}'"
    echo
    echo "  # Delete snapshot"
    echo "  curl -X DELETE '$OPENSEARCH_URL/_snapshot/$SNAPSHOT_REPO/$SNAPSHOT_NAME'"
}

# Function to cleanup on error
cleanup_on_error() {
    log_error "Script failed. Cleaning up..."
    
    # Optionally clean up partial snapshots
    if [[ -n "$SNAPSHOT_NAME" ]]; then
        log_info "Checking for partial snapshot to clean up..."
        local snapshot_status=$(curl -s "$OPENSEARCH_URL/_snapshot/$SNAPSHOT_REPO/$SNAPSHOT_NAME" 2>/dev/null || echo "")
        local state=$(echo "$snapshot_status" | jq -r ".snapshots[0].state // \"UNKNOWN\"" 2>/dev/null || echo "UNKNOWN")
        
        if [[ "$state" == "FAILED" || "$state" == "PARTIAL" ]]; then
            log_warning "Cleaning up failed/partial snapshot: $SNAPSHOT_NAME"
            curl -s -X DELETE "$OPENSEARCH_URL/_snapshot/$SNAPSHOT_REPO/$SNAPSHOT_NAME" >/dev/null 2>&1 || true
        fi
    fi
}

# Parse command line arguments
LIST_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -u|--url)
            OPENSEARCH_URL="$2"
            shift 2
            ;;
        -i|--index)
            INDEX_NAME="$2"
            shift 2
            ;;
        -r|--repo)
            SNAPSHOT_REPO="$2"
            shift 2
            ;;
        -d|--dir)
            BACKUP_DIR="$2"
            shift 2
            ;;
        -n|--name)
            SNAPSHOT_NAME="$2"
            shift 2
            ;;
        -l|--list)
            LIST_ONLY=true
            shift
            ;;
        -h|--help)
            display_usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            display_usage
            exit 1
            ;;
    esac
done

# Main execution
main() {
    log_info "Starting ClickBench hits index snapshot..."
    
    # Set trap for cleanup on error
    trap cleanup_on_error ERR
    
    check_requirements
    check_opensearch
    
    # Handle list-only mode
    if [[ "$LIST_ONLY" == true ]]; then
        if repository_exists; then
            list_snapshots
        else
            log_info "Snapshot repository '$SNAPSHOT_REPO' does not exist"
            log_info "Create a snapshot first to initialize the repository"
        fi
        exit 0
    fi
    
    check_index_exists
    create_backup_directory
    
    # Create repository if it doesn't exist
    if ! repository_exists; then
        create_snapshot_repository
    else
        log_info "Using existing snapshot repository: $SNAPSHOT_REPO"
    fi
    
    create_snapshot
    monitor_snapshot_progress
    verify_snapshot_files
    list_snapshots
    display_summary
    
    log_success "Script completed successfully!"
}

# Run main function
main "$@"
