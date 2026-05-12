"""Phase 1A scraper — fetch leadership postings from competitor public
job boards hosted on Greenhouse infrastructure.

What this script does:
  1. Reads the competitor list from src/data/competitors.json (tiered:
     primary = direct competitors, broad filter; secondary = adjacent
     Consumer Tech + Fintech, narrower filter).
  2. Hits boards-api.greenhouse.io for each company.
  3. Filters titles to leadership levels per tier (see src/scraper.py).
  4. Classifies each match into one of six BUILD_SPEC functions.
  5. Writes the full result set to the 'Scraped — Pending Review' tab in
     the configured Google Sheet (auto-created if missing). Sourcers
     triage there and copy approved rows to the 'Postings' tab.
  6. Appends a row-per-company to the 'Scraper Run Log' tab with
     counts + errors so we can spot board breakage week-over-week.

What this script does NOT do:
  - Touch Affirm's internal Greenhouse ATS or any candidate data.
  - Write to the 'Postings' tab — sourcers promote rows manually.
  - Run on a schedule. Invoked manually: `python scripts/refresh_postings.py`.

Exit code: 0 on success (even if some boards failed individually);
non-zero only on hard config or auth failures.
"""

from __future__ import annotations

import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Tuple

# Make `src` imports work when running from the repo root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import sheets  # noqa: E402
from src.scraper import (  # noqa: E402
    ClassifiedPosting,
    FetchResult,
    classify_jobs,
    fetch_greenhouse_jobs,
    load_competitor_config,
)


PENDING_REVIEW_TAB = "Scraped — Pending Review"
RUN_LOG_TAB = "Scraper Run Log"

PENDING_REVIEW_HEADERS = [
    "scraped_at",
    "company",
    "tier",
    "function",
    "level",
    "raw_title",
    "title",
    "location",
    "posted_date",
    "source_url",
]

RUN_LOG_HEADERS = [
    "run_id",
    "scraped_at",
    "company",
    "tier",
    "status",
    "total_jobs",
    "leadership_matches",
    "error_message",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def _posting_to_row(posting: ClassifiedPosting, scraped_at: str) -> List[str]:
    return [
        scraped_at,
        posting.company,
        posting.tier,
        posting.function,
        posting.level,
        posting.raw_title,
        posting.title,
        posting.location,
        posting.posted_date,
        posting.source_url,
    ]


def _run_log_row(
    run_id: str,
    scraped_at: str,
    result: FetchResult,
    tier: str,
    leadership_count: int,
) -> List[str]:
    return [
        run_id,
        scraped_at,
        result.name,
        tier,
        result.status,
        str(result.total_jobs),
        str(leadership_count),
        result.error_message or "",
    ]


def _scrape_one_tier(
    companies: List[dict],
    tier: str,
    scraped_at: str,
    run_id: str,
) -> Tuple[List[ClassifiedPosting], List[List[str]]]:
    """Scrape every company in one tier. Returns (postings, run_log_rows)."""
    all_postings: List[ClassifiedPosting] = []
    run_log_rows: List[List[str]] = []
    for entry in companies:
        slug = entry["slug"]
        name = entry["name"]
        print(f"  [{tier}] {name} ({slug})...", end=" ", flush=True)
        result, jobs = fetch_greenhouse_jobs(slug, name)
        if result.status == "ok":
            postings = classify_jobs(jobs, name, tier=tier)
            all_postings.extend(postings)
            print(f"OK — {result.total_jobs} total, {len(postings)} leadership")
            run_log_rows.append(
                _run_log_row(run_id, scraped_at, result, tier, len(postings))
            )
        else:
            print(f"FAIL — {result.status} ({result.error_message})")
            run_log_rows.append(_run_log_row(run_id, scraped_at, result, tier, 0))
    return all_postings, run_log_rows


def main() -> int:
    print("=" * 60)
    print("Phase 1A scraper — Greenhouse public boards")
    print("=" * 60)

    # Load competitor config
    try:
        primary, secondary = load_competitor_config()
    except FileNotFoundError:
        print("ERROR: src/data/competitors.json not found.", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"ERROR: failed to load competitor config: {exc}", file=sys.stderr)
        return 1

    print(f"Primary tier:   {len(primary)} companies (broad filter)")
    print(f"Secondary tier: {len(secondary)} companies (narrow filter)")
    print()

    # Open workbook (write scope). Hard fail if not configured —
    # there's no useful local fallback for the scraper.
    try:
        workbook = sheets.open_workbook_for_writing()
    except Exception as exc:
        print(f"ERROR: cannot open Google Sheets workbook: {exc}", file=sys.stderr)
        print(
            "Check GOOGLE_SHEETS_WORKBOOK_ID and GOOGLE_SHEETS_KEY_FILE in .env, "
            "and confirm the service account has Editor access to the workbook.",
            file=sys.stderr,
        )
        return 2

    scraped_at = _now_iso()
    run_id = _run_id()
    print(f"Run id: {run_id}")
    print()

    print("Fetching primary tier...")
    primary_postings, primary_log = _scrape_one_tier(primary, "primary", scraped_at, run_id)
    print()
    print("Fetching secondary tier...")
    secondary_postings, secondary_log = _scrape_one_tier(
        secondary, "secondary", scraped_at, run_id
    )
    print()

    all_postings = primary_postings + secondary_postings
    all_log_rows = primary_log + secondary_log

    print(f"Total leadership postings scraped: {len(all_postings)}")
    print(f"  Primary:   {len(primary_postings)}")
    print(f"  Secondary: {len(secondary_postings)}")
    print()

    # Write Pending Review (full refresh — wipe + rewrite each run so
    # stale postings don't accumulate week-over-week).
    print(f"Writing to '{PENDING_REVIEW_TAB}'...")
    try:
        review_tab = sheets.get_or_create_worksheet(
            workbook, PENDING_REVIEW_TAB, PENDING_REVIEW_HEADERS
        )
        review_rows = [_posting_to_row(p, scraped_at) for p in all_postings]
        sheets.replace_data_rows(review_tab, PENDING_REVIEW_HEADERS, review_rows)
        print(f"  {len(review_rows)} rows written.")
    except Exception as exc:
        print(f"ERROR: failed to write Pending Review tab: {exc}", file=sys.stderr)
        traceback.print_exc()
        return 3

    # Append to Run Log (history retained — useful for spotting boards
    # that suddenly start returning 0 results, which signals breakage).
    print(f"Appending to '{RUN_LOG_TAB}'...")
    try:
        log_tab = sheets.get_or_create_worksheet(workbook, RUN_LOG_TAB, RUN_LOG_HEADERS)
        sheets.append_rows(log_tab, all_log_rows)
        print(f"  {len(all_log_rows)} log rows appended.")
    except Exception as exc:
        print(f"ERROR: failed to write Run Log tab: {exc}", file=sys.stderr)
        traceback.print_exc()
        return 4

    print()
    print("Done. Open your Sheet and triage the 'Scraped — Pending Review' tab.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
