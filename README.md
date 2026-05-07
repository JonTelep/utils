# 🛠️ Utils

A reference collection of developer scripts, snippets, and design prompts by [Telep IO](https://github.com/JonTelep).

This repo is intentionally **not a functional codebase** — it's a grab bag of standalone references you can copy, adapt, or skim. No build system, no CI glue, no Dockerfile, no Makefile. Just files.

## Scripts

### [`scripts/generate_dirty_csv.py`](scripts/)

Generate CSV files with intentionally dirty/corrupted data for testing data cleansing pipelines. Pure Python — no external dependencies.

```bash
python scripts/generate_dirty_csv.py 1000 0.3   # 1000 rows, 70% dirty
python scripts/generate_dirty_csv.py 500 1.0     # 500 rows, perfectly clean
```

### [`scripts/portmap.py`](scripts/)

Visualize container port mappings from `podman ps` output. Generates a Unicode table and terminal flowchart.

```bash
podman ps | python scripts/portmap.py
podman ps -a | python scripts/portmap.py
```

## Crypto

### [`crypto/create_wallet.py`](crypto/)

CLI tool to generate crypto wallets for Solana and Coinbase Base (L2 Ethereum).

```bash
pip install -r crypto/requirements.txt
python crypto/create_wallet.py solana
python crypto/create_wallet.py base
```

## Prompts

### [`prompts/designs/`](prompts/designs/)

70+ design-system reference prompts inspired by well-known brands (Stripe, Linear, Notion, Figma, Vercel, Anthropic-adjacent tooling, automakers, fintech, media, and more). Each folder contains a `DESIGN.md` describing the visual language — colors, typography, shadows, motion — suitable for feeding to an LLM as design inspiration.

```
prompts/designs/<brand>/DESIGN.md
prompts/designs/<brand>/README.md
```

## Structure

```
utils/
├── scripts/
│   ├── generate_dirty_csv.py    # Dirty CSV generator
│   ├── portmap.py               # Container port visualization
│   └── README.md
├── crypto/
│   ├── create_wallet.py         # Wallet generator (Solana & Base)
│   ├── requirements.txt
│   └── README.md
├── prompts/
│   └── designs/                 # Brand-inspired design system prompts
└── README.md
```

## License

MIT

---

Built by **Telep IO** 🚀
