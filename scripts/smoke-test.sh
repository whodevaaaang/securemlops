#!/usr/bin/env bash
# Smoke-test a running SecureMLOps deployment.
# Usage: scripts/smoke-test.sh <base-url>
set -euo pipefail

BASE_URL="${1:-http://localhost:8000}"
RETRIES=20
SLEEP_SECS=2

echo "Waiting for $BASE_URL/health to come up..."
for ((i=1; i<=RETRIES; i++)); do
  if curl -fsS "$BASE_URL/health" >/dev/null; then
    echo "Service is healthy after ${i} attempts."
    break
  fi
  if [[ $i -eq $RETRIES ]]; then
    echo "Service did not become healthy in time." >&2
    exit 1
  fi
  sleep "$SLEEP_SECS"
done

echo "Health payload:"
curl -fsS "$BASE_URL/health"
echo

echo "Calling /predict..."
RESPONSE=$(curl -fsS -X POST "$BASE_URL/predict" \
  -H "Content-Type: application/json" \
  -d '{"text":"this product is amazing and I love it","token":"'"${API_TOKEN:-}"'"}')
echo "$RESPONSE"

echo "$RESPONSE" | grep -q '"label"' || { echo "Missing label in response" >&2; exit 1; }
echo "Smoke test passed."
