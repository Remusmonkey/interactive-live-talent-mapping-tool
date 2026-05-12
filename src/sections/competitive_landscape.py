"""Section 1 — Competitive Landscape.

Renders a filterable table of leadership-level postings (Director, Senior
Director, Head of, VP, SVP) currently posted on public job boards at the
32 Consumer Tech + Fintech companies tracked in src/data/competitors.json.
Plus a curated "Industry Signals" panel for hiring trends and market news.

Workflow note: Section 1 reads directly from the 'Scraped — Pending Review'
tab — the scraper output IS the source of truth for display. Sourcers
triage in-place by deleting unwanted rows or editing function/level/title;
those changes show up in the app on the next cache refresh (5 min).

This means weekly scraper runs wipe sourcer edits since Pending Review is
fully refreshed each run. That's a known tradeoff — see PROJECT_LOG.md
Session 6 for the workflow decision and the persistence work item.

Data sources (in priority order):
  1. Google Sheets via service account — workbook ID + key file in .env.
     Reads 'Scraped — Pending Review' and 'Industry Signals'.
  2. data/competitor_postings.csv + data/insights.json. Fallback when
     Sheets is unconfigured or unreachable. May be stale.
"""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path
from typing import Tuple

import pandas as pd
import streamlit as st

from src import sheets


_POSTINGS_TAB = "Scraped — Pending Review"
_POSTINGS_DISPLAY_COLUMNS = ["company", "title", "function", "level", "location", "posted_date", "source_url"]
_POSTINGS_REQUIRED_COLUMNS = set(_POSTINGS_DISPLAY_COLUMNS) - {"source_url"}
_INSIGHTS_REQUIRED_COLUMNS = {"title", "body"}


@st.cache_data(ttl=300, show_spinner=False)
def _load_postings(csv_path: str) -> Tuple[pd.DataFrame, str]:
    """Return (postings dataframe, source label) for the data-source badge.

    Reads from the 'Scraped — Pending Review' tab — the scraper output
    is the source of truth for display. Falls back to local CSV when the
    Sheet is unreachable or doesn't have the expected schema. Projects
    to display columns regardless of upstream schema width (the tab has
    extra columns like raw_title/tier/source that aren't user-facing).
    """
    df = sheets.read_tab_as_dataframe(_POSTINGS_TAB)
    if df is not None and _POSTINGS_REQUIRED_COLUMNS.issubset(df.columns):
        return df[[c for c in _POSTINGS_DISPLAY_COLUMNS if c in df.columns]], "Google Sheets"
    return pd.read_csv(csv_path), "Local CSV"


@st.cache_data(ttl=300, show_spinner=False)
def _load_insights(json_path: str) -> Tuple[list[dict], str]:
    """Return (insights list, source label)."""
    df = sheets.read_tab_as_dataframe("Industry Signals")
    if df is not None and _INSIGHTS_REQUIRED_COLUMNS.issubset(df.columns):
        insights = df[["title", "body"]].dropna(subset=["title"]).to_dict("records")
        # Drop rows where title is the empty string (Sheets pads blank cells).
        insights = [i for i in insights if str(i.get("title", "")).strip()]
        return insights, "Google Sheets"
    with open(json_path) as f:
        return json.load(f), "Local JSON"


def render(data_dir: Path) -> None:
    st.header("Competitive Landscape")
    st.caption(
        "Leadership roles currently posted on public job boards at Consumer Tech "
        "and FinTech companies. Scraped weekly from Greenhouse + Ashby."
    )

    postings, postings_source = _load_postings(str(data_dir / "competitor_postings.csv"))
    if postings.empty:
        st.info(
            "No postings showing yet — the 'Scraped — Pending Review' tab is empty. "
            "Run the scraper from the repo root with "
            "`python scripts/refresh_postings.py` to populate it."
        )
        st.caption(f"Source: {postings_source}.")
        st.divider()
        _render_industry_signals(data_dir)
        return
    postings["posted_date"] = pd.to_datetime(postings["posted_date"], errors="coerce").dt.date

    filtered = _apply_column_filters(postings).sort_values(
        ["company", "posted_date"], ascending=[True, False]
    )

    st.dataframe(
        filtered,
        use_container_width=True,
        hide_index=True,
        column_config={
            "company": st.column_config.TextColumn("Company"),
            "title": st.column_config.TextColumn("Title", width="large"),
            "function": st.column_config.TextColumn("Function"),
            "level": st.column_config.TextColumn("Level"),
            "location": st.column_config.TextColumn("Location"),
            "posted_date": st.column_config.DateColumn("Posted"),
            "source_url": st.column_config.LinkColumn("Posting", display_text="Open"),
        },
    )

    st.caption(
        f"Showing {len(filtered)} of {len(postings)} postings. "
        f"Source: {postings_source}."
    )

    st.divider()
    _render_industry_signals(data_dir)


