# 📊 Dirty CSV Generator

Generate CSV files with intentionally bad/dirty data for testing data cleansing tools and ETL pipelines.

## Usage

```bash
python generate_dirty_csv.py <num_rows> <quality_score>
```

| Argument | Type | Description |
|---|---|---|
| `num_rows` | int | Number of rows to generate |
| `quality_score` | float (0-1) | Data quality: 0 = all dirty, 1 = all clean |

## Examples

```bash
# Generate 1000 rows of absolute garbage data
python generate_dirty_csv.py 1000 0.0

# Generate 500 rows with ~50% dirty fields
python generate_dirty_csv.py 500 0.5

# Generate 200 rows of perfectly clean data
python generate_dirty_csv.py 200 1.0

# Generate a large dataset with slight corruption
python generate_dirty_csv.py 10000 0.85
```

## Output

Creates `dirty_data_{rows}_{quality}.csv` in the current directory.

### Columns

| Column | Clean Format |
|---|---|
| `id` | Sequential integer |
| `first_name` | Capitalized name |
| `last_name` | Capitalized name |
| `email` | valid@email.com |
| `phone` | (555) 123-4567 |
| `address` | 123 Main St |
| `city` | City name |
| `state` | Two-letter state code |
| `zip_code` | 5-digit zip |
| `date_of_birth` | YYYY-MM-DD |
| `salary` | Positive integer |
| `company` | Company name |

## Types of Dirty Data

The script injects the following corruption types, controlled by `quality_score`:

- **NULL/empty values** — blank or `None` fields
- **Wrong field placement** — phone in first_name, email in phone, etc.
- **Invalid formats** — malformed emails, impossible dates (2025-13-45)
- **Duplicate rows** — exact row copies
- **Mixed data types** — strings in numeric fields
- **Extra whitespace** — leading/trailing/double spaces
- **Special characters** — `@#$%` injected into names
- **Inconsistent casing** — ALL CAPS, rAnDoM cAsE
- **Truncated values** — cut-off strings
- **Unicode/emoji injection** — 🔥 in your data
- **Impossible values** — negative salary, zip "ABCDE", age 999

## Requirements

**Python 3.6+** — uses only standard library modules (csv, random, string, datetime).

No `pip install` needed.

---

# 🗺️ Port Map - Container Port Visualization

Parses `podman ps` (or `docker ps`) output and generates a clean Unicode table and terminal flowchart showing container port mappings.

## Usage

```bash
# Pipe directly from podman/docker
podman ps | python portmap.py
podman ps -a | python portmap.py

# Custom format (tab-separated)
podman ps --format '{{.ID}}\t{{.Names}}\t{{.Ports}}\t{{.Status}}\t{{.Image}}' | python portmap.py

# From a file
python portmap.py < dump.txt
```

## Output

### Port Table
A Unicode box-drawing table sorted by port number showing:
- Host → container port mappings
- Container name, status, and image
- Color-coded output (auto-disabled for non-TTY)

### Flow Diagram
Visual ASCII/Unicode art showing:
- Containers with their port arrows
- HOST NETWORK containers (labeled separately)
- Containers with no exposed ports

## Features

- Auto-detects standard tabular `podman ps` output vs custom `--format` tab-separated output
- Handles multiple port mappings per container
- Supports TCP and UDP ports
- ANSI color output with auto-detect (disabled when piped)
- Handles edge cases: no ports, exited containers, host networking

## Requirements

**Python 3.10+** — pure stdlib, no external dependencies.
