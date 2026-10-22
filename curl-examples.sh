#!/usr/bin/env bash
# Sample requests for every endpoint. Start the service first (see README), then:
#   bash curl-examples.sh
set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:8001}"

echo "1. Submit a query (expect 202 and a run ID):"
response=$(curl -s -X POST "$BASE_URL/research/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is a tracer bullet in software development?"}')
echo "$response"
run_id=$(echo "$response" | sed -E 's/.*"run_id":"([^"]+)".*/\1/')

echo
echo "2. Look up its status (expect 200):"
curl -s "$BASE_URL/research/$run_id/status"
echo

echo
echo "3. Look up a run ID that doesn't exist (expect 404):"
curl -s -w " -> %{http_code}\n" "$BASE_URL/research/00000000-0000-4000-8000-000000000000/status"

echo
echo "4. Submit an empty query (expect 422 naming the field):"
curl -s -w " -> %{http_code}\n" -X POST "$BASE_URL/research/query" \
  -H "Content-Type: application/json" -d '{"query": ""}'