_POSTED_WITHIN_OPTIONS = {
    "All time": None,
    "Last 7 days": 7,
    "Last 14 days": 14,
    "Last 30 days": 30,
    "Last 60 days": 60,
    "Last 90 days": 90,
}


def _apply_column_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Render per-column filter widgets and return the filtered dataframe.

    Filters combine with AND logic. Defaults are 'show everything' so
    the table is fully visible on first render and each filter
    progressively narrows it. Empty multiselect = show all (treated as
    'no filter' rather than 'no rows').
    """
    # Row 1: low-cardinality, high-value categorical filters
    col_company, col_function, col_level = st.columns(3)
    with col_company:
        companies = sorted(df["company"].dropna().unique())
        company_sel = st.multiselect(
            "Company", options=companies, default=[], placeholder="All companies",
        )
    with col_function:
        functions = sorted(df["function"].dropna().unique())
        function_sel = st.multiselect(
            "Function", options=functions, default=[], placeholder="All functions",
        )
    with col_level:
        levels = sorted(df["level"].dropna().unique())
        level_sel = st.multiselect(
            "Level", options=levels, default=[], placeholder="All levels",
        )

    # Row 2: location (high-cardinality), title (free-text), date window
    col_location, col_title, col_date = st.columns(3)
    with col_location:
        locations = sorted(df["location"].dropna().unique())
        location_sel = st.multiselect(
            "Location", options=locations, default=[], placeholder="All locations",
        )
    with col_title:
        title_search = st.text_input(
            "Title contains",
            value="",
            placeholder="e.g. Product, Sales, Engineer",
        )
    with col_date:
        posted_within = st.selectbox(
            "Posted within",
            options=list(_POSTED_WITHIN_OPTIONS.keys()),
            index=0,
        )

    out = df
    if company_sel:
        out = out[out["company"].isin(company_sel)]
    if function_sel:
        out = out[out["function"].isin(function_sel)]
    if level_sel:
        out = out[out["level"].isin(level_sel)]
    if location_sel:
        out = out[out["location"].isin(location_sel)]
    if title_search.strip():
        out = out[out["title"].str.contains(title_search.strip(), case=False, na=False)]
    days = _POSTED_WITHIN_OPTIONS[posted_within]
    if days is not None:
        cutoff = date.today() - timedelta(days=days)
        out = out[out["posted_date"].apply(lambda d: isinstance(d, date) and d >= cutoff)]
    return out


def _render_industry_signals(data_dir: Path) -> None:
    st.subheader("Industry Signals")
    st.caption(
        "Tier 1 hiring trends and broader fintech market signals relevant to leadership talent flows."
    )

    insights, insights_source = _load_insights(str(data_dir / "insights.json"))

    if not insights:
        st.info(
            "No industry signals yet — the Google Sheets Industry Signals tab is empty."
        )
        st.caption(f"Source: {insights_source}.")
        return

    cards_html = "".join(
        f"<div style='border-left:4px solid #4A4AF4;border-radius:6px;"
        f"padding:14px 16px;background:#9DADF9;display:flex;flex-direction:column;'>"
        f"<div style='font-weight:600;color:#0A0340;margin-bottom:6px;font-size:0.95rem;'>"
        f"{insight['title']}</div>"
        f"<div style='color:#13131F;font-size:0.9rem;line-height:1.5;'>"
        f"{insight['body']}</div>"
        f"</div>"
        for insight in insights
    )
    st.markdown(
        "<div style='display:grid;grid-template-columns:repeat(2,1fr);"
        f"gap:16px;margin-top:8px;'>{cards_html}</div>",
        unsafe_allow_html=True,
    )
    st.caption(f"Source: {insights_source}.")
