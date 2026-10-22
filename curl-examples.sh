#!/usr/bin/env bash
# Sample requests for every endpoint, including one Run from start to end.
# Start the service first (see README), then:
#   bash curl-examples.sh
set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:8001}"

echo "1. Submit a query (expect 202, a run ID and status queued):"
response=$(curl -s -X POST "$BASE_URL/research/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is a tracer bullet in software development?"}')
echo "$response"
run_id=$(echo "$response" | sed -nE 's/.*"run_id":"([^"]+)".*/\1/p')
if [[ -z "$run_id" ]]; then
  echo "No run ID in that response, so stopping here." >&2
  exit 1
fi

echo
echo "2. Poll its status until the Run finishes (about 6 seconds):"
previous=""
for _ in $(seq 1 60); do  # give up after about 30 seconds
  status_body=$(curl -s "$BASE_URL/research/$run_id/status")
  status=$(echo "$status_body" | sed -E 's/.*"status":"([^"]+)".*/\1/')
  if [[ "$status" != "$previous" ]]; then
    echo "   $(date +%T)  $status"
    previous="$status"
  fi
  if [[ "$status" == "done" || "$status" == "failed" ]]; then
    break
  fi
  sleep 0.5
done
echo "   Final: $status_body"
if [[ "$status" != "done" && "$status" != "failed" ]]; then
  echo "The Run didn't finish within 30 seconds." >&2
  exit 1
fi

echo
echo "3. Look up a run ID that doesn't exist (expect 404):"
curl -s -w " -> %{http_code}\n" "$BASE_URL/research/00000000-0000-4000-8000-000000000000/status"

echo
echo "4. Submit an empty query (expect 422 naming the field):"
curl -s -w " -> %{http_code}\n" -X POST "$BASE_URL/research/query" \
  -H "Content-Type: application/json" -d '{"query": ""}'
