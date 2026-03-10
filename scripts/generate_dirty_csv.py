#!/usr/bin/env python3
"""
Generate CSV files with intentionally dirty/corrupted data for testing
data cleansing tools and ETL pipelines.

Usage: python generate_dirty_csv.py <num_rows> <quality_score>
  num_rows:      integer, how many rows to generate
  quality_score: float 0-1 where 0 = all dirty, 1 = all clean
"""

import csv
import random
import string
import sys
from datetime import date, timedelta

# --- Seed Data ---

FIRST_NAMES = [
    "James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael",
    "Linda", "David", "Elizabeth", "William", "Barbara", "Richard", "Susan",
    "Joseph", "Jessica", "Thomas", "Sarah", "Christopher", "Karen", "Charles",
    "Lisa", "Daniel", "Nancy", "Matthew", "Betty", "Anthony", "Margaret",
    "Mark", "Sandra", "Donald", "Ashley", "Steven", "Kimberly", "Paul",
    "Emily", "Andrew", "Donna", "Joshua", "Michelle", "Kenneth", "Carol",
    "Kevin", "Amanda", "Brian", "Dorothy", "George", "Melissa", "Timothy",
    "Deborah",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
    "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark",
    "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King",
    "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green",
    "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
    "Carter", "Roberts",
]

CITIES = [
    "New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia",
    "San Antonio", "San Diego", "Dallas", "San Jose", "Austin", "Jacksonville",
    "Fort Worth", "Columbus", "Charlotte", "Indianapolis", "San Francisco",
    "Seattle", "Denver", "Washington", "Nashville", "Oklahoma City",
    "El Paso", "Boston", "Portland", "Las Vegas", "Memphis", "Louisville",
    "Baltimore", "Milwaukee",
]

STATES = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID",
    "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS",
    "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK",
    "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV",
    "WI", "WY",
]

STREET_NAMES = [
    "Main St", "Oak Ave", "Maple Dr", "Cedar Ln", "Pine Rd", "Elm St",
    "Washington Blvd", "Park Ave", "Lake Dr", "Hill Rd", "River Rd",
    "Sunset Blvd", "Broadway", "Church St", "Market St", "Spring St",
    "Highland Ave", "Forest Dr", "Meadow Ln", "Valley Rd",
]

COMPANIES = [
    "Acme Corp", "Globex Inc", "Initech", "Umbrella Corp", "Stark Industries",
    "Wayne Enterprises", "Cyberdyne Systems", "Soylent Corp", "Massive Dynamic",
    "Aperture Science", "Wonka Industries", "Dunder Mifflin", "Pied Piper",
    "Hooli", "Prestige Worldwide", "Sterling Cooper", "Los Pollos Hermanos",
    "Vandelay Industries", "Bluth Company", "TechCorp Solutions",
]

EMAIL_DOMAINS = [
    "gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "aol.com",
    "protonmail.com", "icloud.com", "mail.com", "zoho.com", "fastmail.com",
]

EMOJIS = ["🔥", "💀", "🚀", "😂", "💩", "👻", "🤖", "💰", "⚡", "🎭", "🦄", "🍕"]

SPECIAL_CHARS = ["@", "#", "$", "%", "^", "&", "*", "!", "~", "`", "\\", "|"]


def clean_first_name():
    return random.choice(FIRST_NAMES)


def clean_last_name():
    return random.choice(LAST_NAMES)


def clean_email(first, last):
    domain = random.choice(EMAIL_DOMAINS)
    sep = random.choice([".", "_", ""])
    num = random.choice(["", str(random.randint(1, 999))])
    return f"{first.lower()}{sep}{last.lower()}{num}@{domain}"


def clean_phone():
    area = random.randint(200, 999)
    mid = random.randint(200, 999)
    last = random.randint(1000, 9999)
    return f"({area}) {mid}-{last}"


def clean_address():
    num = random.randint(1, 9999)
    street = random.choice(STREET_NAMES)
    return f"{num} {street}"


def clean_city():
    return random.choice(CITIES)


def clean_state():
    return random.choice(STATES)


def clean_zip():
    return f"{random.randint(10000, 99999)}"


def clean_dob():
    start = date(1950, 1, 1)
    end = date(2005, 12, 31)
    days_between = (end - start).days
    random_date = start + timedelta(days=random.randint(0, days_between))
    return random_date.strftime("%Y-%m-%d")


def clean_salary():
    return str(random.randint(25000, 250000))


def clean_company():
    return random.choice(COMPANIES)


