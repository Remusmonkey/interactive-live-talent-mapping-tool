"""Section 4 — Role-Based Sourcing Engine (interactive).

Dropdown of 25-30 leadership titles + location text input.

Renders four sub-panels:
  1. Tier 1 companies hiring this role (filtered from Section 1 data).
  2. Mini heat map row from Section 2 for this function x level.
  3. Comp benchmark cell from Section 3 for this function x level.
  4. LinkedIn Boolean X-Ray search string (see src/xray.py).

The exact 25-30 titles are an open decision — finalize in the PR that builds
this section. Once finalized, list them in `DROPDOWN_TITLES` below; non-engineer
teammates can extend the list per the README.

Owner: TBD. Implementation lands per BUILD_SPEC.md, Day 4.
"""

from pathlib import Path

import streamlit as st

DROPDOWN_TITLES: list[dict[str, str]] = [
    # {"title": "VP of Engineering", "function": "Engineering", "level": "VP"},
    # ... finalize during Section 4 build (target: 25-30 entries across the six functions).
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
