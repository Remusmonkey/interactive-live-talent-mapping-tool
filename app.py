"""Streamlit entry point for the Interactive Live Talent Mapping Tool.

Run locally with:

    streamlit run app.py

The app has four section tabs (see BUILD_SPEC.md for full requirements) plus a
"Publish to Notion" button. Each section's logic lives in `src/sections/` so
section owners can iterate independently without touching this file.
"""

from datetime import date, datetime
from pathlib import Path

import pandas as pd
import streamlit as st

from src.sections import (
    competitive_landscape,
    comp_benchmarks,
    difficulty_heatmap,
    sourcing_engine,
)
from src.notion_publisher import publish_snapshot

DATA_DIR = Path(__file__).parent / "data"

# Affirm brand palette (see .streamlit/config.toml for the locked values).
INDIGO = "#4A4AF4"
DARK_INDIGO = "#0A0340"
AFFIRM_BLACK = "#13131F"


def _inject_montserrat() -> None:
    """Inject Montserrat as the app-wide font via Google Fonts.

    Calibre is Affirm's actual brand font but it's paid (Klim Type Foundry).
    Montserrat is a freely licensed substitute with similar geometric feel.
    """
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap');

        html, body, [class*="css"], [class*="st-"],
        h1, h2, h3, h4, h5, h6, p, label, span, div,
        .stMarkdown, .stCaption, .stText, .stButton button {
            font-family: 'Montserrat', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _hide_dataframe_column_menu() -> None:
    """Hide the per-column 3-dot menu in st.dataframe widgets.

    Streamlit decorates that menu (Sort, Pin, Hide, Filter) with Material
    Symbols icons loaded from Google Fonts. On corporate networks where
    fonts.gstatic.com is blocked or filtered, the icon font fails to load
    and raw icon names render alongside the labels (e.g., "arrow upward
    Sort ascending"). The 6-filter row above the postings table covers
    filtering; clicking the column name still sorts. So hiding the
    broken menu is a clean fallback.

    Selectors target multiple known Streamlit versions; case-insensitive
    matching makes the rule robust to internal class/test-id renames.
    """
    st.markdown(
        """
        <style>
        [data-testid="stDataFrame"] button[aria-label*="column" i],
        [data-testid="stDataFrame"] [data-testid*="ColumnMenu" i],
        [data-testid="stDataFrame"] [class*="ColumnMenu" i],
        [data-testid="stDataFrame"] [class*="column-menu" i] {
            display: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _data_as_of(data_dir: Path) -> date:
    """Return the most recent date across postings + comp benchmarks.

    Used as the global "data freshness" timestamp in the header.
    """
    postings = pd.read_csv(data_dir / "competitor_postings.csv")
    comp = pd.read_csv(data_dir / "comp_benchmarks.csv")
    latest_posting = pd.to_datetime(postings["posted_date"]).max().date()
    latest_comp = pd.to_datetime(comp["as_of_date"]).max().date()
    return max(latest_posting, latest_comp)


def _render_footer() -> None:
    """App-wide footer with project metadata."""
    today = datetime.now().strftime("%B %d, %Y")
    st.markdown(
        f"""
        <div style='margin-top:48px;padding-top:24px;border-top:1px solid #E5E5E5;
                    color:{AFFIRM_BLACK};font-size:0.8rem;line-height:1.6;text-align:center;'>
            <div style='font-weight:600;color:{DARK_INDIGO};'>
                Interactive Live Talent Mapping Tool
            </div>
            <div>
                Affirm Leadership Recruiting · Local demo · Generated {today}
            </div>
            <div style='color:#888;'>
                See <code>BUILD_SPEC.md</code> for scope · No internal Affirm data
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(
        page_title="Talent Mapping Tool",
        page_icon=":mag:",
        layout="wide",
    )

    _inject_montserrat()
    _hide_dataframe_column_menu()

    as_of = _data_as_of(DATA_DIR)
    st.markdown(
        f"<div style='color:#888;font-size:0.85rem;letter-spacing:0.05em;text-transform:uppercase;'>"
        f"Data as of {as_of.strftime('%B %d, %Y')}</div>",
        unsafe_allow_html=True,
    )

    st.title("Interactive Live Talent Mapping Tool")

    st.markdown(
        f"<div style='font-size:1.05rem;line-height:1.6;color:{AFFIRM_BLACK};margin-bottom:8px;'>"
        "A weekly-refreshed view of the senior leadership talent market across our seven Tier 1 fintech "
        "competitors. Use it to size the candidate pool, gauge outreach difficulty, benchmark comp, and "
        "generate sourcing strings for any function and level — all from one place, before the first "
        "calibration call."
        "</div>",
        unsafe_allow_html=True,
    )
    st.caption(
        "Senior Director · Vice President · Senior Vice President · "
        "Operations · Technical Programs · Product · Engineering · Revenue · Finance"
    )

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

    _render_footer()


if __name__ == "__main__":
    main()
