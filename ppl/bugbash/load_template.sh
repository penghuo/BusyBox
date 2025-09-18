#!/bin/bash

# Script to load index settings and mappings from index_template.json file
# Uses "log-template" as the index template name

# Display usage information
usage() {
  echo "Usage: $0 [-u username] [-p password]"
  echo "Options:"
  echo "  -u username    OpenSearch username for authentication"
  echo "  -p password    OpenSearch password for authentication"
  echo "  -h             Display this help message"
  exit 1
}

# Parse command line options
USERNAME=""
PASSWORD=""
while getopts "u:p:h" opt; do
  case ${opt} in
    u )
      USERNAME=$OPTARG
      ;;
    p )
      PASSWORD=$OPTARG
      ;;
    h )
      usage
      ;;
    \? )
      usage
      ;;
  esac
done

TEMPLATE_FILE="index_template.json"
TEMPLATE_NAME="log-template"

# Check if the template file exists
if [ ! -f "$TEMPLATE_FILE" ]; then
  echo "Error: Template file $TEMPLATE_FILE not found."
  exit 1
fi

# Check if the template file has content
if [ ! -s "$TEMPLATE_FILE" ]; then
  echo "Error: Template file $TEMPLATE_FILE is empty."
  echo "Please add index settings and mappings to the file before running this script."
  exit 1
fi

# Validate JSON format
if ! jq . "$TEMPLATE_FILE" > /dev/null 2>&1; then
  echo "Error: Template file $TEMPLATE_FILE is not valid JSON."
  exit 1
fi

echo "Loading index template '$TEMPLATE_NAME' from $TEMPLATE_FILE..."

# Use curl to create/update the index template
# Assuming OpenSearch/Elasticsearch is running on localhost:9200
# Adjust the URL if your cluster is running elsewhere

# Set up authentication if credentials are provided
AUTH_PARAM=""
if [ -n "$USERNAME" ] && [ -n "$PASSWORD" ]; then
  echo "Using authentication with username: $USERNAME"
  AUTH_PARAM="-u $USERNAME:$PASSWORD"
fi

curl -XPUT "https://search-ppl-bugbash-fgac-3-1-xymlna32dqd3uwee2bfcy2nq6m.eu-west-1.es-staging.amazonaws.com/_index_template/$TEMPLATE_NAME" \
  $AUTH_PARAM \
  -H "Content-Type: application/json" \
  -d @"$TEMPLATE_FILE"

# Check if the operation was successful
if [ $? -eq 0 ]; then
  echo "Successfully loaded index template '$TEMPLATE_NAME'."
else
  echo "Failed to load index template '$TEMPLATE_NAME'."
  exit 1
fi
