"""Section 1 — Competitive Landscape.

Renders, for each Tier 1 company, a table of currently posted Senior Director,
Vice President, and Senior Vice President roles plus a curated "Industry
Signals" panel that mixes Tier 1 hiring trends with broader fintech industry
news.

Data sources:
  - data/competitor_postings.csv  (columns: company, title, function, level, location, posted_date)
  - data/insights.json            (list of {title, body})
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st


def render(data_dir: Path) -> None:
    st.header("Competitive Landscape")
    st.caption(
        "Senior Director, Vice President, and Senior Vice President roles posted at Tier 1 fintech competitors "
        "(Stripe, Block, Brex, Ramp, Wise, Adyen, Revolut)."
    )

    postings = pd.read_csv(data_dir / "competitor_postings.csv")
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

    st.caption(f"Showing {len(filtered)} of {len(postings)} postings.")

    st.divider()

    st.subheader("Industry Signals")
    st.caption(
        "Tier 1 hiring trends and broader fintech market signals relevant to leadership talent flows."
    )

    insights_path = data_dir / "insights.json"
    with insights_path.open() as f:
        insights = json.load(f)

    for insight in insights:
        st.markdown(f"**{insight['title']}**  \n{insight['body']}")
