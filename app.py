"""Streamlit entry point for the Interactive Live Talent Mapping Tool.

Run locally with:

    streamlit run app.py

The app has four section tabs (see BUILD_SPEC.md for full requirements) plus a
"Publish to Notion" button. Each section's logic lives in `src/sections/` so
section owners can iterate independently without touching this file.
"""

from pathlib import Path

import streamlit as st

from src.sections import (
    competitive_landscape,
    comp_benchmarks,
    difficulty_heatmap,
    sourcing_engine,
)
from src.notion_publisher import publish_snapshot

DATA_DIR = Path(__file__).parent / "data"


def main() -> None:
    st.set_page_config(
        page_title="Talent Mapping Tool",
        page_icon=":mag:",
        layout="wide",
    )

    st.title("Interactive Live Talent Mapping Tool")
    st.caption(
        "Tier 1 competitive landscape, hiring difficulty, comp benchmarks, "
        "and a role-based sourcing engine. Local read-only view + Notion publishing."
    )

    # Notion publishing lives at the top so it's always one click away.
    publish_col, _spacer = st.columns([1, 4])
    with publish_col:
        if st.button("Publish snapshot to Notion", type="primary"):
            with st.spinner("Publishing..."):
                result = publish_snapshot(DATA_DIR)
            if result.get("ok"):
                st.success(f"Published. [Open in Notion]({result['url']})")
            else:
                st.error(result.get("error", "Publishing failed."))

    tab_landscape, tab_heatmap, tab_comp, tab_sourcing = st.tabs(
        [
            "1. Competitive Landscape",
            "2. Hiring Difficulty",
            "3. Comp Benchmarks",
            "4. Sourcing Engine",
        ]
    )

    with tab_landscape:
        competitive_landscape.render(DATA_DIR)
    with tab_heatmap:
        difficulty_heatmap.render(DATA_DIR)
    with tab_comp:
        comp_benchmarks.render(DATA_DIR)
    with tab_sourcing:
        sourcing_engine.render(DATA_DIR)


if __name__ == "__main__":
    main()