def generate_clean_row(row_id):
    first = clean_first_name()
    last = clean_last_name()
    return {
        "id": str(row_id),
        "first_name": first,
        "last_name": last,
        "email": clean_email(first, last),
        "phone": clean_phone(),
        "address": clean_address(),
        "city": clean_city(),
        "state": clean_state(),
        "zip_code": clean_zip(),
        "date_of_birth": clean_dob(),
        "salary": clean_salary(),
        "company": clean_company(),
    }


# --- Corruption Functions ---
# Each takes a row dict and corrupts a specific field.

def corrupt_null(row):
    """Set a random field to empty/null."""
    field = random.choice([k for k in row if k != "id"])
    row[field] = random.choice(["", "NULL", "None", "N/A", "null", "nan", "-"])
    return row


def corrupt_swap_fields(row):
    """Put values in wrong fields."""
    swaps = [
        ("first_name", "phone"),
        ("email", "phone"),
        ("phone", "first_name"),
        ("city", "state"),
        ("zip_code", "salary"),
        ("address", "email"),
        ("last_name", "city"),
    ]
    a, b = random.choice(swaps)
    row[a], row[b] = row[b], row[a]
    return row


def corrupt_invalid_email(row):
    """Malform the email."""
    corruptions = [
        lambda: f"{random.choice(FIRST_NAMES)}@@{random.choice(EMAIL_DOMAINS)}",
        lambda: f"{random.choice(FIRST_NAMES)}@",
        lambda: f"@{random.choice(EMAIL_DOMAINS)}",
        lambda: f"{random.choice(FIRST_NAMES)}.{random.choice(EMAIL_DOMAINS)}",
        lambda: f"{random.choice(FIRST_NAMES)}@.com",
        lambda: f"not an email",
        lambda: f"{random.choice(FIRST_NAMES)}@{random.choice(EMAIL_DOMAINS)}.{random.choice(EMAIL_DOMAINS)}",
        lambda: str(random.randint(10000, 99999)),
    ]
    row["email"] = random.choice(corruptions)()
    return row


def corrupt_invalid_date(row):
    """Create impossible dates."""
    corruptions = [
        lambda: f"2025-13-{random.randint(1, 45)}",
        lambda: f"2025-{random.randint(1, 12)}-32",
        lambda: f"0000-00-00",
        lambda: f"99/99/9999",
        lambda: f"{random.randint(1, 12)}/{random.randint(1, 28)}/{random.randint(1900, 2025)}",
        lambda: f"not-a-date",
        lambda: f"2025-02-30",
        lambda: f"tomorrow",
        lambda: f"{random.randint(2030, 2099)}-01-01",
    ]
    row["date_of_birth"] = random.choice(corruptions)()
    return row


def corrupt_mixed_types(row):
    """Put strings in numeric fields or vice versa."""
    targets = [
        ("salary", lambda: random.choice(["lots", "N/A", "$$$$", "unknown", "TBD", "yes"])),
        ("zip_code", lambda: random.choice(["ABCDE", "nope", "zip", "12.34", "true"])),
        ("id", lambda: random.choice(["abc", "??", "#REF!", "null", str(random.random())])),
        ("salary", lambda: str(random.random())),
    ]
    field, gen = random.choice(targets)
    row[field] = gen()
    return row


def corrupt_whitespace(row):
    """Add extra whitespace."""
    field = random.choice([k for k in row if k != "id"])
    val = row[field]
    corruption = random.choice([
        f"  {val}",
        f"{val}  ",
        f"  {val}  ",
        f"{val[:len(val)//2]}  {val[len(val)//2:]}",
        f"\t{val}",
        f"{val}\n",
    ])
    row[field] = corruption
    return row


def corrupt_special_chars(row):
    """Inject special characters."""
    field = random.choice(["first_name", "last_name", "city", "company", "address"])
    val = row[field]
    chars = "".join(random.choices(SPECIAL_CHARS, k=random.randint(1, 3)))
    pos = random.randint(0, max(len(val) - 1, 0))
    row[field] = val[:pos] + chars + val[pos:]
    return row


def corrupt_casing(row):
    """Mess up casing."""
    field = random.choice(["first_name", "last_name", "city", "company", "state", "email"])
    val = row[field]
    corruption_type = random.choice(["upper", "lower", "random"])
    if corruption_type == "upper":
        row[field] = val.upper()
    elif corruption_type == "lower":
        row[field] = val.lower()
    else:
        row[field] = "".join(c.upper() if random.random() > 0.5 else c.lower() for c in val)
    return row


