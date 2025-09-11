#!/bin/bash

# OpenSearch 3.2.0 Setup Script
# This script downloads OpenSearch 3.2.0, configures plugins, and adjusts JVM settings
# Author: Generated for BusyBox project
# Date: $(date)

set -e  # Exit on any error

# Configuration
OPENSEARCH_VERSION="3.2.0"
OPENSEARCH_DIR="opensearch-${OPENSEARCH_VERSION}"
OPENSEARCH_ARCHIVE="${OPENSEARCH_DIR}-linux-x64.tar.gz"
DOWNLOAD_URL="https://artifacts.opensearch.org/releases/bundle/opensearch/${OPENSEARCH_VERSION}/${OPENSEARCH_ARCHIVE}"

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
    local required_commands=("curl" "tar" "java")
    for cmd in "${required_commands[@]}"; do
        if ! command_exists "$cmd"; then
            log_error "Required command '$cmd' not found. Please install it first."
            exit 1
        fi
    done
    
    # Check Java version
    local java_version_output=$(java -version 2>&1 | head -n 1)
    local java_version=$(echo "$java_version_output" | sed -n 's/.*"\([0-9]*\)\..*/\1/p')
    
    # Handle cases where version might be in different format
    if [[ -z "$java_version" ]]; then
        java_version=$(echo "$java_version_output" | sed -n 's/.*version "\([0-9]*\.[0-9]*\).*/\1/p' | cut -d'.' -f1)
    fi
    
    if [[ -n "$java_version" && "$java_version" -ge 11 ]]; then
        log_info "Java version check passed: $java_version"
    else
        log_error "Java 11 or higher is required. Detected: $java_version_output"
        exit 1
    fi
    
    log_success "System requirements check passed"
}

# Function to download OpenSearch
download_opensearch() {
    log_info "Downloading OpenSearch ${OPENSEARCH_VERSION}..."
    
    if [[ -f "$OPENSEARCH_ARCHIVE" ]]; then
        log_warning "Archive $OPENSEARCH_ARCHIVE already exists. Skipping download."
        return 0
    fi
    
    if ! curl -L -o "$OPENSEARCH_ARCHIVE" "$DOWNLOAD_URL"; then
        log_error "Failed to download OpenSearch from $DOWNLOAD_URL"
        exit 1
    fi
    
    log_success "OpenSearch downloaded successfully"
}

# Function to extract OpenSearch
extract_opensearch() {
    log_info "Extracting OpenSearch archive..."
    
    if [[ -d "$OPENSEARCH_DIR" ]]; then
        log_warning "Directory $OPENSEARCH_DIR already exists. Removing it..."
        rm -rf "$OPENSEARCH_DIR"
    fi
    
    if ! tar -xzf "$OPENSEARCH_ARCHIVE"; then
        log_error "Failed to extract OpenSearch archive"
        exit 1
    fi
    
    log_success "OpenSearch extracted successfully"
}

# Function to manage plugins
manage_plugins() {
    log_info "Managing OpenSearch plugins..."
    
    local plugins_dir="${OPENSEARCH_DIR}/plugins"
    
    if [[ ! -d "$plugins_dir" ]]; then
        log_error "Plugins directory not found: $plugins_dir"
        exit 1
    fi
    
    # List current plugins
    log_info "Current plugins:"
    ls -la "$plugins_dir"
    
    # Keep only opensearch-sql and opensearch-job-scheduler
    local keep_plugins=("opensearch-sql" "opensearch-job-scheduler")
    
    # Find all plugin directories
    for plugin_dir in "$plugins_dir"/*; do
        if [[ -d "$plugin_dir" ]]; then
            local plugin_name=$(basename "$plugin_dir")
            local keep_plugin=false
            
            # Check if this plugin should be kept
            for keep in "${keep_plugins[@]}"; do
                if [[ "$plugin_name" == "$keep" ]]; then
                    keep_plugin=true
                    break
                fi
            done
            
            if [[ "$keep_plugin" == true ]]; then
                log_success "Keeping plugin: $plugin_name"
            else
                log_warning "Removing plugin: $plugin_name"
                rm -rf "$plugin_dir"
            fi
        fi
    done
    
    # Verify required plugins exist
    for required_plugin in "${keep_plugins[@]}"; do
        if [[ ! -d "$plugins_dir/$required_plugin" ]]; then
            log_error "Required plugin '$required_plugin' not found in OpenSearch distribution"
            log_info "Available plugins after cleanup:"
            ls -la "$plugins_dir"
            exit 1
        fi
    done
    
    log_success "Plugin management completed"
}

# Function to update JVM options
update_jvm_options() {
    log_info "Updating JVM options..."
    
    local jvm_options_file="${OPENSEARCH_DIR}/config/jvm.options"
    
    if [[ ! -f "$jvm_options_file" ]]; then
        log_error "JVM options file not found: $jvm_options_file"
        exit 1
    fi
    
    # Create backup
    cp "$jvm_options_file" "${jvm_options_file}.backup"
    log_info "Created backup: ${jvm_options_file}.backup"
    
    # Update memory settings
    sed -i.tmp 's/-Xms1g/-Xms16g/g' "$jvm_options_file"
    sed -i.tmp 's/-Xmx1g/-Xmx16g/g' "$jvm_options_file"
    
    # Remove temporary file created by sed on macOS
    rm -f "${jvm_options_file}.tmp"
    
    # Verify changes
    log_info "JVM memory settings after update:"
    grep -E "^-Xm[sx]" "$jvm_options_file" || true
    
    log_success "JVM options updated successfully"
}

# Function to set permissions
set_permissions() {
    log_info "Setting appropriate permissions..."
    
    # Make scripts executable
    chmod +x "${OPENSEARCH_DIR}/bin/"*
    
    log_success "Permissions set successfully"
}

# Function to display summary
display_summary() {
    log_success "OpenSearch setup completed successfully!"
    echo
    echo "Summary:"
    echo "  - OpenSearch version: ${OPENSEARCH_VERSION}"
    echo "  - Installation directory: ${OPENSEARCH_DIR}"
    echo "  - Remaining plugins:"
    ls -1 "${OPENSEARCH_DIR}/plugins" | sed 's/^/    - /'
    echo "  - JVM heap size: 16GB (Xms16g, Xmx16g)"
    echo
    echo "To start OpenSearch:"
    echo "  cd ${OPENSEARCH_DIR}"
    echo "  ./bin/opensearch"
    echo
    echo "To start OpenSearch in the background:"
    echo "  cd ${OPENSEARCH_DIR}"
    echo "  ./bin/opensearch -d"
    echo
    echo "OpenSearch will be available at: http://localhost:9200"
    echo "Default credentials: admin/admin"
}

# Function to cleanup on error
cleanup_on_error() {
    log_error "Script failed. Cleaning up..."
    if [[ -f "$OPENSEARCH_ARCHIVE" ]]; then
        log_info "Removing downloaded archive..."
        rm -f "$OPENSEARCH_ARCHIVE"
    fi
    if [[ -d "$OPENSEARCH_DIR" ]]; then
        log_info "Removing extracted directory..."
        rm -rf "$OPENSEARCH_DIR"
    fi
}

# Main execution
main() {
    log_info "Starting OpenSearch 3.2.0 setup..."
    
    # Set trap for cleanup on error
    trap cleanup_on_error ERR
    
    check_requirements
    download_opensearch
    extract_opensearch
    manage_plugins
    update_jvm_options
    set_permissions
    display_summary
    
    log_success "Setup script completed successfully!"
}

# Run main function
main "$@"
