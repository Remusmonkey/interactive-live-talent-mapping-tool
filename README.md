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

## How we collaborate

Two leadership sourcers maintain this tool: a **code owner** (handles app changes in Cursor) and a **data partner** (helps maintain the weekly data). Both contribute to data; only the code owner touches Python.

| Lane | Who | Where the work happens | How often |
|---|---|---|---|
| **Data** — postings, signals, etc. | Both sourcers | Shared Google Sheet | Weekly |
| **Code** — app behavior, fixes, polish | Code owner + AI in Cursor | This repo | As needed |

The Google Sheet is the day-to-day surface for data. You don't need GitHub or Cursor to update data — you just edit cells in a shared workbook and the app picks up the changes within ~5 minutes.

## Refreshing data weekly (for non-engineers)

Two paths exist depending on whether the Google Sheets backend is set up yet:

### Path A — Google Sheets (preferred, once configured)

1. Open the shared workbook `Talent Mapping Tool — Live Data` in Google Sheets (link in team Slack).
2. Edit the relevant tab:
   - `Postings` — Section 1 competitor postings (one row per posting)
   - `Industry Signals` — Section 1 news/signals panel (title + body)
3. Save (auto-saves).
4. Refresh the running app in your browser. New data appears within 5 minutes (caching window).

No git, no command line. The app reads from the published Sheet URL on a 5-minute cache.

### Path B — Local CSVs (fallback)

If the Sheets backend hasn't been wired up yet, or if you're working offline:

1. Open the relevant CSV (e.g., `data/competitor_postings.csv`) in Excel, Google Sheets, or any text editor.
2. Replace or append rows. Keep the column headers exactly as they are.
3. Save the file (Excel: "Save As" → CSV UTF-8).
4. Refresh the running app — local edits are picked up immediately.
5. (Code owner only) Commit + push the CSV when you want the change to outlive your local copy.

The app will automatically use the Sheet if `SHEET_POSTINGS_URL` and `SHEET_INDUSTRY_SIGNALS_URL` are configured in `.env`, and fall back to local files otherwise.

See [BUILD_SPEC.md](./BUILD_SPEC.md) for the full data dictionary (which file/tab maps to which section).

## Setting up the Google Sheets backend (one-time, code owner)

This is a one-time setup that connects the app to a shared Google Sheet so the data partner can contribute without touching GitHub.

**Auth approach:** Affirm Google Workspace blocks the simpler "publish to web" sharing flow, so the app authenticates via a Google Cloud **service account** that's been explicitly granted read access to the workbook. The Sheet itself stays inside Affirm GWS — only this one service account gets through the door.

### Steps

