#!/bin/bash

# ClickBench Hits Index Preparation Script
# This script clones the ClickBench repository and creates the hits index in OpenSearch
# Author: Generated for BusyBox project
# Date: $(date)

set -e  # Exit on any error

# Configuration
CLICKBENCH_REPO="https://github.com/ClickHouse/ClickBench"
CLICKBENCH_DIR="ClickBench"
OPENSEARCH_URL="http://localhost:9200"
INDEX_NAME="hits"
MAPPING_FILE="elasticsearch/mapping_tuned.json"

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
    local required_commands=("git" "curl" "jq")
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

# Function to clone ClickBench repository
clone_clickbench() {
    log_info "Cloning ClickBench repository..."
    
    if [[ -d "$CLICKBENCH_DIR" ]]; then
        log_warning "ClickBench directory already exists. Updating..."
        cd "$CLICKBENCH_DIR"
        if ! git pull origin main; then
            log_warning "Failed to update repository. Removing and re-cloning..."
            cd ..
            rm -rf "$CLICKBENCH_DIR"
            git clone "$CLICKBENCH_REPO" "$CLICKBENCH_DIR"
        else
            cd ..
        fi
    else
        if ! git clone "$CLICKBENCH_REPO" "$CLICKBENCH_DIR"; then
            log_error "Failed to clone ClickBench repository"
            exit 1
        fi
    fi
    
    log_success "ClickBench repository ready"
}

# Function to validate mapping file
validate_mapping() {
    log_info "Validating mapping file..."
    
    local mapping_path="${CLICKBENCH_DIR}/${MAPPING_FILE}"
    
    if [[ ! -f "$mapping_path" ]]; then
        log_error "Mapping file not found: $mapping_path"
        exit 1
    fi
    
    # Validate JSON syntax
    if ! jq empty "$mapping_path" 2>/dev/null; then
        log_error "Invalid JSON in mapping file: $mapping_path"
        exit 1
    fi
    
    # Check if it has the expected structure
    local has_mappings=$(jq 'has("mappings")' "$mapping_path")
    local has_settings=$(jq 'has("settings")' "$mapping_path")
    
    if [[ "$has_mappings" != "true" ]]; then
        log_error "Mapping file missing 'mappings' section"
        exit 1
    fi
    
    if [[ "$has_settings" != "true" ]]; then
        log_warning "Mapping file missing 'settings' section"
    fi
    
    local field_count=$(jq '.mappings.properties | length' "$mapping_path")
    log_info "Mapping file validated: $field_count fields defined"
    
    log_success "Mapping file validation passed"
}

# Function to check if index exists
index_exists() {
    local response_code=$(curl -s -o /dev/null -w "%{http_code}" "$OPENSEARCH_URL/$INDEX_NAME" || echo "000")
    [[ "$response_code" == "200" ]]
}

# Function to delete existing index
delete_index() {
    log_warning "Deleting existing index: $INDEX_NAME"
    
    local response=$(curl -s -X DELETE "$OPENSEARCH_URL/$INDEX_NAME" 2>/dev/null || echo "")
    local response_code=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "$OPENSEARCH_URL/$INDEX_NAME" || echo "000")
    
    if [[ "$response_code" == "200" ]]; then
        log_success "Existing index deleted successfully"
    else
        log_error "Failed to delete existing index (HTTP $response_code)"
        exit 1
    fi
}

# Function to create index with mapping
create_index() {
    log_info "Creating index: $INDEX_NAME"
    
    local mapping_path="${CLICKBENCH_DIR}/${MAPPING_FILE}"
    
    # Create the index with mapping and settings
    local response=$(curl -s -X PUT \
        -H "Content-Type: application/json" \
        -d @"$mapping_path" \
        "$OPENSEARCH_URL/$INDEX_NAME")
    
    local response_code=$(curl -s -o /dev/null -w "%{http_code}" -X PUT \
        -H "Content-Type: application/json" \
        -d @"$mapping_path" \
        "$OPENSEARCH_URL/$INDEX_NAME")
    
    if [[ "$response_code" == "200" ]]; then
        log_success "Index created successfully"
        
        # Display index information
        local index_info=$(curl -s "$OPENSEARCH_URL/$INDEX_NAME" 2>/dev/null || echo "")
        if [[ -n "$index_info" ]]; then
            local field_count=$(echo "$index_info" | jq ".[\"$INDEX_NAME\"].mappings.properties | length" 2>/dev/null || echo "unknown")
            log_info "Index created with $field_count field mappings"
        fi
    else
        log_error "Failed to create index (HTTP $response_code)"
        log_error "Response: $response"
        exit 1
    fi
}

