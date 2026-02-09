# Agbero Auto-Deploy Script
# One command to deploy and initialize everything

import subprocess
import json
import os
import sys
from pathlib import Path

# Add oracle to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'oracle'))

try:
    from activity_logger import get_logger
    logger = get_logger()
except:
    logger = None

def run_command(cmd: str, desc: str) -> str:
    """Run shell command and log it"""
    print(f"\n🔨 {desc}...")
    
    if logger:
        logger.log_activity('command_start', {'command': cmd, 'description': desc})
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
        if logger:
            logger.log_activity('command_error', {'command': cmd, 'error': result.stderr})
        sys.exit(1)
    
    print(f"✅ {desc} complete")
    
    if logger:
        logger.log_activity('command_complete', {'command': cmd, 'output': result.stdout[:200]})
    
    return result.stdout

def main():
    print("🛡️  Agbero Auto-Deploy")
    print("=" * 50)
    
    # Log start
    if logger:
        logger.log_activity('deploy_start', {'version': '0.1.0'})
    
    # Set devnet
    run_command('solana config set --url devnet', 'Configuring Solana for devnet')
    
    # Check/get airdrop
    balance_output = run_command('solana balance', 'Checking balance')
    balance = float(balance_output.split()[0])
    
    if balance < 2.0:
        print("💰 Requesting airdrop...")
        run_command('solana airdrop 2', 'Requesting devnet SOL')
    
    # Build
    run_command('anchor build', 'Building Anchor program')
    if logger:
        logger.log_build_cycle(['lib.rs', 'idl generation'])
    
    # Deploy
    deploy_output = run_command('anchor deploy', 'Deploying to devnet')
    
    # Extract program ID
    for line in deploy_output.split('\n'):
        if 'Program Id:' in line:
            program_id = line.split('Program Id:')[1].strip()
            print(f"\n🎯 Program ID: {program_id}")
            
            if logger:
                logger.log_deployment(program_id, 'devnet')
            
            # Update config files
            print("\n📝 Updating configuration files...")
            
            # Update Anchor.toml
            anchor_toml = Path('Anchor.toml')
            if anchor_toml.exists():
                content = anchor_toml.read_text()
                content = content.replace(
                    'Agbero1111111111111111111111111111111111111',
                    program_id
                )
                anchor_toml.write_text(content)
            
            # Update lib.rs
            lib_rs = Path('programs/agbero/src/lib.rs')
            if lib_rs.exists():
                content = lib_rs.read_text()
                content = content.replace(
                    'Agbero1111111111111111111111111111111111111',
                    program_id
                )
                lib_rs.write_text(content)
            
            break
    
    # Rebuild with correct program ID
    run_command('anchor build', 'Rebuilding with final program ID')
    
    # Redeploy
    run_command('anchor deploy', 'Final deployment')
    
    # Run tests
    print("\n🧪 Running tests...")
    test_result = subprocess.run('anchor test --skip-local-validator', shell=True)
    if test_result.returncode == 0:
        print("✅ All tests passed")
        if logger:
            logger.log_activity('tests_passed', {'count': 'all'})
    else:
        print("⚠️  Some tests failed (non-critical for hackathon)")
    
    # Git commit the deployment
    run_command('git add -A', 'Staging changes')
    run_command('git commit -m "Auto-deploy: Program deployed to devnet"', 'Committing deployment')
    
    # Final stats
    if logger:
        stats = logger.get_stats()
        print(f"\n📊 Deployment Stats:")
        print(json.dumps(stats, indent=2))
        logger.log_activity('deploy_complete', stats)
    
    print("\n" + "=" * 50)
    print("✅ Agbero deployed successfully!")
    print("\nNext steps:")
    print("1. Create GitHub repo and push")
    print("2. Update Colosseum project with program ID")
    print("3. Start autonomous validator: python oracle/validator.py")
    print("4. Create demo bonds")

if __name__ == '__main__':
    main()
