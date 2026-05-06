# Build Spec — Interactive Live Talent Mapping Tool

This is the locked spec for week one. If you're about to build something, read the relevant section here first. The README is for "how do I run this"; this file is for "what are we building and what's out of scope."

The spec is portable — adjust file paths or naming if your local conventions differ, but don't change scope without team agreement.

---

## Goal

Build a local web app that produces a dynamic, shareable talent market brief for executive searches. Used by the Leadership Recruiting team at Affirm to give stakeholders (hiring managers, recruiting leadership, execs) a high-signal research artifact before the first calibration call and throughout a search.

The tool has three read-only analytical sections + one interactive sourcing engine, runs locally as a Streamlit app, and can publish a snapshot to a Notion page on demand.

## Audience

Built by sourcers and recruiters (non-engineers). Code should be readable, well-commented, and the README should document how a non-engineer can refresh data weekly.

## Tech stack

- Python 3.11+
- Streamlit for the local web UI
- Pandas for data manipulation
- Plotly for heat maps and charts
- `notion-client` for publishing to Notion via API
- `python-dotenv` for credentials
- CSV and JSON files for stored datasets (committed to git)

## Architecture

```text
[Curated CSV/JSON datasets in /data]
            ↓
   [Streamlit app: app.py]
            ↓
[Publish to Notion button → notion-client → Notion page]

[Weekly refresh: scripts/refresh_data.py — manual run, no automation]
```

- All data lives in `/data/` as CSV or JSON files, hand-curated and versioned in git.
- Streamlit reads the static datasets at runtime.
- A "Publish to Notion" button serializes the current snapshot to a Notion page.
- No live API calls during normal use. No scraping during the demo.

---

## Locked scope (week 1, non-negotiable)

- **Companies (Tier 1 only):** Stripe, Block, Brex, Ramp, Wise, Adyen, Revolut. No Tier 2 or Tier 3.
- **Levels:** Senior Director, Vice President (VP), Senior Vice President (SVP). Skip Director and below. Skip C-suite. Skip ICs.
- **Functions:** Operations, Technical Programs, Product, Engineering, Revenue, Finance. Six total.
- **Geography:** US-first. London optional in the data model.
- **X-Ray strings:** LinkedIn only.
- **Deliverable surface:** Local Streamlit app + Notion publishing endpoint.

---

## Section 1 — Competitive Landscape

What types of senior roles each Tier 1 competitor is currently hiring for.

- For each of the seven companies, render a table of posted SrDir/VP/SVP roles with columns: `title`, `function`, `level`, `location`, `posted_date`.
- Render an "Industry Signals" panel with 3–5 manually curated insights below the table. Mix Tier 1 hiring trends with broader fintech industry news (e.g., "Block named to TIME's most influential finance companies for 2026", "PayPal spins out Venmo as a standalone unit"). Insights don't have to be drawn solely from the Tier 1 postings dataset — public market signals about non-Tier 1 fintechs are in-scope as long as they're relevant to leadership talent flows.
- Data source: public job boards, manually curated weekly.

Storage: `data/competitor_postings.csv`, `data/insights.json`.

## Section 2 — Hiring Difficulty Heat Map

A 6×3 grid (functions × levels) showing hiring difficulty as a Plotly heat map.

Difficulty score is a composite of two inputs:

1. **Talent pool size** — count of qualified candidates in geo, manually pulled from LinkedIn Recruiter.
2. **Outreach response rates** — pulled from Gem, manually exported.

Cells are colored low / medium / high based on the composite. Hovering on a cell shows the two component values that drive the score.

> **Open decision:** the exact formula combining the two inputs into a low/medium/high score is TBD. Propose one in the first PR that builds Section 2; the team approves before implementation.

Storage: `data/talent_pool.csv`, `data/gem_response_rates.csv`.

## Section 3 — Compensation Benchmarking

A 6×3 grid (functions × levels) showing comp ranges.

- **Source:** manually curated from public sources only — public job postings, Levels.fyi (where applicable), executive hire press coverage.
- **Hard rule: NO internal Affirm compensation data.** All comp data must be public. Enforced in the data schema (see "Constraints to enforce in code" below).
- Display per cell: median total cash + median equity grant + P25–P75 range.
- Each cell shows a "View sources" link that lists the postings or articles that informed it.

Storage: `data/comp_benchmarks.csv`.

## Section 4 — Role-Based Sourcing Engine (interactive)

The user picks a title from a dropdown of 25–30 pre-defined leadership titles (across the six functions at SrDir/VP/SVP) and types a location. The tool renders:

