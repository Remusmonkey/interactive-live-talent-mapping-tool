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

    header_cells_html = []
    header_labels = ["Function", *LEVELS]
    for idx, label in enumerate(header_labels):
        is_last = idx == len(header_labels) - 1
        right_border = "border-right:1px solid #FFFFFF;" if not is_last else ""
        header_cells_html.append(
            f"<th style='background:#4A4AF4;color:#FFFFFF;padding:12px 14px;"
            f"text-align:left;font-weight:600;font-size:0.9rem;"
            f"border-bottom:2px solid #FFFFFF;{right_border}'>{label}</th>"
        )
    header_html = "<tr>" + "".join(header_cells_html) + "</tr>"

    body_rows = []
    for func in FUNCTIONS:
        row_cells = [
            f"<td style='background:#4A4AF4;color:#FFFFFF;padding:12px 14px;"
            f"font-weight:600;font-size:0.9rem;border:1px solid #FFFFFF;vertical-align:middle;'>{func}</td>"
        ]
        for level in LEVELS:
            cell = df[(df["function"] == func) & (df["level"] == level)]
            if cell.empty:
                row_cells.append(
                    "<td style='background:#9DADF9;color:#13131F;padding:12px 14px;"
                    "font-style:italic;font-size:0.85rem;border:1px solid #FFFFFF;'>no data</td>"
                )
                continue
            row = cell.iloc[0]
            cash_median = _format_k(row["total_cash_median"])
            cash_p25 = _format_k(row["total_cash_p25"])
            cash_p75 = _format_k(row["total_cash_p75"])
            equity = _format_k(row["equity_grant_median"])
            source_url = str(row.get("source_url", "")).strip()
            source_type = str(row.get("source_type", "")).strip()
            source_html = ""
            if source_url and source_url.lower() != "nan":
                source_html = (
                    f"<div style='font-size:0.7rem;margin-top:6px;'>"
                    f"<a href='{source_url}' target='_blank' "
                    f"style='color:#0A0340;text-decoration:underline;opacity:0.75;'>"
                    f"Source: {source_type} &#8599;</a></div>"
                )
            row_cells.append(
                f"<td style='background:#9DADF9;padding:12px 14px;border:1px solid #FFFFFF;"
                f"vertical-align:top;line-height:1.5;'>"
                f"<div style='font-size:1.05rem;font-weight:700;color:#0A0340;'>{cash_median} cash</div>"
                f"<div style='font-size:0.8rem;color:#13131F;'>{cash_p25}–{cash_p75} range</div>"
                f"<div style='font-size:0.9rem;color:#0A0340;font-weight:500;margin-top:2px;'>"
                f"{equity} equity</div>"
                f"{source_html}"
                f"</td>"
            )
        body_rows.append("<tr>" + "".join(row_cells) + "</tr>")

    table_html = (
        "<div style='overflow-x:auto;margin:8px 0 16px 0;'>"
        "<table style='width:100%;border-collapse:collapse;font-family:inherit;'>"
        f"<thead>{header_html}</thead>"
        f"<tbody>{''.join(body_rows)}</tbody>"
        "</table></div>"
    )
    st.markdown(table_html, unsafe_allow_html=True)

    st.caption(
        f"Sources: {df['source_type'].value_counts().to_dict()}. "
        "All rows reference publicly available postings, Levels.fyi entries, "
        "or news articles."
    )
