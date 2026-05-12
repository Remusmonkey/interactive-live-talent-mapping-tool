"""Centralized configuration loader for the Talent Mapping Tool.

Loads values from a local `.env` file (never committed) via python-dotenv,
plus helpers for the Google Sheets backend (Phase 1 real-data rollout).

Sheets access pattern: a Google Cloud service account reads from a single
shared workbook. Affirm Google Workspace blocks the simpler publish-to-web
flow, so we authenticate via a service-account JSON key file (also
gitignored, stored in secrets/). If the workbook ID or key file aren't
configured, the app falls back to the local CSV/JSON files in data/.
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


def google_sheets_workbook_id() -> Optional[str]:
    """The ID of the shared workbook (the long string in the Sheet URL)."""
    return _get_optional("GOOGLE_SHEETS_WORKBOOK_ID")


def google_sheets_key_file() -> Optional[str]:
    """Local path to the service-account JSON key file."""
    return _get_optional("GOOGLE_SHEETS_KEY_FILE")


def sheets_configured() -> bool:
    """True only when both the workbook ID and key file are set.

    Used by sections to decide whether to try Sheets at all or jump
    straight to the local-file fallback.
    """
    return bool(google_sheets_workbook_id() and google_sheets_key_file())


def notion_token() -> Optional[str]:
    """Notion integration token (already used by src/notion_publisher.py)."""
    return _get_optional("NOTION_TOKEN")


def notion_parent_page_id() -> Optional[str]:
    """Parent Notion page ID to publish snapshots under."""
    return _get_optional("NOTION_PARENT_PAGE_ID")
