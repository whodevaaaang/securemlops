#!/usr/bin/env bash
# Build and run the API locally with docker compose.
set -euo pipefail
cd "$(dirname "$0")/.."

if [[ ! -f .env ]]; then
  echo "WARN: .env not found; API_TOKEN will be empty (auth disabled)."
fi

docker compose up --build -d
echo "API is reachable at http://localhost:8000"
echo "Try: curl -X POST http://localhost:8000/predict -H 'Content-Type: application/json' -d '{\"text\":\"great service\"}'"
