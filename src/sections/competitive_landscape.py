"""Section 1 — Competitive Landscape.

Renders, for each Tier 1 company, a table of currently posted SrDir/VP/SVP
roles plus a curated "Industry Signals" panel that mixes Tier 1 hiring
trends with broader fintech industry news.

Data sources:
  - data/competitor_postings.csv  (columns: company, title, function, level, location, posted_date)
  - data/insights.json            (list of {title, body})

Owner: TBD. Implementation lands per BUILD_SPEC.md, Day 3.
"""

from pathlib import Path

import streamlit as st


def render(data_dir: Path) -> None:
    st.header("Competitive Landscape")
    st.caption(
        "Senior Director, VP, and SVP roles posted at Tier 1 fintech competitors "
        "(Stripe, Block, Brex, Ramp, Wise, Adyen, Revolut)."
    )
    st.info(
        "Section 1 scaffold — implementation pending (see BUILD_SPEC.md, Day 3). "
        "Data files: `data/competitor_postings.csv`, `data/insights.json`."
    )