# Function to verify index creation
verify_index() {
    log_info "Verifying index creation..."
    
    local index_info=$(curl -s "$OPENSEARCH_URL/$INDEX_NAME" 2>/dev/null || echo "")
    
    if [[ -z "$index_info" ]]; then
        log_error "Failed to retrieve index information"
        exit 1
    fi
    
    # Check if index has the expected structure
    local has_mappings=$(echo "$index_info" | jq ".[\"$INDEX_NAME\"] | has(\"mappings\")" 2>/dev/null || echo "false")
    local has_settings=$(echo "$index_info" | jq ".[\"$INDEX_NAME\"] | has(\"settings\")" 2>/dev/null || echo "false")
    
    if [[ "$has_mappings" == "true" && "$has_settings" == "true" ]]; then
        log_success "Index verification passed"
        
        # Display some key information
        local field_count=$(echo "$index_info" | jq ".[\"$INDEX_NAME\"].mappings.properties | length" 2>/dev/null || echo "unknown")
        local sort_fields=$(echo "$index_info" | jq -r ".[\"$INDEX_NAME\"].settings.index[\"sort.field\"] // [] | join(\", \")" 2>/dev/null || echo "none")
        
        log_info "Index details:"
        log_info "  - Field mappings: $field_count"
        log_info "  - Sort fields: $sort_fields"
    else
        log_error "Index verification failed - missing mappings or settings"
        exit 1
    fi
}

# Function to display usage information
display_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "  -f, --force     Force recreation of index (delete existing if present)"
    echo "  -u, --url URL   OpenSearch URL (default: $OPENSEARCH_URL)"
    echo "  -i, --index     Index name (default: $INDEX_NAME)"
    echo "  -h, --help      Show this help message"
    echo
    echo "Examples:"
    echo "  $0                          # Create index with default settings"
    echo "  $0 --force                  # Force recreate index"
    echo "  $0 --url http://localhost:9201  # Use different OpenSearch URL"
}

# Function to display summary
display_summary() {
    log_success "ClickBench hits index preparation completed!"
    echo
    echo "Summary:"
    echo "  - Repository: ClickBench cloned/updated"
    echo "  - OpenSearch URL: $OPENSEARCH_URL"
    echo "  - Index name: $INDEX_NAME"
    echo "  - Mapping source: ${CLICKBENCH_DIR}/${MAPPING_FILE}"
    echo
    echo "Next steps:"
    echo "  1. Load data into the index using ClickBench tools"
    echo "  2. Run benchmark queries against the index"
    echo
    echo "Useful commands:"
    echo "  # Check index status"
    echo "  curl '$OPENSEARCH_URL/$INDEX_NAME/_stats?pretty'"
    echo
    echo "  # View index mapping"
    echo "  curl '$OPENSEARCH_URL/$INDEX_NAME/_mapping?pretty'"
    echo
    echo "  # Count documents (after loading data)"
    echo "  curl '$OPENSEARCH_URL/$INDEX_NAME/_count?pretty'"
}

# Function to cleanup on error
cleanup_on_error() {
    log_error "Script failed. Cleaning up..."
    # Note: We don't remove the cloned repository as it might be useful for debugging
    log_info "ClickBench repository preserved for debugging: $CLICKBENCH_DIR"
}

# Parse command line arguments
FORCE_RECREATE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -f|--force)
            FORCE_RECREATE=true
            shift
            ;;
        -u|--url)
            OPENSEARCH_URL="$2"
            shift 2
            ;;
        -i|--index)
            INDEX_NAME="$2"
            shift 2
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
    log_info "Starting ClickBench hits index preparation..."
    
    # Set trap for cleanup on error
    trap cleanup_on_error ERR
    
    check_requirements
    check_opensearch
    clone_clickbench
    validate_mapping
    
    # Check if index exists and handle accordingly
    if index_exists; then
        if [[ "$FORCE_RECREATE" == true ]]; then
            delete_index
            create_index
        else
            log_warning "Index '$INDEX_NAME' already exists"
            log_info "Use --force to recreate the index"
            log_info "Verifying existing index..."
            verify_index
        fi
    else
        create_index
    fi
    
    verify_index
    display_summary
    
    log_success "Script completed successfully!"
}

# Run main function
main "$@"
