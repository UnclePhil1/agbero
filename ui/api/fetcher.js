// Agbero Real-Time Data Fetcher
// Connects to Solana devnet and fetches actual bond data

const { Connection, PublicKey, clusterApiUrl } = require('@solana/web3.js');

const PROGRAM_ID = new PublicKey('CjgZCZi8j4Hh4M5sctFN866w7Wg7Dn6N1JPYVRWFxGhT');
const NETWORK = 'devnet';

class AgberoDataFetcher {
    constructor() {
        this.connection = new Connection(clusterApiUrl(NETWORK), 'confirmed');
        this.programId = PROGRAM_ID;
    }

    // Fetch all bond accounts from the program
    async fetchAllBonds() {
        try {
            console.log('🔍 Fetching bonds from devnet...');
            
            const accounts = await this.connection.getProgramAccounts(this.programId, {
                commitment: 'confirmed',
                encoding: 'base64'
            });

            console.log(`✅ Found ${accounts.length} bond accounts`);

            const bonds = accounts.map((acc, index) => {
                try {
                    // Parse bond account data
                    const data = this.parseBondData(acc.account.data);
                    return {
                        id: `bond-${index + 1}`,
                        address: acc.pubkey.toBase58(),
                        ...data
                    };
                } catch (err) {
                    console.error('Error parsing bond:', err);
                    return null;
                }
            }).filter(b => b !== null);

            return bonds;
        } catch (error) {
            console.error('❌ Error fetching bonds:', error);
            return [];
        }
    }

    // Parse bond account data from buffer
    parseBondData(buffer) {
        // This is a simplified parser - in production you'd use the full IDL
        // For now, we'll return basic info
        return {
            balance: 0, // Would parse from account lamports
            dataSize: buffer.length,
            exists: true
        };
    }

    // Get program info
    async getProgramInfo() {
        try {
            const accountInfo = await this.connection.getAccountInfo(this.programId);
            
            if (!accountInfo) {
                return { exists: false, error: 'Program not found' };
            }

            return {
                exists: true,
                executable: accountInfo.executable,
                lamports: accountInfo.lamports,
                dataSize: accountInfo.data.length,
                owner: accountInfo.owner.toBase58()
            };
        } catch (error) {
            return { exists: false, error: error.message };
        }
    }

    // Fetch recent transactions
    async getRecentActivity(limit = 10) {
        try {
            const signatures = await this.connection.getSignaturesForAddress(
                this.programId,
                { limit }
            );

            const activities = [];
            
            for (const sigInfo of signatures) {
                try {
                    const tx = await this.connection.getTransaction(sigInfo.signature, {
                        commitment: 'confirmed'
                    });

                    if (tx) {
                        activities.push({
                            signature: sigInfo.signature,
                            timestamp: sigInfo.blockTime,
                            slot: sigInfo.slot,
                            success: tx.meta.err === null,
                            fee: tx.meta.fee
                        });
                    }
                } catch (err) {
                    console.error('Error fetching tx:', err);
                }
            }

            return activities;
        } catch (error) {
            console.error('❌ Error fetching activity:', error);
            return [];
        }
    }

    // Get real-time stats
    async getStats() {
        const bonds = await this.fetchAllBonds();
        const programInfo = await this.getProgramInfo();

        return {
            totalBonds: bonds.length,
            programInfo,
            network: NETWORK,
            timestamp: new Date().toISOString()
        };
    }
}

// Run if called directly
if (require.main === module) {
    const fetcher = new AgberoDataFetcher();
    
    async function main() {
        console.log('🛡️ Agbero Real-Time Data Fetcher\n');
        
        // Check program
        console.log('1️⃣ Checking program...');
        const programInfo = await fetcher.getProgramInfo();
        console.log(programInfo);

        // Fetch bonds
        console.log('\n2️⃣ Fetching bonds...');
        const bonds = await fetcher.fetchAllBonds();
        console.log(`Found ${bonds.length} bonds`);

        // Fetch activity
        console.log('\n3️⃣ Fetching recent activity...');
        const activity = await fetcher.getRecentActivity(5);
        console.log(`Found ${activity.length} recent transactions`);
        activity.forEach(a => {
            console.log(`  - ${a.signature.slice(0, 20)}... (${a.success ? '✅' : '❌'})`);
        });

        console.log('\n✅ Data fetch complete');
    }

    main().catch(console.error);
}

module.exports = AgberoDataFetcher;
