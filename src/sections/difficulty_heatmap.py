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
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

FUNCTIONS = ["Operations", "Technical Programs", "Product", "Engineering", "Revenue", "Finance"]
LEVELS = ["Senior Director", "Vice President", "Senior Vice President"]

TIER_COLORS = {
    "HIGH": "#E74C3C",
    "MED": "#F4B400",
    "LOW": "#0F9D58",
}
TIER_NUM = {"HIGH": 1, "MED": 2, "LOW": 3}


def _tertile_score(values: pd.Series) -> pd.Series:
    """Rank values descending; top 6 -> 3 pts, middle 6 -> 2 pts, bottom 6 -> 1 pt."""
    ranks = values.rank(ascending=False, method="dense").astype(int)
    return ranks.apply(lambda r: 3 if r <= 6 else (2 if r <= 12 else 1))


def _bucket_tier(composite: int) -> str:
    if composite <= 3:
        return "HIGH"
    if composite == 4:
        return "MED"
    return "LOW"


def _build_dataframe(data_dir: Path) -> pd.DataFrame:
    pool = pd.read_csv(data_dir / "talent_pool.csv")[["function", "level", "pool_size"]]
    resp = pd.read_csv(data_dir / "gem_response_rates.csv")[["function", "level", "response_rate_pct"]]

    merged = pool.merge(resp, on=["function", "level"])
    merged["pool_score"] = _tertile_score(merged["pool_size"])
    merged["resp_score"] = _tertile_score(merged["response_rate_pct"])
    merged["composite"] = merged["pool_score"] + merged["resp_score"]
    merged["tier"] = merged["composite"].apply(_bucket_tier)
    merged["tier_num"] = merged["tier"].map(TIER_NUM)
    return merged


def render(data_dir: Path) -> None:
    st.header("Hiring Difficulty Heat Map")
    st.caption(
        "Composite difficulty score by function x level (low / medium / high). "
        "Computed from talent pool size and outreach response rates using the "
        "tertile bucket sum formula — hover any cell to see the raw inputs."
    )

    df = _build_dataframe(data_dir)

    tier_counts = df["tier"].value_counts().to_dict()
    high = tier_counts.get("HIGH", 0)
    med = tier_counts.get("MED", 0)
    low = tier_counts.get("LOW", 0)
    total = len(df)
    summary_chips = (
        f"<span style='background:{TIER_COLORS['HIGH']};color:white;padding:4px 10px;"
        f"border-radius:4px;font-weight:600;font-size:0.85rem;'>{high} HIGH</span>"
        f"<span style='background:{TIER_COLORS['MED']};color:white;padding:4px 10px;"
        f"border-radius:4px;font-weight:600;font-size:0.85rem;'>{med} MED</span>"
        f"<span style='background:{TIER_COLORS['LOW']};color:white;padding:4px 10px;"
        f"border-radius:4px;font-weight:600;font-size:0.85rem;'>{low} LOW</span>"
    )
    st.markdown(
        f"<div style='display:flex;gap:8px;align-items:center;margin:8px 0 16px 0;'>"
        f"{summary_chips}"
        f"<span style='color:#888;font-size:0.85rem;'>of {total} cells</span>"
        f"</div>",
        unsafe_allow_html=True,
    )

    z_matrix = []
    text_matrix = []
    hover_matrix = []
    for func in FUNCTIONS:
        z_row = []
        text_row = []
        hover_row = []
        for level in LEVELS:
            cell = df[(df["function"] == func) & (df["level"] == level)].iloc[0]
            z_row.append(cell["tier_num"])
            text_row.append(cell["tier"])
            hover_row.append(
                f"<b>{func} · {level}</b><br>"
                f"Difficulty: {cell['tier']}<br>"
                f"Pool size: {int(cell['pool_size']):,}<br>"
                f"Response rate: {cell['response_rate_pct']:.1f}%<br>"
                f"<i>Pool tertile {cell['pool_score']} + Response tertile {cell['resp_score']} = {cell['composite']}</i>"
            )
        z_matrix.append(z_row)
        text_matrix.append(text_row)
        hover_matrix.append(hover_row)

    fig = go.Figure(
        data=go.Heatmap(
            z=z_matrix,
            x=LEVELS,
            y=FUNCTIONS,
            text=text_matrix,
            texttemplate="<b>%{text}</b>",
            textfont={"size": 16, "color": "white"},
            customdata=hover_matrix,
            hovertemplate="%{customdata}<extra></extra>",
            colorscale=[
                [0.0, TIER_COLORS["HIGH"]],
                [0.5, TIER_COLORS["HIGH"]],
                [0.5, TIER_COLORS["MED"]],
                [0.83, TIER_COLORS["MED"]],
                [0.83, TIER_COLORS["LOW"]],
                [1.0, TIER_COLORS["LOW"]],
            ],
            zmin=1,
            zmax=3,
            showscale=False,
            xgap=3,
            ygap=3,
        )
    )

    fig.update_layout(
        height=480,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(side="top", tickfont=dict(size=13)),
        yaxis=dict(autorange="reversed", tickfont=dict(size=13)),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#13131F"),
    )

    st.plotly_chart(fig, use_container_width=True)

    legend_cols = st.columns(3)
    for col, (tier_name, label) in zip(
        legend_cols,
        [("LOW", "Low difficulty"), ("MED", "Medium difficulty"), ("HIGH", "High difficulty")],
    ):
        col.markdown(
            f"<div style='display:flex;align-items:center;gap:8px;'>"
            f"<span style='display:inline-block;width:14px;height:14px;background:{TIER_COLORS[tier_name]};border-radius:3px;'></span>"
            f"<span>{label}</span></div>",
            unsafe_allow_html=True,
        )
