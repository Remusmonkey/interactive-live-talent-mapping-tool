"""Centralized configuration loader for the Talent Mapping Tool.

Loads values from a local `.env` file (never committed) via python-dotenv,
plus a few computed helpers for the Google Sheets backend that's coming
online in Phase 1 of real-data rollout.

The pattern: every section reads from a published Google Sheets CSV URL if
one is configured for its tab, and falls back to the local CSV/JSON file
otherwise. This keeps the app working during the transition and protects
against transient Sheets failures.
"""

from __future__ import annotations

import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


def _get_optional(env_var: str) -> Optional[str]:
    """Return the env var stripped of whitespace, or None if blank/unset.

    Treats empty strings the same as unset — easier to grok in `.env` files
    where placeholder lines like `FOO=` are common during setup.
    """
    value = os.environ.get(env_var, "").strip()
    return value or None


def sheet_url_postings() -> Optional[str]:
    """Published-CSV URL for the Postings tab in the shared workbook."""
    return _get_optional("SHEET_POSTINGS_URL")


def sheet_url_industry_signals() -> Optional[str]:
    """Published-CSV URL for the Industry Signals tab in the shared workbook."""
    return _get_optional("SHEET_INDUSTRY_SIGNALS_URL")


def notion_token() -> Optional[str]:
    """Notion integration token (already used by src/notion_publisher.py)."""
    return _get_optional("NOTION_TOKEN")


def notion_parent_page_id() -> Optional[str]:
    """Parent Notion page ID to publish snapshots under."""
    return _get_optional("NOTION_PARENT_PAGE_ID")
