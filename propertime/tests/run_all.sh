#!/bin/bash
set -e

# Navigate to the project root
cd "$(dirname "$0")/../.."

echo "=== Syncing dependencies ==="
uv sync

echo ""
echo "=== Running unit tests ==="
uv run python -m unittest discover

echo ""
echo "=== Running e2e notebook test ==="
bash propertime/tests/e2e/test_notebook.sh

echo ""
echo "=== All tests passed ==="
