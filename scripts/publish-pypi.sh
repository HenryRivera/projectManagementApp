#!/bin/bash

# Script to publish the PyPI package
# Usage: ./publish-pypi.sh

set -e

PACKAGE_DIR="packages/pypi/project-management-sdk"

echo "📦 Publishing PyPI Package..."
echo ""

cd "$PACKAGE_DIR"

# Install build tools
echo "Installing build tools..."
pip install --upgrade build twine

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info src/*.egg-info

# Build the package
echo "Building package..."
python -m build

# Upload to PyPI
echo ""
echo "Uploading to PyPI..."
echo "You will be prompted for your PyPI credentials."
echo "(Use __token__ as username and your API token as password)"
echo ""
python -m twine upload dist/*

echo ""
echo "=========================================="
echo "✅ Package published successfully!"
echo "=========================================="
echo ""
echo "Install with:"
echo "  pip install project-management-sdk"
