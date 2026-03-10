# 🔐 Crypto Wallet Generator

CLI tool to create crypto wallets for **Solana** and **Coinbase Base** (L2 Ethereum).

## Chains

### Solana
Solana is a high-performance Layer 1 blockchain known for fast transaction speeds and low fees. It uses Ed25519 keypairs for wallet addresses.

### Base
Base is Coinbase's Layer 2 Ethereum rollup. It's EVM-compatible, meaning it uses the same account/key format as Ethereum (secp256k1 keypairs). Wallets created here work on Base, Ethereum mainnet, and any EVM chain.

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Create a Solana wallet
python create_wallet.py solana

# Create a Base (Ethereum L2) wallet
python create_wallet.py base
```

Each command will:
1. Generate a new random keypair
2. Print the **public address** to stdout
3. Save the full keypair (including private key) to `wallets/`

## Output

Wallet files are saved as JSON in `crypto/wallets/`:
- `solana_{address}.json`
- `base_{address}.json`

## ⚠️ Security Warnings

> **CRITICAL: Your private key is the ONLY way to access your funds.**

- **NEVER** share your private key with anyone
- **NEVER** commit wallet files to git (the `wallets/` directory is gitignored)
- **BACK UP** your wallet files to a secure, offline location
- **DO NOT** store private keys in cloud storage, email, or messaging apps
- Consider using a **hardware wallet** for significant funds
- These wallets are real — any funds sent to them are only recoverable with the private key

## Dependencies

| Package | Purpose |
|---|---|
| `solders` | Solana keypair generation |
| `eth-account` | Ethereum/Base keypair generation |
