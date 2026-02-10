#!/bin/bash
# Push Agbero to GitHub - Run this on your local machine

echo "🚀 Pushing Agbero to GitHub"
echo "============================"

# Clone your empty repo
git clone https://github.com/UnclePhil1/agbero.git
cd agbero

# Add the bundle
git bundle unbundle ../agbero.bundle

# Fetch and checkout
git fetch origin
git checkout main 2>/dev/null || git checkout -b main

# Push everything
git push origin main --force

echo ""
echo "✅ Code pushed to https://github.com/UnclePhil1/agbero"
echo ""
echo "Next steps:"
echo "1. Check your repo: https://github.com/UnclePhil1/agbero"
echo "2. Update Colosseum project with this repo URL"
echo "3. Deploy to devnet with: anchor deploy"
