#!/usr/bin/env python3
"""
Crypto wallet generator for Solana and Coinbase Base (L2 Ethereum).

Usage:
    python create_wallet.py solana   — Create a Solana wallet
    python create_wallet.py base     — Create a Base (Ethereum L2) wallet
"""

import json
import os
import sys
from datetime import datetime, timezone

WALLETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wallets")


def ensure_wallets_dir():
    os.makedirs(WALLETS_DIR, exist_ok=True)


def create_solana_wallet():
    """Generate a new Solana keypair using solders."""
    try:
        from solders.keypair import Keypair  # type: ignore
    except ImportError:
        print("Error: 'solders' package not installed.")
        print("Run: pip install -r requirements.txt")
        sys.exit(1)

    keypair = Keypair()
    public_key = str(keypair.pubkey())
    private_key = list(bytes(keypair))  # 64-byte secret key as list of ints

    wallet_data = {
        "chain": "solana",
        "network": "mainnet-beta",
        "public_key": public_key,
        "private_key": private_key,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "warning": "NEVER share your private key. Anyone with this key can steal your funds.",
    }

    filename = f"solana_{public_key[:16]}.json"
    filepath = os.path.join(WALLETS_DIR, filename)
    with open(filepath, "w") as f:
        json.dump(wallet_data, f, indent=2)

    print(f"\n🟣 Solana Wallet Created")
    print(f"   Address:  {public_key}")
    print(f"   Saved to: {filepath}")
    print_security_warning()

    return public_key


def create_base_wallet():
    """Generate a new Base (Ethereum L2) wallet using eth-account."""
    try:
        from eth_account import Account  # type: ignore
    except ImportError:
        print("Error: 'eth-account' package not installed.")
        print("Run: pip install -r requirements.txt")
        sys.exit(1)

    account = Account.create()
    address = account.address
    private_key = account.key.hex()

    wallet_data = {
        "chain": "base",
        "network": "Base Mainnet (Coinbase L2)",
        "chain_id": 8453,
        "address": address,
        "private_key": private_key,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "note": "This wallet works on Base, Ethereum mainnet, and all EVM-compatible chains.",
        "warning": "NEVER share your private key. Anyone with this key can steal your funds.",
    }

    short_addr = address[:10]
    filename = f"base_{short_addr}.json"
    filepath = os.path.join(WALLETS_DIR, filename)
    with open(filepath, "w") as f:
        json.dump(wallet_data, f, indent=2)

    print(f"\n🔵 Base (Ethereum L2) Wallet Created")
    print(f"   Address:  {address}")
    print(f"   Chain ID: 8453 (Base Mainnet)")
    print(f"   Saved to: {filepath}")
    print_security_warning()

    return address


def print_security_warning():
    print()
    print("  ⚠️  SECURITY WARNING")
    print("  ├── NEVER share your private key with anyone")
    print("  ├── BACK UP the wallet file to a secure offline location")
    print("  ├── DO NOT store in cloud, email, or messaging apps")
    print("  └── Consider a hardware wallet for significant funds")
    print()


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ("solana", "base"):
        print("Usage: python create_wallet.py <chain>")
        print("  chain: solana | base")
        print()
        print("Examples:")
        print("  python create_wallet.py solana   # Create Solana wallet")
        print("  python create_wallet.py base     # Create Base (Ethereum L2) wallet")
        sys.exit(1)

    ensure_wallets_dir()
    chain = sys.argv[1]

    if chain == "solana":
        create_solana_wallet()
    elif chain == "base":
        create_base_wallet()


if __name__ == "__main__":
    main()
