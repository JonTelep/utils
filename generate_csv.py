#!/usr/bin/env python3
"""Generate CSV files with configurable data quality using Faker."""

import argparse
import csv
import random
import sys
from faker import Faker

fake = Faker()

COLUMNS = {
    "name": fake.name,
    "email": fake.email,
    "phone": fake.phone_number,
    "address": fake.address,
    "date_of_birth": lambda: fake.date_of_birth(minimum_age=18, maximum_age=90).isoformat(),
    "company": fake.company,
    "job_title": fake.job,
    "salary": lambda: round(random.uniform(30000, 200000), 2),
    "city": fake.city,
    "country": fake.country,
}

# Map each column to generators from OTHER columns for wrong-column corruption
WRONG_COLUMN_MAP = {
    "name": fake.company,
    "email": fake.phone_number,
    "phone": fake.email,
    "address": lambda: round(random.uniform(30000, 200000), 2),
    "date_of_birth": fake.name,
    "company": fake.city,
    "job_title": lambda: fake.date_of_birth().isoformat(),
    "salary": fake.email,
    "city": lambda: round(random.uniform(30000, 200000), 2),
    "country": fake.phone_number,
}


def generate_row(badness: float) -> dict:
    """Generate a single row, corrupting cells based on badness percentage."""
    row = {}
    for col, generator in COLUMNS.items():
        if random.random() < badness:
            # Coin flip: null or wrong-type data
            if random.random() < 0.5:
                row[col] = ""
            else:
                row[col] = str(WRONG_COLUMN_MAP[col]())
        else:
            row[col] = str(generator())
    return row


def main():
    parser = argparse.ArgumentParser(description="Generate CSV with configurable data quality.")
    parser.add_argument("rows", type=int, help="Number of rows to generate")
    parser.add_argument(
        "-b", "--badness", type=float, default=0.0,
        help="Percentage of bad data (0-100). Controls random nulls and wrong-column values.",
    )
    parser.add_argument("-o", "--output", default=None, help="Output file (default: stdout)")
    parser.add_argument(
        "-s", "--seed", type=int, default=None, help="Random seed for reproducibility",
    )
    args = parser.parse_args()

    if not 0 <= args.badness <= 100:
        parser.error("Badness must be between 0 and 100")
    if args.rows < 1:
        parser.error("Rows must be at least 1")

    badness = args.badness / 100.0

    if args.seed is not None:
        Faker.seed(args.seed)
        random.seed(args.seed)

    out = open(args.output, "w", newline="") if args.output else sys.stdout
    writer = csv.DictWriter(out, fieldnames=COLUMNS.keys())
    writer.writeheader()

    for _ in range(args.rows):
        writer.writerow(generate_row(badness))

    if args.output:
        out.close()
        print(f"Wrote {args.rows} rows to {args.output} (badness={args.badness}%)", file=sys.stderr)


if __name__ == "__main__":
    main()