1. **Create the workbook** in Google Sheets. Name it `Talent Mapping Tool — Live Data`.
2. **Add two tabs to start:**
   - `Postings` — headers: `company, title, function, level, location, posted_date, source_url` (header case doesn't matter; the app normalizes to lowercase)
   - `Industry Signals` — headers: `title, body`
3. **Share the workbook** with the data partner as an editor.
4. **Create a Google Cloud project + service account:**
   - Open [console.cloud.google.com](https://console.cloud.google.com)
   - Create a new project (e.g. `talent-mapping-tool`)
   - Enable the **Google Sheets API** (APIs & Services → Library)
   - Create a service account (APIs & Services → Credentials → + Create Credentials → Service account); skip the optional "grant roles" steps
5. **Download the service account's JSON key:**
   - Click the service account row → Keys tab → Add Key → Create new key → JSON
   - Move the downloaded file to `secrets/google-sheets-key.json` (the `secrets/` folder is gitignored)
6. **Share the workbook with the service account email** as a **Viewer**. The email looks like `<name>@<project>.iam.gserviceaccount.com`. Uncheck "Notify people" before clicking Share.
7. **Get the workbook ID** from the Sheet URL (the long string between `/d/` and `/edit`).
8. **Configure `.env`:** copy `.env.example` to `.env` and fill in `GOOGLE_SHEETS_WORKBOOK_ID` and `GOOGLE_SHEETS_KEY_FILE` (path defaults to `secrets/google-sheets-key.json`).
9. **Restart Streamlit.** Section 1 should now read live from the Sheet. The caption under each block will say `Source: Google Sheets`.

If the caption still says `Local CSV`, the app couldn't reach the Sheet — most common causes are missing/incorrect column headers (see step 2), the JSON key file not being in the right place, or the service account not having been shared on the Sheet (step 6).

## Refreshing competitor postings (Phase 1A + 1B scraper)

The scraper pulls leadership postings (Director, Head of, Senior Director, VP, SVP) from 32 competitor public job boards: 25 hosted on **Greenhouse** + 7 hosted on **Ashby**. Manually triggered — no schedule, no live scraping during page load.

### Running it

```bash
# From the repo root, with the Google Sheets service account configured (see above)
python3 scripts/refresh_postings.py
```

Takes ~20 seconds. Writes to two tabs in your workbook (auto-created on first run):

- **`Scraped — Pending Review`** — every leadership posting found. Sourcers triage here.
- **`Scraper Run Log`** — one row per company per run with counts + any errors. Useful for spotting board breakage.

### Tier-based filtering + sources

Each competitor in `src/data/competitors.json` has a `tier` (broad vs. narrow level filter) and a `source` (which SaaS hosts their public board).

| Tier | Companies | Level filter |
|---|---|---|
| **primary** | Stripe, Brex, Block, Ramp, Sezzle, SoFi, Adyen, Mercury | Director, Senior Director, Head of, VP, SVP |
| **secondary** | Marqeta, Robinhood, Chime, Betterment, Checkr, N26, Nubank, Plaid, Deel, Anthropic, OpenAI, Notion, Harvey, Perplexity, Figma, Asana, Discord, Reddit, Pinterest, Airbnb, Instacart, Lyft, Roblox, Duolingo | Senior Director, Head of, VP, SVP (skip plain Director — too many IC titles at consumer tech) |

| Source | Companies | API endpoint |
|---|---|---|
| **greenhouse** | Stripe, Brex, Block, Sezzle, SoFi, Adyen, Mercury, Marqeta, Robinhood, Chime, Betterment, Checkr, N26, Nubank, Anthropic, Figma, Asana, Discord, Reddit, Pinterest, Airbnb, Instacart, Lyft, Roblox, Duolingo | `boards-api.greenhouse.io/v1/boards/<slug>/jobs` |
| **ashby** | Ramp, Plaid, Deel, OpenAI, Notion, Harvey, Perplexity | `api.ashbyhq.com/posting-api/job-board/<slug>` |

To move a company between tiers or change its source, edit `src/data/competitors.json` — no code change needed.

To **add a new SaaS provider** (e.g., Lever, Workday), see the dev guide in `src/scraper.py`: add a `fetch_<provider>_jobs()` function returning the normalized job dict, register it in `FETCHERS`, then any competitor can declare `"source": "<provider>"`.

### What the scraper does NOT touch

- Affirm's internal Greenhouse ATS (this targets *competitors'* public boards, hosted on Greenhouse the SaaS)
- The `Postings` tab — sourcers manually promote approved rows from Pending Review after triage
- Compensation, talent pool, or any data outside Section 1

### Triage workflow (sourcer)

1. Run the scraper weekly: `python3 scripts/refresh_postings.py`
2. Open the workbook and review the `Scraped — Pending Review` tab
3. For each row: keep, edit (fix function/level), or delete
4. Pay extra attention to rows where `function = Other` — those didn't match any of the six BUILD_SPEC functions (or Growth) and need manual classification
5. Copy approved rows into the `Postings` tab (the one the app reads from)
6. Glance at `Scraper Run Log` for any company with `status != ok` — that means their board is broken or moved off its SaaS provider

### Companies NOT yet on a supported scraper

These competitors run their public boards on different infrastructure and need future scraper work:

- **Workday / their own ATS:** Klarna, Coinbase, Wealthfront, DoorDash, Uber, Shopify, Bill.com, Wise, Revolut, TikTok/ByteDance, Etsy, Scale AI, Rippling, Gusto, Carta, Modern Health (Phase 1C+ — Workday usually requires headless browser; custom ATSes are case-by-case)

## Adding a new role title to the dropdown

Role titles live in `src/sections/sourcing_engine.py` (constant `DROPDOWN_TITLES` — added when Section 4 is built). To add one:

1. Edit `DROPDOWN_TITLES` and append the new title with its function and level.
2. Confirm a corresponding row exists in `data/comp_benchmarks.csv` and `data/talent_pool.csv` for that function × level combo (otherwise the section will show "no data").
3. Open a PR.

## Project status

**Phase 1 — real data rollout in progress.** All four sections render with placeholder/synthetic data today. Section 1 (Competitive Landscape) is the first to move to real data via the Google Sheets backend + a scraper pipeline (see `scripts/refresh_postings.py` once it lands). Sections 2-4 stay on synthetic CSVs until their own phases. See [PROJECT_LOG.md](./PROJECT_LOG.md) for the live working log.

## Documentation map

| File | What it's for |
|---|---|
| [README.md](./README.md) | How to run the app and refresh data (this file) |
| [BUILD_SPEC.md](./BUILD_SPEC.md) | Locked scope, data schemas, build sequence, non-goals, code constraints |
| [PROJECT_LOG.md](./PROJECT_LOG.md) | Living working log — decisions, sessions, recurring issues, open TODOs |
| [SETUP.md](./SETUP.md) | First-time code-owner onboarding (GitHub auth, repo access, daily workflow) |

## Contributing

Branch + PR workflow. See [SETUP.md](./SETUP.md) for daily flow and team agreements.
