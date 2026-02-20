#!/bin/bash
# One-click regression for intelligence collection pre-release checks

set -e

echo "[INFO] Running intelligence collection pre-release regression..."
echo "[INFO] Specs:"
echo "  - tests/e2e/intelligence-collection-quality-fields.spec.js"
echo "  - tests/e2e/intelligence-collection-p2-cache.spec.js"
echo "  - tests/e2e/intelligence-collection-settings-and-replay.spec.js"

cd "$(dirname "$0")/../frontend"

if [ ! -d "node_modules" ]; then
  echo "[WARN] node_modules not found, installing dependencies..."
  npm ci
fi

npx playwright test \
  tests/e2e/intelligence-collection-quality-fields.spec.js \
  tests/e2e/intelligence-collection-p2-cache.spec.js \
  tests/e2e/intelligence-collection-settings-and-replay.spec.js \
  --project=chromium \
  --reporter=html

echo "[INFO] Intelligence collection pre-release regression passed"
echo "[INFO] Report: frontend/playwright-report/index.html"
