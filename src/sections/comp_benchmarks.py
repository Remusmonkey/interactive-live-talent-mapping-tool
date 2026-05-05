"""Section 3 — Compensation Benchmarking.

A 6 functions x 3 levels grid of comp ranges sourced from public data only.

Hard constraint: NO internal Affirm compensation data. The data schema enforces
this via a `source_type` column restricted to public values; rows tagged
`internal` are rejected.

Owner: TBD. Implementation lands per BUILD_SPEC.md, Day 3.
"""

from pathlib import Path

import streamlit as st

ALLOWED_SOURCE_TYPES = {
    "public_posting",
    "levels_fyi",
    "news_article",
    "manual_research",
}


def render(data_dir: Path) -> None:
    st.header("Compensation Benchmarking")
    st.caption(
        "Median total cash + median equity grant + P25-P75 range, "
        "sourced from public postings, Levels.fyi, and news coverage. "
        "Internal Affirm data is never displayed."
    )
    st.info(
        "Section 3 scaffold — implementation pending (see BUILD_SPEC.md, Day 3). "
        "Data file: `data/comp_benchmarks.csv`."
    )
