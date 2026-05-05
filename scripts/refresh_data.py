"""Weekly data-refresh helper.

Run manually each week after curating new rows in `data/`. The script doesn't
fetch anything from the internet — it just validates the curated CSVs against
the constraints in BUILD_SPEC.md (schema, allowed source types, no PII columns)
and prints a summary of what changed since the last commit.

Usage:

    python scripts/refresh_data.py

Owner: TBD. Implementation lands per BUILD_SPEC.md, Day 2.
"""

from __future__ import annotations

import sys
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def main() -> int:
    print(f"Validating data in {DATA_DIR}...")
    if not DATA_DIR.exists():
        print(f"ERROR: data directory not found at {DATA_DIR}")
        return 1

    # Validation rules to implement:
    #   - comp_benchmarks.csv: source_type in {public_posting, levels_fyi, news_article, manual_research}
    #   - no PII columns (name, email, phone) anywhere
    #   - all required columns present per BUILD_SPEC.md
    #   - print row counts per file + a diff summary vs. last commit
    print("Refresh validation scaffold - implementation pending (BUILD_SPEC.md, Day 2).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
