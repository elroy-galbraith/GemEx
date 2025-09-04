#!/bin/bash

# GemEx Artifact Cleanup Script
# This script safely removes old trading-session artifacts from GitHub Actions

set -e  # Exit on any error

echo "🧹 GemEx Artifact Cleanup Script"
echo "================================="

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed."
    echo "📥 Install it from: https://cli.github.com/"
    echo "💡 Or use: brew install gh"
    exit 1
fi

# Check if user is authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ Not authenticated with GitHub CLI."
    echo "🔐 Run: gh auth login"
    exit 1
fi

echo "✅ GitHub CLI is ready"
echo ""

# Get repository info
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
echo "📂 Repository: $REPO"

# List all trading session artifacts
echo "🔍 Fetching trading session artifacts..."
ARTIFACTS=$(gh api "repos/$REPO/actions/artifacts" --paginate | jq -r '.artifacts[] | select(.name | startswith("trading-session-")) | "\(.id) \(.name) \(.created_at)"')

if [ -z "$ARTIFACTS" ]; then
    echo "✅ No trading session artifacts found. Nothing to clean up!"
    exit 0
fi

echo "📋 Found trading session artifacts:"
echo "$ARTIFACTS" | while read -r id name created_at; do
    echo "  • $name (ID: $id) - Created: $created_at"
done

echo ""
echo "⚠️  WARNING: This will permanently delete ALL trading-session artifacts."
echo "💡 This is recommended before merging to main to ensure a fresh start."
echo ""

# Confirmation prompt
read -p "🤔 Are you sure you want to delete all trading-session artifacts? (yes/no): " -r
echo ""

if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "❌ Cancelled. No artifacts were deleted."
    exit 0
fi

echo "🗑️  Deleting artifacts..."

# Delete each artifact
DELETED_COUNT=0
FAILED_COUNT=0

echo "$ARTIFACTS" | while read -r id name created_at; do
    echo "🗑️  Deleting: $name (ID: $id)"
    
    if gh api "repos/$REPO/actions/artifacts/$id" -X DELETE; then
        echo "   ✅ Deleted successfully"
        ((DELETED_COUNT++))
    else
        echo "   ❌ Failed to delete"
        ((FAILED_COUNT++))
    fi
done

echo ""
echo "🎉 Cleanup completed!"
echo "✅ Artifacts processed"
echo ""
echo "💡 Next steps:"
echo "1. Merge your branch to main"
echo "2. Let the workflow run 2-3 times successfully"
echo "3. Remove the FORCE_FRESH_START lines from the code"
echo "4. The system will then use proper temporal analysis"
echo ""
echo "🚀 Your GemEx system will start fresh with clean artifacts!"
