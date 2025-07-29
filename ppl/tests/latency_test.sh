#!/bin/bash

# Save this script as measure_ppl_latency.sh
# Usage: ./measure_ppl_latency.sh

URL="http://localhost:9200/_plugins/_ppl/"
QUERY='{"query": "source=testindex | where v=1"}'

echo "Sending POST request to: $URL"

curl --request POST "$URL" \
  --header 'Content-Type: application/x-ndjson' \
  --header 'User-Agent: vscode-restclient' \
  --data "$QUERY" \
  --silent --output /dev/null --write-out \
  "DNS lookup:        %{time_namelookup}s\n\
Connect:           %{time_connect}s\n\
TLS handshake:     %{time_appconnect}s\n\
TTFB (1st byte):   %{time_starttransfer}s\n\
Total time:        %{time_total}s\n"