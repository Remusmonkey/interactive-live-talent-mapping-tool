"""Section 2 — Hiring Difficulty Heat Map.

A 6 functions x 3 levels Plotly heat map. Difficulty is a composite of:
  1. Talent pool size      (data/talent_pool.csv)
  2. Comp inflation rate   (data/comp_inflation.csv)
  3. Outreach response     (data/gem_response_rates.csv)

The exact formula combining the three is an open decision — propose it in the
PR that builds this section.

Owner: TBD. Implementation lands per BUILD_SPEC.md, Day 3.
"""

from pathlib import Path

import streamlit as st


def render(data_dir: Path) -> None:
    st.header("Hiring Difficulty Heat Map")
    st.caption("Composite difficulty score by function x level (low / medium / high).")
    st.info(
        "Section 2 scaffold — implementation pending (see BUILD_SPEC.md, Day 3). "
        "Data files: `data/talent_pool.csv`, `data/comp_inflation.csv`, "
        "`data/gem_response_rates.csv`."
    )
