"""Section 3 — Compensation Benchmarking.

A 6 functions x 3 levels grid of comp ranges sourced from public data only.

Hard constraint: NO internal Affirm compensation data. The data schema enforces
this via a `source_type` column restricted to public values; rows tagged
`internal` are rejected.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

ALLOWED_SOURCE_TYPES = {
    "public_posting",
    "levels_fyi",
    "news_article",
    "manual_research",
}

FUNCTIONS = ["Operations", "Technical Programs", "Product", "Engineering", "Revenue", "Finance"]
LEVELS = ["Senior Director", "Vice President", "Senior Vice President"]


def _format_k(amount: float) -> str:
    """Format a dollar amount as a compact $X.XK or $X.XM string."""
    if amount >= 1_000_000:
        return f"${amount / 1_000_000:.1f}M"
    return f"${amount / 1_000:.0f}K"


def render(data_dir: Path) -> None:
    st.header("Compensation Benchmarking")
    st.caption(
        "Median total cash + median equity grant + P25–P75 range, "
        "sourced from public postings, Levels.fyi, and news coverage. "
        "Internal Affirm data is never displayed."
    )

    df = pd.read_csv(data_dir / "comp_benchmarks.csv")

    invalid = df[~df["source_type"].isin(ALLOWED_SOURCE_TYPES)]
    if not invalid.empty:
        st.error(
            f"Rejected {len(invalid)} rows with disallowed source types: "
            f"{sorted(invalid['source_type'].unique())}. "
            "Only public sources may surface in this section."
        )
        df = df[df["source_type"].isin(ALLOWED_SOURCE_TYPES)]

    header_cols = st.columns([1.5, 1.5, 1.5, 1.5])
    header_cols[0].markdown("&nbsp;")
    for col, level in zip(header_cols[1:], LEVELS):
        col.markdown(f"**{level}**")

    st.divider()

    for func in FUNCTIONS:
        row_cols = st.columns([1.5, 1.5, 1.5, 1.5])
        row_cols[0].markdown(f"**{func}**")
        for col, level in zip(row_cols[1:], LEVELS):
            cell = df[(df["function"] == func) & (df["level"] == level)]
            if cell.empty:
                col.markdown("_no data_")
                continue
            row = cell.iloc[0]
            cash_median = _format_k(row["total_cash_median"])
            cash_p25 = _format_k(row["total_cash_p25"])
            cash_p75 = _format_k(row["total_cash_p75"])
            equity = _format_k(row["equity_grant_median"])
            source_url = str(row.get("source_url", "")).strip()
            source_type = str(row.get("source_type", "")).strip()
            source_caption = ""
            if source_url and source_url.lower() != "nan":
                source_caption = (
                    f"<div style='font-size:0.7rem;color:#888;margin-top:4px;'>"
                    f"<a href='{source_url}' target='_blank' style='color:#888;text-decoration:none;'>"
                    f"Source: {source_type} &#8599;</a></div>"
                )
            col.markdown(
                f"<div style='line-height:1.5;padding:6px 0;'>"
                f"<div style='font-size:1.1rem;font-weight:600;color:#0A0340;'>{cash_median} cash</div>"
                f"<div style='font-size:0.85rem;color:#13131F;'>{cash_p25}–{cash_p75} range</div>"
                f"<div style='font-size:0.95rem;color:#4A4AF4;'>{equity} equity</div>"
                f"{source_caption}"
                f"</div>",
                unsafe_allow_html=True,
            )

    st.divider()
    st.caption(
        f"Sources: {df['source_type'].value_counts().to_dict()}. "
        "All rows reference publicly available postings, Levels.fyi entries, "
        "or news articles."
    )
