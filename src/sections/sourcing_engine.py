"""Section 4 — Role-Based Sourcing Engine (interactive).

Dropdown of leadership titles + location text input.

Renders four sub-panels:
  1. Tier 1 companies hiring this role (filtered from Section 1 data).
  2. Mini heat map row from Section 2 for this function x level.
  3. Comp benchmark cell from Section 3 for this function x level.
  4. LinkedIn Boolean X-Ray search string (see src/xray.py).

`DROPDOWN_TITLES` below is seeded from the unique titles found in
`data/competitor_postings.csv` (18 entries). BUILD_SPEC targets 25-30; expand
with industry-standard titles to hit that range as the postings dataset grows.
Non-engineer teammates can extend the list per the README.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from src.sections.difficulty_heatmap import TIER_COLORS, _build_dataframe as _build_heatmap_df
from src.xray import build_linkedin_xray

DROPDOWN_TITLES: list[dict[str, str]] = [
    {"title": "Senior Director of Risk Operations", "function": "Operations", "level": "Senior Director"},
    {"title": "Vice President of Operations", "function": "Operations", "level": "Vice President"},
    {"title": "Senior Director of Technical Program Management", "function": "Technical Programs", "level": "Senior Director"},
    {"title": "Vice President of Technical Program Management", "function": "Technical Programs", "level": "Vice President"},
    {"title": "Senior Director of Product", "function": "Product", "level": "Senior Director"},
    {"title": "Senior Director of Product (Payments)", "function": "Product", "level": "Senior Director"},
    {"title": "Vice President of Product", "function": "Product", "level": "Vice President"},
    {"title": "Senior Director of Engineering", "function": "Engineering", "level": "Senior Director"},
    {"title": "Vice President of Engineering", "function": "Engineering", "level": "Vice President"},
    {"title": "Vice President of Infrastructure", "function": "Engineering", "level": "Vice President"},
    {"title": "Senior Vice President of Engineering", "function": "Engineering", "level": "Senior Vice President"},
    {"title": "Senior Director of Partnerships", "function": "Revenue", "level": "Senior Director"},
    {"title": "Senior Director of Sales", "function": "Revenue", "level": "Senior Director"},
    {"title": "Vice President of Partnerships", "function": "Revenue", "level": "Vice President"},
    {"title": "Vice President of Revenue", "function": "Revenue", "level": "Vice President"},
    {"title": "Senior Vice President of Revenue", "function": "Revenue", "level": "Senior Vice President"},
    {"title": "Senior Director of Financial Planning & Analysis", "function": "Finance", "level": "Senior Director"},
    {"title": "Vice President of Finance", "function": "Finance", "level": "Vice President"},
]

TIER_1_COMPANIES = ["Stripe", "Block", "Brex", "Ramp", "Wise", "Adyen", "Revolut"]
LEVELS = ["Senior Director", "Vice President", "Senior Vice President"]


def _function_keyword(title: str) -> str:
    """Strip the level prefix from a title to get the substantive specialty."""
    return title.split(" of ", 1)[1] if " of " in title else title


def _format_k(amount: float) -> str:
    if amount >= 1_000_000:
        return f"${amount / 1_000_000:.1f}M"
    return f"${amount / 1_000:.0f}K"


def render(data_dir: Path) -> None:
    st.header("Role-Based Sourcing Engine")
    st.caption(
        "Pick a leadership title and a location, then get a competitor list, "
        "difficulty snapshot, comp range, and a LinkedIn X-Ray search string."
    )

    title_options = [entry["title"] for entry in DROPDOWN_TITLES]
    title_lookup = {entry["title"]: entry for entry in DROPDOWN_TITLES}

    col_title, col_location = st.columns([2, 1])
    with col_title:
        selected_title = st.selectbox(
            "Leadership title",
            options=title_options,
            index=title_options.index("Vice President of Engineering"),
        )
    with col_location:
        location = st.text_input("Location", value="United States", help="City, region, or country.")

    entry = title_lookup[selected_title]
    func, level = entry["function"], entry["level"]
    keyword = _function_keyword(selected_title)

    st.divider()

    st.subheader(f"1. Tier 1 companies hiring {selected_title}")
    postings = pd.read_csv(data_dir / "competitor_postings.csv")
    postings["posted_date"] = pd.to_datetime(postings["posted_date"]).dt.date
    matching = postings[(postings["function"] == func) & (postings["level"] == level)]
    if matching.empty:
        st.info(
            f"No Tier 1 companies have an active {func} / {level} posting in our weekly snapshot. "
            "This often happens for SVP roles, which are filled via executive search rather than public postings."
        )
    else:
        st.dataframe(
            matching[["company", "title", "location", "posted_date"]].sort_values("posted_date", ascending=False),
            use_container_width=True,
            hide_index=True,
            column_config={
                "company": st.column_config.TextColumn("Company"),
                "title": st.column_config.TextColumn("Title", width="large"),
                "location": st.column_config.TextColumn("Location"),
                "posted_date": st.column_config.DateColumn("Posted"),
            },
        )

    st.divider()

    st.subheader(f"2. Difficulty snapshot — {func}")
    heatmap_df = _build_heatmap_df(data_dir)
    func_rows = heatmap_df[heatmap_df["function"] == func]
    diff_cols = st.columns(3)
    for col, row_level in zip(diff_cols, LEVELS):
        cell = func_rows[func_rows["level"] == row_level].iloc[0]
        is_selected = row_level == level
        border = "3px solid #4A4AF4" if is_selected else "1px solid #E5E5E5"
        col.markdown(
            f"<div style='border:{border};border-radius:8px;padding:12px;text-align:center;background:#FFFFFF;'>"
            f"<div style='font-size:0.85rem;color:#13131F;margin-bottom:4px;'>{row_level}</div>"
            f"<div style='display:inline-block;background:{TIER_COLORS[cell['tier']]};color:white;font-weight:600;padding:4px 12px;border-radius:4px;margin-bottom:8px;'>{cell['tier']}</div>"
            f"<div style='font-size:0.8rem;color:#13131F;'>Pool: {int(cell['pool_size']):,}</div>"
            f"<div style='font-size:0.8rem;color:#13131F;'>Reply: {cell['response_rate_pct']:.1f}%</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.divider()

    st.subheader(f"3. Comp benchmark — {func} / {level}")
    comp_df = pd.read_csv(data_dir / "comp_benchmarks.csv")
    comp_cell = comp_df[(comp_df["function"] == func) & (comp_df["level"] == level)]
    if comp_cell.empty:
        st.info("No comp benchmark on file for this function and level.")
    else:
        comp = comp_cell.iloc[0]
        cash_median = _format_k(comp["total_cash_median"])
        cash_p25 = _format_k(comp["total_cash_p25"])
        cash_p75 = _format_k(comp["total_cash_p75"])
        equity = _format_k(comp["equity_grant_median"])
        comp_left, comp_right = st.columns(2)
        with comp_left:
            st.metric("Median total cash", cash_median, help=f"P25–P75 range: {cash_p25}–{cash_p75}")
        with comp_right:
            st.metric("Median equity grant", equity, help=f"Source: {comp['source_type']}")
        st.caption(
            f"P25–P75 cash range: **{cash_p25}–{cash_p75}** · "
            f"Source: `{comp['source_type']}` · As of {comp['as_of_date']}"
        )

    st.divider()

    st.subheader("4. LinkedIn X-Ray search string")
    xray = build_linkedin_xray(
        function_keyword=keyword,
        companies=TIER_1_COMPANIES,
        location=location or "United States",
    )
    st.caption(
        f"Searches LinkedIn for {keyword} leaders at the seven Tier 1 companies in your location. "
        "Copy and paste into Google to run."
    )
    st.code(xray, language="text")
