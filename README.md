# Interactive Live Talent Mapping Tool

A local Streamlit app that produces a dynamic, shareable talent market brief for executive searches. Built for the Leadership Recruiting team at Affirm to give stakeholders a high-signal research artifact before the first calibration call and throughout a search.

Reference inspiration: <https://crafttalentmap.netlify.app/>

## What it does

- **Section 1 — Competitive Landscape:** roles each Tier 1 competitor is hiring for, plus curated trend notes
- **Section 2 — Hiring Difficulty Heat Map:** 6 functions × 3 levels, colored by a composite difficulty score
- **Section 3 — Compensation Benchmarking:** public-source-only comp ranges per function × level
- **Section 4 — Role-Based Sourcing Engine:** pick a title + location → get competitor list, mini heat map, comp range, and a LinkedIn X-Ray string
- **Publish to Notion:** one-click snapshot to a designated Notion page

## Quick start

Requires Python 3.11+ and `gh` (see [SETUP.md](./SETUP.md) if you haven't onboarded yet).

```bash
# Clone and enter the repo
git clone https://github.com/Remusmonkey/interactive-live-talent-mapping-tool.git
cd interactive-live-talent-mapping-tool

# Create a virtual environment and install deps
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure Notion credentials (optional — only needed for "Publish to Notion")
cp .env.example .env
# Then edit .env and fill in NOTION_TOKEN and NOTION_PARENT_PAGE_ID

# Run the app
streamlit run app.py
```

Streamlit opens the app in your browser at `http://localhost:8501`.

## Refreshing data weekly (for non-engineers)

All datasets live in `data/` as CSV or JSON files. To refresh:

1. Open the relevant CSV (e.g., `data/competitor_postings.csv`) in Excel, Google Sheets, or any text editor.
2. Replace or append rows. Keep the column headers exactly as they are.
3. Save the file (Excel: "Save As" → CSV UTF-8).
4. Commit and push:

   ```bash
   git checkout -b chore/weekly-refresh-YYYY-MM-DD
   git add data/
   git commit -m "chore: weekly data refresh YYYY-MM-DD"
   git push -u origin chore/weekly-refresh-YYYY-MM-DD
   ```

5. Open a PR. Once merged, anyone running the app sees the updated data.

See [BUILD_SPEC.md](./BUILD_SPEC.md) for the full data dictionary (which file maps to which section).

## Adding a new role title to the dropdown

Role titles live in `src/sections/sourcing_engine.py` (constant `DROPDOWN_TITLES` — added when Section 4 is built). To add one:

1. Edit `DROPDOWN_TITLES` and append the new title with its function and level.
2. Confirm a corresponding row exists in `data/comp_benchmarks.csv` and `data/talent_pool.csv` for that function × level combo (otherwise the section will show "no data").
3. Open a PR.

## Project status

**Day 1 — scaffold complete.** Sections render placeholder content. Real implementations land per the build sequence in [BUILD_SPEC.md](./BUILD_SPEC.md).

## Documentation map

| File | What it's for |
|---|---|
| [README.md](./README.md) | How to run the app and refresh data (this file) |
| [BUILD_SPEC.md](./BUILD_SPEC.md) | Locked scope, data schemas, build sequence, non-goals, code constraints |
| [SETUP.md](./SETUP.md) | First-time team onboarding (GitHub auth, repo access, daily workflow) |

## Contributing

Branch + PR workflow. See [SETUP.md](./SETUP.md) for daily flow and team agreements.
