"""Google Sheets reader/writer using a service account.

Wraps gspread so the rest of the codebase can call one function to pull a
tab as a pandas DataFrame (for the read-only Streamlit app), or append
rows + auto-create tabs (for the scraper). If the service account or
workbook isn't configured, the read helpers return None so callers can
fall back to local files.
"""

from __future__ import annotations

from typing import List, Optional, Sequence

import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

from src import config

# Read-only scope for the app — least privilege.
_READ_SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# Read+write scope for the scraper.
_WRITE_SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


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
            scopes=_READ_SCOPES,
        )
        client = gspread.authorize(creds)
        return client.open_by_key(config.google_sheets_workbook_id())
    except Exception:
        return None


def open_workbook_for_writing() -> gspread.Spreadsheet:
    """Authenticate with read+write scope and return the workbook.

    Unlike _open_workbook(), this raises on failure rather than returning
    None — the scraper (the only caller) cannot meaningfully proceed
    without write access, so a hard failure with a clear error is better
    than silent degradation.
    """
    if not config.sheets_configured():
        raise RuntimeError(
            "Google Sheets is not configured. Set GOOGLE_SHEETS_WORKBOOK_ID "
            "and GOOGLE_SHEETS_KEY_FILE in .env."
        )
    creds = Credentials.from_service_account_file(
        config.google_sheets_key_file(),
        scopes=_WRITE_SCOPES,
    )
    client = gspread.authorize(creds)
    return client.open_by_key(config.google_sheets_workbook_id())


def get_or_create_worksheet(
    workbook: gspread.Spreadsheet,
    tab_name: str,
    headers: Sequence[str],
) -> gspread.Worksheet:
    """Return the named worksheet, creating it with the given headers if absent.

    If the worksheet exists but lacks a header row matching `headers`,
    the existing first row is overwritten with `headers`. Callers that
    care about preserving non-matching headers should check first.
    """
    try:
        worksheet = workbook.worksheet(tab_name)
    except gspread.WorksheetNotFound:
        worksheet = workbook.add_worksheet(
            title=tab_name, rows=100, cols=max(10, len(headers))
        )
        worksheet.update("A1", [list(headers)])
        return worksheet

    existing = worksheet.row_values(1)
    if [h.strip().lower() for h in existing] != [h.lower() for h in headers]:
        worksheet.update("A1", [list(headers)])
    return worksheet


def append_rows(worksheet: gspread.Worksheet, rows: List[List[str]]) -> None:
    """Append rows (list of lists, no header) to the worksheet.

    No-op when rows is empty so callers don't have to guard.
    """
    if not rows:
        return
    worksheet.append_rows(rows, value_input_option="USER_ENTERED")


def replace_data_rows(
    worksheet: gspread.Worksheet,
    headers: Sequence[str],
    rows: List[List[str]],
) -> None:
    """Wipe the worksheet and write fresh headers + rows.

    Use this for tabs that should be fully refreshed each run (e.g.,
    Pending Review — we don't want stale candidate rows accumulating
    across weeks).
    """
    worksheet.clear()
    worksheet.update("A1", [list(headers), *rows])


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