1. **Tier 1 companies hiring this role:** filtered list from Section 1 data.
2. **Mini heat map:** the row from Section 2 for this function and level.
3. **Comp benchmarks:** the cell from Section 3 for this function and level.
4. **LinkedIn Boolean X-Ray search string:** generated from a template.

### Dropdown titles

Build out to 25–30 titles across all six functions, balanced. Examples:

- **Engineering:** Senior Director of Engineering, VP of Engineering, SVP of Engineering, Senior Director of Platform Engineering, VP of Infrastructure
- **Product:** Senior Director of Product, VP of Product, SVP of Product, Senior Director of Product (Payments)
- **Finance:** Senior Director of FP&A, VP of Finance, VP of Treasury, SVP of Finance
- **Operations:** Senior Director of Risk Operations, VP of Operations, SVP of Operations
- **Technical Programs:** Senior Director of TPM, VP of Technical Program Management
- **Revenue:** Senior Director of Sales, VP of Revenue, SVP of Revenue, VP of Partnerships

> **Open decision:** finalize the exact 25–30 title list in the first PR that builds Section 4.

### LinkedIn X-Ray template

```text
site:linkedin.com/in ("VP" OR "Vice President" OR "SVP" OR "Senior Vice President" OR "Senior Director") "<function_keyword>" ("<company1>" OR "<company2>" OR ...) "<location>"
```

The function keyword and company list are populated from the dropdown selection. The location is the user's text input.

---

## Notion publisher

A "Publish to Notion" button at the top of the Streamlit app:

- Reads `NOTION_TOKEN` and `NOTION_PARENT_PAGE_ID` from `.env` (never hardcoded).
- Pushes the current dataset snapshot to the designated parent Notion page.
- Creates a child page titled `Talent Map — [date]` with four section headings and embedded tables.
- Returns a clickable link to the new Notion page after publishing.

---

## Data sources reference

| Section | Source | Storage |
|---|---|---|
| Competitor postings | Public job boards (Greenhouse public boards for Stripe/Brex/Ramp/Block; Workday/Lever for others). Manually curated weekly. | `data/competitor_postings.csv` |
| Trend insights | Manually written based on competitor postings + news. | `data/insights.json` |
| Talent pool sizes | Manual LinkedIn Recruiter searches by title × geo × company. Recorded in CSV. | `data/talent_pool.csv` |
| Outreach response rates | Gem dashboards, manually exported. | `data/gem_response_rates.csv` |
| Comp benchmarks | Manually curated from public job postings, Levels.fyi, executive hire press coverage. | `data/comp_benchmarks.csv` |

---

## Build sequence (week 1)

1. **Day 1:** Repo scaffold, `requirements.txt`, `.env.example`, `.gitignore`, README. Streamlit "hello world" with four section tabs. ← *this PR.*
2. **Day 2:** Curate initial datasets in CSVs. Use clearly-marked placeholder values where real data isn't ready yet.
3. **Day 3:** Build Sections 1, 2, 3 — read CSVs, render tables and Plotly heat map.
4. **Day 4:** Build Section 4 (sourcing engine) — dropdown + X-Ray template generator + cross-section data lookups.
5. **Day 5:** Notion publisher + polish. End-of-week demo.

---

## Non-goals (do not build)

- Live web scraping during page load
- Real-time API integration with LinkedIn, Gem, Greenhouse, or vendors
- Free-text role search in the sourcing engine (dropdown only)
- Tier 2 or Tier 3 company data
- Director-level, manager-level, or C-suite analysis
- Internal Affirm compensation data of any kind
- IC-level data (Staff, Principal, etc.)
- Multi-platform X-Ray strings (LinkedIn only)

---

## Constraints to enforce in code

- The `comp_benchmarks.csv` schema must include a `source_type` column restricted to: `public_posting`, `levels_fyi`, `news_article`, `manual_research`. Reject or warn on any row with `source_type = internal`.
- All candidate-related data must be anonymized. **No PII** (names, emails, phone numbers) in any committed dataset.
- Credentials (Notion integration token, parent page ID) loaded only from `.env`. `.env` must be in `.gitignore`. Never hardcoded.
- README must include a "How to refresh data weekly" section written for non-engineers, plus a "How to add a new role title to the dropdown" section.

---

## Definition of done (week 1 demo)

- App runs locally via `streamlit run app.py`.
- All four sections render with real or clearly-marked placeholder data.
- Sourcing engine dropdown produces a valid LinkedIn boolean string for every option.
- "Publish to Notion" button creates a snapshot page in a designated test Notion workspace.
- README documents setup, refresh workflow, and dropdown maintenance.
- All datasets committed to git; no credentials committed.
