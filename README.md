# 🛠️ Utils

A collection of developer utilities by [Telep IO](https://github.com/JonTelep).

## Tools

### [`scripts/generate_dirty_csv.py`](scripts/)

Generate CSV files with intentionally dirty/corrupted data for testing data cleansing pipelines. Pure Python — no external dependencies.

```bash
python scripts/generate_dirty_csv.py 1000 0.3   # 1000 rows, 70% dirty
python scripts/generate_dirty_csv.py 500 1.0     # 500 rows, perfectly clean
```

### [`crypto/create_wallet.py`](crypto/)

CLI tool to generate crypto wallets for Solana and Coinbase Base (L2 Ethereum).

```bash
pip install -r crypto/requirements.txt
python crypto/create_wallet.py solana
python crypto/create_wallet.py base
```

## Structure

```
utils/
├── scripts/
│   ├── generate_dirty_csv.py    # Dirty CSV generator
│   └── README.md
├── crypto/
│   ├── create_wallet.py         # Wallet generator (Solana & Base)
│   ├── requirements.txt
│   ├── README.md
│   └── .gitignore
└── README.md
```

## License

MIT

---

Built by **Telep IO** 🚀