def corrupt_truncate(row):
    """Truncate a value."""
    field = random.choice([k for k in row if k != "id" and len(row[k]) > 2])
    val = row[field]
    cut = random.randint(1, max(len(val) // 2, 1))
    row[field] = val[:cut]
    return row


def corrupt_unicode(row):
    """Inject unicode/emoji."""
    field = random.choice(["first_name", "last_name", "city", "company", "address", "email"])
    val = row[field]
    emoji = random.choice(EMOJIS)
    pos = random.randint(0, len(val))
    row[field] = val[:pos] + emoji + val[pos:]
    return row


def corrupt_impossible_values(row):
    """Create impossible values."""
    corruptions = [
        ("salary", lambda: str(random.randint(-100000, -1))),
        ("salary", lambda: str(random.randint(10000000, 99999999))),
        ("zip_code", lambda: "ABCDE"),
        ("zip_code", lambda: str(random.randint(100000, 999999))),
        ("zip_code", lambda: "00000"),
        ("state", lambda: random.choice(["XX", "ZZ", "USA", "N/A", "12"])),
        ("phone", lambda: "000-000-0000"),
        ("phone", lambda: str(random.randint(1, 9))),
        ("date_of_birth", lambda: "1800-01-01"),
        ("id", lambda: str(random.randint(-1000, -1))),
    ]
    field, gen = random.choice(corruptions)
    row[field] = gen()
    return row


CORRUPTION_FUNCTIONS = [
    corrupt_null,
    corrupt_swap_fields,
    corrupt_invalid_email,
    corrupt_invalid_date,
    corrupt_mixed_types,
    corrupt_whitespace,
    corrupt_special_chars,
    corrupt_casing,
    corrupt_truncate,
    corrupt_unicode,
    corrupt_impossible_values,
]


def corrupt_row(row, quality_score):
    """Apply corruption based on quality_score. Lower score = more corruption."""
    dirty_probability = 1.0 - quality_score

    # Number of corruptions to apply per row (0 at quality=1, up to 5 at quality=0)
    if random.random() < dirty_probability:
        num_corruptions = max(1, int(random.gauss(
            (1 - quality_score) * 4,  # mean: 0-4 corruptions
            1.0
        )))
        num_corruptions = min(num_corruptions, len(CORRUPTION_FUNCTIONS))

        chosen = random.sample(CORRUPTION_FUNCTIONS, num_corruptions)
        for fn in chosen:
            row = fn(row)

    return row


def generate_csv(num_rows, quality_score):
    """Generate the dirty CSV file."""
    filename = f"dirty_data_{num_rows}_{quality_score}.csv"
    fields = [
        "id", "first_name", "last_name", "email", "phone", "address",
        "city", "state", "zip_code", "date_of_birth", "salary", "company",
    ]

    rows = []
    for i in range(1, num_rows + 1):
        row = generate_clean_row(i)
        row = corrupt_row(row, quality_score)
        rows.append(row)

    # Inject duplicate rows (controlled by quality)
    num_dupes = int(num_rows * (1 - quality_score) * 0.05)  # up to 5% dupes
    for _ in range(num_dupes):
        if rows:
            dupe = dict(random.choice(rows))
            rows.append(dupe)

    # Shuffle to mix dupes in
    if num_dupes > 0:
        random.shuffle(rows)

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    total = len(rows)
    print(f"✅ Generated {filename}")
    print(f"   Rows: {total} ({num_rows} original + {total - num_rows} duplicates)")
    print(f"   Quality: {quality_score} ({'pristine' if quality_score == 1.0 else 'garbage' if quality_score == 0.0 else 'mixed'})")


def main():
    if len(sys.argv) != 3:
        print("Usage: python generate_dirty_csv.py <num_rows> <quality_score>")
        print("  num_rows:      integer, number of rows to generate")
        print("  quality_score: float 0-1 (0=all dirty, 1=all clean)")
        sys.exit(1)

    try:
        num_rows = int(sys.argv[1])
        if num_rows < 1:
            raise ValueError("num_rows must be positive")
    except ValueError as e:
        print(f"Error: Invalid num_rows — {e}")
        sys.exit(1)

    try:
        quality_score = float(sys.argv[2])
        if not 0.0 <= quality_score <= 1.0:
            raise ValueError("quality_score must be between 0 and 1")
    except ValueError as e:
        print(f"Error: Invalid quality_score — {e}")
        sys.exit(1)

    generate_csv(num_rows, quality_score)


if __name__ == "__main__":
    main()
