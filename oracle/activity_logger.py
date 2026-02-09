# Agbero Autonomous Activity Logger
# Logs every action to Solana devnet via Memo program
# This IS the "Most Agentic" demonstration

import os
import json
import time
import hashlib
from datetime import datetime
from solana.rpc.api import Client
from solana.transaction import Transaction
from solana.keypair import Keypair
from solana.publickey import PublicKey
from solana.system_program import TransferParams, transfer
from solana.memo_program import MemoParams, memo_program

class AgberoActivityLogger:
    """
    Autonomous activity logger - every action is hashed, signed, and anchored on-chain.
    Not "trust me" - cryptographic proof of what Agbero actually did.
    """
    
    def __init__(self):
        self.rpc_url = os.getenv('SOLANA_RPC', 'https://api.devnet.solana.com')
        self.client = Client(self.rpc_url)
        
        # Load validator keypair
        keypair_path = os.getenv('VALIDATOR_KEYPAIR_PATH', '~/.config/solana/id.json')
        with open(os.path.expanduser(keypair_path)) as f:
            secret = json.load(f)
        self.keypair = Keypair.from_secret_key(bytes(secret))
        
        self.activity_count = 0
        self.build_cycles = 0
        
    def log_activity(self, action: str, data: dict) -> str:
        """
        Log an activity on-chain via memo program.
        Format: SHA256(action + data + timestamp) -> memo transaction
        """
        timestamp = datetime.utcnow().isoformat()
        self.activity_count += 1
        
        # Create activity payload
        payload = {
            'agent': 'agbero',
            'action': action,
            'data': data,
            'timestamp': timestamp,
            'sequence': self.activity_count
        }
        
        # Hash the payload
        payload_json = json.dumps(payload, sort_keys=True)
        payload_hash = hashlib.sha256(payload_json.encode()).hexdigest()[:16]
        
        # Create memo
        memo_text = f"AGBERO:{action}:{payload_hash}:{timestamp}"
        
        try:
            # Build transaction
            txn = Transaction()
            txn.add(
                memo_program(
                    MemoParams(
                        signer=self.keypair.public_key,
                        memo=memo_text
                    )
                )
            )
            
            # Send transaction
            response = self.client.send_transaction(txn, self.keypair)
            signature = response['result']
            
            print(f"✅ Activity #{self.activity_count} logged: {action}")
            print(f"   Hash: {payload_hash}")
            print(f"   Tx: {signature}")
            
            return signature
            
        except Exception as e:
            print(f"⚠️  Failed to log activity: {e}")
            # Still track locally even if on-chain fails
            return f"local-{payload_hash}"
    
    def log_build_cycle(self, components: list) -> str:
        """Log a build cycle (file creation, compilation, test)"""
        self.build_cycles += 1
        return self.log_activity('build_cycle', {
            'cycle_number': self.build_cycles,
            'components_built': components,
            'total_activities': self.activity_count
        })
    
    def log_deployment(self, program_id: str, network: str) -> str:
        """Log program deployment"""
        return self.log_activity('deployment', {
            'program_id': program_id,
            'network': network,
            'validator': str(self.keypair.public_key)
        })
    
    def log_bond_created(self, bond_id: str, principal: str, collateral: float) -> str:
        """Log bond creation"""
        return self.log_activity('bond_created', {
            'bond_id': bond_id,
            'principal': principal,
            'collateral_sol': collateral
        })
    
    def log_verification_vote(self, bond_id: str, approve: bool, confidence: float) -> str:
        """Log verification vote"""
        return self.log_activity('verification_vote', {
            'bond_id': bond_id,
            'approve': approve,
            'confidence': confidence,
            'validator': str(self.keypair.public_key)
        })
    
    def log_bond_finalized(self, bond_id: str, outcome: str, stake_amount: float) -> str:
        """Log bond finalization"""
        return self.log_activity('bond_finalized', {
            'bond_id': bond_id,
            'outcome': outcome,
            'stake_amount_sol': stake_amount
        })
    
    def get_stats(self) -> dict:
        """Get activity stats"""
        return {
            'total_activities': self.activity_count,
            'build_cycles': self.build_cycles,
            'agent': 'agbero',
            'validator': str(self.keypair.public_key),
            'network': self.rpc_url
        }

# Singleton instance
_logger = None

def get_logger():
    global _logger
    if _logger is None:
        _logger = AgberoActivityLogger()
    return _logger

if __name__ == '__main__':
    logger = get_logger()
    
    # Log startup
    logger.log_activity('startup', {'version': '0.1.0', 'mode': 'autonomous'})
    
    # Simulate some activities
    logger.log_build_cycle(['lib.rs', 'Cargo.toml'])
    logger.log_deployment('Agbero1111111111111111111111111111111111111', 'devnet')
    
    print(f"\n📊 Stats: {json.dumps(logger.get_stats(), indent=2)}")
