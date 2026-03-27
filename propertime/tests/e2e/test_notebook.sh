#!/bin/bash
set -e

OUTDIR=$(mktemp -d)
trap "rm -rf $OUTDIR" EXIT

echo "Executing Quickstart.ipynb..."
uv run python -m nbconvert --to notebook --execute Quickstart.ipynb --output-dir "$OUTDIR"
echo "Notebook executed successfully."
