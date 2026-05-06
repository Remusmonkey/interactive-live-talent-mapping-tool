"""Section 2 — Hiring Difficulty Heat Map.

A 6 functions x 3 levels Plotly heat map. Difficulty is a composite of:
  1. Talent pool size  (data/talent_pool.csv)
  2. Outreach response (data/gem_response_rates.csv)

Composite formula (locked): tertile bucket sum.

  For each input independently, rank all 18 cells into thirds:
    Bottom 6 cells -> 1 point
    Middle 6 cells -> 2 points
    Top 6 cells    -> 3 points

  Sum each cell's two tertile scores (range 2-6) and bucket:
    sum <= 3  -> High difficulty
    sum  = 4  -> Medium difficulty
    sum >= 5  -> Low difficulty

  Chosen for explainability over statistical smoothness — see BUILD_SPEC.md
  Section 2 for the full rationale.

Owner: TBD. Implementation lands per BUILD_SPEC.md, Day 3.
"""

from pathlib import Path

import streamlit as st


def render(data_dir: Path) -> None:
    st.header("Hiring Difficulty Heat Map")
    st.caption("Composite difficulty score by function x level (low / medium / high).")
    st.info(
        "Section 2 scaffold — implementation pending (see BUILD_SPEC.md, Day 3). "
        "Data files: `data/talent_pool.csv`, `data/gem_response_rates.csv`."
    )
