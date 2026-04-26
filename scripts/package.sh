#!/usr/bin/env bash
# scripts/package.sh
# Packages sql-eval/ and python-eval/ into client-ready zips.
#
# Usage (from repo root):
#   bash scripts/package.sh
#
# Output:
#   dist/sql-eval.zip
#   dist/python-eval.zip
#
# Each zip contains the skill folder at root — ready for upload to
# Settings > Customize > Skills in Claude.ai.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIST_DIR="$REPO_ROOT/dist"

# Clean previous build
rm -rf "$DIST_DIR"
mkdir -p "$DIST_DIR"

# -------------------------------------------------------------------
# sql-eval.zip
# -------------------------------------------------------------------
echo "Packaging sql-eval..."
cd "$REPO_ROOT"
zip -r "$DIST_DIR/sql-eval.zip" sql-eval/ \
    -x "sql-eval/outputs/*" \
    -x "sql-eval/__pycache__/*" \
    -x "sql-eval/scripts/__pycache__/*"
echo "✓ dist/sql-eval.zip"

# -------------------------------------------------------------------
# python-eval.zip
# -------------------------------------------------------------------
echo "Packaging python-eval..."
cd "$REPO_ROOT"
zip -r "$DIST_DIR/python-eval.zip" python-eval/ \
    -x "python-eval/outputs/*" \
    -x "python-eval/__pycache__/*" \
    -x "python-eval/scripts/__pycache__/*"
echo "✓ dist/python-eval.zip"

# -------------------------------------------------------------------
# Summary
# -------------------------------------------------------------------
echo ""
echo "=========================================="
echo "  Build complete"
echo "=========================================="
echo "  dist/sql-eval.zip"
echo "  dist/python-eval.zip"
echo ""
echo "  Upload each zip separately via:"
echo "  Settings > Customize > Skills > + > + Create skill"
echo "=========================================="
