# Data — Talent Mapping Tool

All datasets here are **manually curated** from public sources only. No PII, no internal Affirm compensation data, no scraped vendor data. See [`../BUILD_SPEC.md`](../BUILD_SPEC.md) for the full constraints.

## Files

| File | Section | Refresh cadence | Source |
|---|---|---|---|
| `competitor_postings.csv` | 1 — Competitive Landscape | Weekly | Public job boards (Greenhouse / Workday / Lever) |
| `insights.json` | 1 — Trends panel | Weekly | Manually written |
| `talent_pool.csv` | 2 — Difficulty heat map | Weekly | LinkedIn Recruiter (manual) |
| `comp_inflation.csv` | 2 — Difficulty heat map | Monthly | Public job postings + news |
| `gem_response_rates.csv` | 2 — Difficulty heat map | Weekly | Gem dashboard export |
| `comp_benchmarks.csv` | 3 — Comp benchmarking | Bi-weekly | Public postings, Levels.fyi, news |

## Placeholder rows

Every CSV in this directory currently contains one or more rows with `placeholder` in the data — they exist so the app runs end-to-end on Day 1 before real curation is done. Replace them as part of the Day 2 data-curation pass.

## Refresh workflow

See the "Refreshing data weekly" section in [`../README.md`](../README.md) for the non-engineer-friendly walkthrough.
