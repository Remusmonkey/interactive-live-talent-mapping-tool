"""Section modules for the talent mapping app.

Each section module exposes a single ``render(data_dir: Path) -> None`` function
that reads its data files and draws its UI. ``app.py`` calls them inside tabs.
"""

from . import (
    competitive_landscape,
    comp_benchmarks,
    difficulty_heatmap,
    sourcing_engine,
)

__all__ = [
    "competitive_landscape",
    "comp_benchmarks",
    "difficulty_heatmap",
    "sourcing_engine",
]
