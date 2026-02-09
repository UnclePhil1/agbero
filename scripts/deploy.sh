#!/bin/bash
# Agbero Deployment Script
# Deploys the program to Solana devnet and initializes it

set -e

echo "🛡️ Agbero Deployment Script"
echo "============================"

# Check Solana CLI
if ! command -v solana &> /dev/null; then
    echo "❌ Solana CLI not found. Install from https://docs.solana.com/cli"
    exit 1
fi

# Check Anchor
if ! command -v anchor &> /dev/null; then
    echo "❌ Anchor not found. Install: npm install -g @coral-xyz/anchor-cli"
    exit 1
fi

# Set devnet
solana config set --url devnet
echo "✅ Configured for devnet"

# Check balance
BALANCE=$(solana balance | awk '{print $1}')
if (( $(echo "$BALANCE < 2" | bc -l) )); then
    echo "💰 Requesting airdrop..."
    solana airdrop 2
fi
echo "✅ Balance: $BALANCE SOL"

# Build
echo "🔨 Building program..."
anchor build

# Deploy
echo "🚀 Deploying to devnet..."
anchor deploy

# Get program ID
PROGRAM_ID=$(solana address -k target/deploy/agbero-keypair.json)
echo "✅ Program deployed: $PROGRAM_ID"

# Update Anchor.toml
echo "📝 Updating configuration..."
sed -i "s/Agbero1111111111111111111111111111111111111/$PROGRAM_ID/g" Anchor.toml
sed -i "s/Agbero1111111111111111111111111111111111111/$PROGRAM_ID/g" programs/agbero/src/lib.rs

# Redeploy with updated ID
echo "🚀 Redeploying with final program ID..."
anchor build
anchor deploy

echo ""
echo "✅ Deployment complete!"
echo "Program ID: $PROGRAM_ID"
echo ""
echo "Next steps:"
echo "1. Update frontend/src/config.ts with program ID: $PROGRAM_ID"
echo "2. Update SDK with deployed program ID"
echo "3. Run tests: anchor test"
echo "4. Start validator: cd oracle && npm run start"
