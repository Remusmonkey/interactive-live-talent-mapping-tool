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

Owner: TBD. Implementation lands per BUILD_SPEC.md, Day 4.
"""

from pathlib import Path

import streamlit as st

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


def render(data_dir: Path) -> None:
    st.header("Role-Based Sourcing Engine")
    st.caption(
        "Pick a leadership title and a location, then get a competitor list, "
        "difficulty snapshot, comp range, and a LinkedIn X-Ray search string."
    )
    st.info(
        "Section 4 scaffold — implementation pending (see BUILD_SPEC.md, Day 4). "
        "Dropdown titles to be finalized; X-Ray template lives in `src/xray.py`."
    )
