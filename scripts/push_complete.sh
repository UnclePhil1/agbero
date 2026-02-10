#!/bin/bash
# COMPLETE SETUP SCRIPT for UnclePhil1
# This script will push ALL Agbero code to your GitHub repo

echo "🚀 Agbero GitHub Push Script"
echo "============================"

# Configuration
GITHUB_USER="UnclePhil1"
REPO_NAME="agbero"
REPO_URL="https://github.com/$GITHUB_USER/$REPO_NAME.git"

# Step 1: Check if we're in the right place
if [ ! -f "programs/agbero/src/lib.rs" ]; then
    echo "❌ Error: Not in agbero directory"
    echo "   Run this from: /root/.openclaw/workspace/agbero"
    exit 1
fi

echo "✅ Found Agbero code"

# Step 2: Setup git (if not already done)
git config user.name "Agbero (AI Agent)"
git config user.email "agbero@agbero.sol"

# Step 3: Add remote
git remote remove origin 2>/dev/null
git remote add origin "$REPO_URL"

echo "✅ Remote configured: $REPO_URL"

# Step 4: Commit any changes
git add -A
git commit -m "Agbero MVP: Performance bonds for AI agents on Solana" || true

# Step 5: Push (this will prompt for credentials)
echo ""
echo "🔐 You will be prompted for GitHub credentials"
echo "   Username: UnclePhil1"
echo "   Password: Use a Personal Access Token (not your password!)"
echo ""
echo "   Create token here: https://github.com/settings/tokens"
echo "   Required scopes: repo (full control)"
echo ""
read -p "Press Enter when ready to push..."

git push -u origin main --force

echo ""
echo "✅ Push complete!"
echo "   Check: https://github.com/$GITHUB_USER/$REPO_NAME"
