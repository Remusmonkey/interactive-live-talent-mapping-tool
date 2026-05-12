"""Section 1 — Competitive Landscape.

Renders, for each Tier 1 company, a table of currently posted Senior Director,
Vice President, and Senior Vice President roles plus a curated "Industry
Signals" panel that mixes Tier 1 hiring trends with broader fintech industry
news.

Data sources (in priority order):
  1. Google Sheets — published-CSV URL configured in .env. Live data.
  2. data/competitor_postings.csv + data/insights.json. Fallback when Sheets
     is unconfigured or unreachable. May be stale.

Source-selection is per-section and per-tab: if SHEET_POSTINGS_URL is set we
fetch the postings tab from Sheets but still read insights from the local JSON
unless SHEET_INDUSTRY_SIGNALS_URL is also set. Belt and suspenders.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Tuple

import pandas as pd
import streamlit as st

from src.config import sheet_url_industry_signals, sheet_url_postings


@st.cache_data(ttl=300, show_spinner=False)
def _load_postings(sheet_url: str | None, csv_path: str) -> Tuple[pd.DataFrame, str]:
    """Return (postings dataframe, source label) for the data-source badge.

    Tries Sheets first if a URL is configured; falls back to local CSV on any
    exception (network failure, malformed CSV, etc.). The 5-minute cache means
    edits in Google Sheets show up in the app within 5 minutes without manual
    refresh, but we don't re-fetch on every interaction.
    """
    if sheet_url:
        try:
            df = pd.read_csv(sheet_url)
            return df, "Google Sheets"
        except Exception:
            # Intentionally swallow and fall through — failure should degrade
            # to local CSV, not crash the app for a stakeholder demo.
            pass
    df = pd.read_csv(csv_path)
    return df, "Local CSV"


@st.cache_data(ttl=300, show_spinner=False)
def _load_insights(sheet_url: str | None, json_path: str) -> Tuple[list[dict], str]:
    """Return (insights list, source label). Sheets returns a dataframe; we
    convert to the same shape as the local JSON so downstream code is uniform.
    """
    if sheet_url:
        try:
            df = pd.read_csv(sheet_url)
            insights = df[["title", "body"]].dropna(subset=["title"]).to_dict("records")
            return insights, "Google Sheets"
        except Exception:
            pass
    with open(json_path) as f:
        return json.load(f), "Local JSON"


def render(data_dir: Path) -> None:
    st.header("Competitive Landscape")
    st.caption(
        "Senior Director, Vice President, and Senior Vice President roles posted at Tier 1 fintech competitors "
        "(Stripe, Block, Brex, Ramp, Wise, Adyen, Revolut)."
    )

    postings, postings_source = _load_postings(
        sheet_url_postings(),
        str(data_dir / "competitor_postings.csv"),
    )
    postings["posted_date"] = pd.to_datetime(postings["posted_date"]).dt.date

    companies = sorted(postings["company"].unique())
    selected = st.multiselect(
        "Filter by company",
        options=companies,
        default=companies,
        help="Hide or show specific Tier 1 companies. All shown by default.",
    )

    filtered = postings[postings["company"].isin(selected)].sort_values(
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
        },
    )

    st.caption(
        f"Showing {len(filtered)} of {len(postings)} postings. "
        f"Source: {postings_source}."
    )

    st.divider()

    st.subheader("Industry Signals")
    st.caption(
        "Tier 1 hiring trends and broader fintech market signals relevant to leadership talent flows."
    )

    insights, insights_source = _load_insights(
        sheet_url_industry_signals(),
        str(data_dir / "insights.json"),
    )

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
