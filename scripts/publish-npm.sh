#!/bin/bash

# Script to publish the NPM package
# Usage: ./publish-npm.sh

set -e

PACKAGE_DIR="packages/npm/project-management-ui"

echo "📦 Publishing NPM Package..."
echo ""

cd "$PACKAGE_DIR"

# Install dependencies
echo "Installing dependencies..."
npm install

# Build the package
echo "Building package..."
npm run build

# Login to NPM (if not already logged in)
echo ""
echo "Logging in to NPM..."
npm whoami 2>/dev/null || npm login

# Publish
echo ""
echo "Publishing to NPM..."
npm publish --access public

echo ""
echo "=========================================="
echo "✅ Package published successfully!"
echo "=========================================="
echo ""
echo "Install with:"
echo "  npm install @henryrivera/project-management-ui"
