"""Google Sheets reader using a service account.

Wraps gspread so the rest of the codebase can call one function to pull a
tab as a pandas DataFrame without thinking about authentication. If the
service account or workbook isn't configured, the helpers return None so
callers can fall back to local files.
"""

from __future__ import annotations

from typing import Optional

import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

from src import config

# Read-only access is all we need for the app. The scraper (Phase 1A+)
# will use a separate, write-capable client.
_SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


def _open_workbook() -> Optional[gspread.Spreadsheet]:
    """Authenticate via the service account and open the configured workbook.

    Returns None when Sheets isn't configured, when the key file is missing,
    or when any other failure happens — callers should then fall back to
    local CSVs. We never crash the app on a Sheets failure; demo audiences
    deserve stale-but-rendered, not blank-and-broken.
    """
    if not config.sheets_configured():
        return None

    try:
        creds = Credentials.from_service_account_file(
            config.google_sheets_key_file(),
            scopes=_SCOPES,
        )
        client = gspread.authorize(creds)
        return client.open_by_key(config.google_sheets_workbook_id())
    except Exception:
        return None


def read_tab_as_dataframe(tab_name: str) -> Optional[pd.DataFrame]:
    """Read a tab from the configured workbook and return it as a DataFrame.

    Assumes the first row of the tab is the header. Returns:
      - DataFrame (possibly empty rows but with proper columns) on success
      - None when the workbook isn't configured, the tab is unreachable, or
        the tab has no header row at all (truly blank Sheet)

    The "headers but no data rows" case still returns a DataFrame so callers
    can distinguish a valid-but-empty Sheet from a broken one — useful
    while the scraper hasn't populated data yet.
    """
    workbook = _open_workbook()
    if workbook is None:
        return None

    try:
        worksheet = workbook.worksheet(tab_name)
        all_values = worksheet.get_all_values()
        if not all_values:
            return None
        # Normalize headers: lowercase + underscores, so "Posted Date" or
        # "posted_date" both work and downstream code can rely on a stable
        # canonical form regardless of how a sourcer typed the header.
        headers = [h.strip().lower().replace(" ", "_") for h in all_values[0]]
        if not any(headers):
            return None
        rows = all_values[1:]
        return pd.DataFrame(rows, columns=headers)
    except Exception:
        return None
