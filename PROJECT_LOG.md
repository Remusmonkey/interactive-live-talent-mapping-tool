# Project Working Log

A running record of decisions, problems, and changes for the **Interactive Live Talent Mapping Tool** project. Add new entries as the project progresses — this is meant as a living reference, not a one-time write-up.

---

## Project Snapshot

A Streamlit application for interactive talent mapping, organized into multiple sections (competitive landscape, hiring difficulty heat map, comp benchmarking, sourcing engine, etc.). All datasets are manually curated from public sources only — no PII, no internal compensation data.

- **Repo:** `Remusmonkey/interactive-live-talent-mapping-tool`
- **Spec:** see `BUILD_SPEC.md`
- **Setup:** see `SETUP.md`

## Team & Contribution Pattern

| Contributor | Branch convention | Notes |
|---|---|---|
| Aaron (owner) | works on `main` directly, reviews/merges others | |
| Heather | feature branches off `main` | initially used `verify/heather`, switched to `heather` per cleanup |
| Kyle | feature branches off `main` | first branch was `verify/kyle`; deleted before substantive work |
| Jason | feature branches off `main` | first branch was `verify/jason`; deleted before substantive work |

## Workflow Patterns We've Settled On

- **Always start work from current `main`** — pull latest before branching. Avoids stale-state edits and merge conflicts.
- **One logical commit per piece of work** — makes selective merging (cherry-picking) clean if needed.
- **Merge strategy** — moved from local cherry-picks (Session 1) to GitHub Pull Requests with squash-merge (Session 2). PRs give review + CI + a record.
- **Branch cleanup** — delete branches once merged, both on remote *and* the contributor's local copy (otherwise they reappear on the next push).
- **Sensitive data** — only synthetic / public-source data lands in this repo. Comp data is labeled "synthetic test data" with synthetic source URLs.

---

## Session Log

### Session 1 — May 6, 2026 (Wed AM)

**Goal:** Merge Heather's first round of contributions, clean up old verification branches.

#### What happened

1. **Verified agent setup.** Confirmed that working in `repos/` subfolder still inherits all `.cursor/rules/` from the parent `golden-workspace/` (Tokyo, Sherpa, Sheriff, skills catalog, etc.).
2. **Discovered Heather's branch had more than expected.** What looked like "one push" was actually 3 commits on `verify/heather`:
   - `b493d1a` "verify: heather can push" (noise — just a permissions test)
   - `f08a504` Expanded `competitor_postings.csv` (3 → 33 rows) and `comp_benchmarks.csv` (3 placeholder → 18 rows of synthetic comp data)
   - `b0698aa` Refactored Section 2 — dropped "comp inflation" from the difficulty composite (3 inputs → 2 inputs); deleted `data/comp_inflation.csv`; updated `BUILD_SPEC.md` and the scaffold to match
3. **Cherry-picked the 2 substantive commits** onto `main`, skipping the verify-noise commit. Pushed.
4. **Heather pushed again** — single commit `2170203` populating `gem_response_rates.csv` with 18 rows of synthetic Gem benchmark data. Cherry-picked, pushed.
5. **Deleted Heather's `verify/heather` branch** on the remote. Also deleted `verify/jason` (no work). Kept `verify/kyle` for upcoming work.
6. **Kyle path changed.** Decided to overwrite Kyle's local work since Heather had already done the equivalent. Walked Kyle through `git fetch && checkout -f main && reset --hard origin/main && branch -D verify/kyle`. Deleted remote `verify/kyle`.
7. **Heather's branch reappeared.** When she pushed again, `verify/heather` came back from the dead because her *local* branch was still alive after we'd only deleted the remote. Pushed her work recreated the remote branch with all the old commits attached.
8. **Cherry-picked her new tip commit** `9838b50` — Section 1 reframed from "Trends and Insights" to "Industry Signals" and populated with 5 curated fintech industry signals. Deleted the remote branch a second time.
9. **Side question — Jason's Cursor "looked wrong."** Diagnosed via screenshot: he was in Cursor's standalone Agents view, not the IDE workspace. Solution: `Cmd+O` to open the project folder as a workspace.

#### Problems we ran into

| Problem | Solution |
|---|---|
| One contributor's "single push" actually contained 3 commits including a meaningless permissions-test commit | Inspect with `git log main..origin/<branch> --oneline` before merging. Decide per-commit whether to keep. |
| Deleted remote branches kept reappearing | Only deleting on the remote isn't enough — the contributor must also delete their *local* branch (`git branch -D <name>`), otherwise their next push recreates it. |
| Cherry-picking creates new SHAs, so `git log main..branch` keeps showing old commits as "unmerged" forever | Known side effect; either ignore the noise or have contributors start fresh from main for each new piece of work. |
| Two scope changes to `BUILD_SPEC.md` (Section 2 inputs reduced; Section 1 panel renamed and scope widened) landed almost silently inside refactor commits | Tokyo flagged both at merge time. Going forward — surface BUILD_SPEC changes in commit messages explicitly, ideally as their own commits. |

#### State at end of session

- `main` at `68f3000` — Heather's three rounds of work all incorporated
- All `verify/*` branches deleted on remote
- Kyle reset to clean main, no work in flight
- Working tree clean

---

### Session 3 — May 12, 2026 (Tue PM)

**Goal:** Pivot from AI-Week demo to two-sourcer working tool with real data. Lay the foundation for Phase 1.

#### Context shift

The project transitioned from a one-week demo to an ongoing working tool used by two leadership sourcers to present talent landscape data to hiring managers and the broader talent team. The audience is now real stakeholders, not a demo crowd, which changes what "good enough" means: synthetic data is no longer acceptable.

#### Decisions

| Decision | Choice | Why |
|---|---|---|
| Collaboration model | **Option A** — one code owner (Heather), both sourcers maintain data in a shared Google Sheet. Code stays in git as a safety net. | Two non-engineers can't sustainably both edit Python; clean role split matches how recruiting work actually flows. Data partner never touches GitHub. |
| First problem area | **Section 1 (competitor postings)** | Most automatable section, highest stakeholder visibility, sets up the Sheets backend other sections will reuse. |
| Data approach for Section 1 | **Scrapers first, no manual hand-curation baseline.** | "Time isn't an issue; we just want to get this tool right." No throw-away work; postings tab stays empty until scrapers ship. |
| Scraper sequencing | **Three SaaS-based scrapers in order of tractability.** | Sequenced by how stable the source is, not by which competitor matters most. |

#### Scope clarification

"Greenhouse" appears in some scraper URLs because Greenhouse-the-company runs a SaaS that hosts public job boards for several of our Tier 1 competitors (Stripe, Brex, Ramp, Block). **This is not Affirm's internal Greenhouse ATS.** Same name, different system. The scraper reads from each competitor's own public-facing careers page — the exact same data anyone in the world can browse, hosted on Greenhouse infrastructure as a SaaS service. No internal Affirm data, no candidate PII, no ATS access.

#### What landed in this session (foundation work)

1. New `src/config.py` — centralized env loader for Google Sheets credentials + Notion. Uses `python-dotenv` (already a dep).
2. New `src/sheets.py` — gspread + service account wrapper. Reads any tab as a pandas DataFrame. Lowercases + underscore-normalizes column names so headers like "Posted Date" vs "posted_date" both work.
3. Section 1 (`src/sections/competitive_landscape.py`) refactored to read from Sheets via the service account, fall back to local CSV/JSON otherwise. 5-minute `@st.cache_data` TTL so edits in the Sheet show up within 5 minutes without manual reload. Source label ("Google Sheets" vs "Local CSV") rendered under each block. Graceful empty-state handling when a tab exists with the right schema but no data rows yet.
4. `.env.example` rewritten with the service account variables (`GOOGLE_SHEETS_WORKBOOK_ID`, `GOOGLE_SHEETS_KEY_FILE`) and step-by-step setup instructions.
5. `.gitignore` extended to exclude `secrets/` and `*.serviceaccount.json` patterns.
6. `requirements.txt` adds `gspread>=6.0` and `google-auth>=2.0`.
7. README rewritten:
   - New "How we collaborate" section explaining the code-owner / data-partner split
   - "Refreshing data weekly" split into Path A (Google Sheets) and Path B (Local CSVs fallback)
   - New "Setting up the Google Sheets backend" one-time setup section for the code owner

#### Bumps along the way

- **First tried publish-to-web CSV URLs** (the simpler approach). Confirmed via the publish-to-web dialog: Affirm Workspace restricts the audience to "Affirm, Inc." which means external/unauthenticated requests get 401. **Pivoted to the service account approach** — same end-state (data partner edits a Sheet, app reads it), different auth path.
- **Column-name case sensitivity bit us on first test.** Sourcers naturally type "Title" or "Posted Date"; the code expected lowercase. Fixed in `src/sheets.py` by lowercasing + underscore-normalizing all column names from Sheets — sourcers can use any reasonable header style.

#### What's next

- **User action (data partner can help):** create the shared Google Sheet, share with both sourcers, publish the two tabs to CSV, paste the URLs into `.env`. Then the app starts reading live data even though the Sheet is empty (it'll just show no rows until the scraper populates it).
- **Code owner action:** build the scraper for Stripe / Brex / Ramp / Block (the four competitors whose public boards run on Greenhouse infrastructure). This is Phase 1A in the plan.

#### Plan reference

Full plan with phasing, decisions, and todos lives in `.cursor/plans/real_data_phase_1_4347dee3.plan.md`.

---

### Session 4 — May 12, 2026 (Tue PM, continued)

**Goal:** Ship Phase 1A — the Greenhouse public-board scraper.

#### Mid-build scope expansion

The original plan was a scraper for 4 named competitors (Stripe, Brex, Ramp, Block). Mid-build, the scope expanded to also cover the broader Consumer Tech + Fintech landscape. A discovery probe across 44 candidates produced concrete data: 25 are on Greenhouse with active leadership postings; 13 use different infrastructure (Ashby, Workday, custom). Ramp turned out to be on Ashby, not Greenhouse — moved to Phase 1B.

#### Two design decisions resolved mid-build

| Decision | Choice | Why |
|---|---|---|
| Level filter strictness | Phase 1A scope expanded to Director + Head + SD + VP + SVP, not just SD/VP/SVP as originally specced | Probe data showed competitors essentially never post SD/VP roles publicly — 23 hits across 879 jobs under strict filter. Senior leadership hires through retained search. Broader filter captures what's actually published (177 hits). |
| Tier-based filtering | Option C — broad filter for direct competitors, narrower filter (Head/SD/VP only) for the broader Consumer Tech + Fintech list | Sourcers care more about Director-level signal from direct payments/BNPL competitors than from consumer tech where "Director" often means senior IC (Art Director, Account Director). Tier config in `src/data/competitors.json` so re-tiering is one file edit, not a code change. |

#### What landed in this session

1. **`src/scraper.py`** — new module with all shared scraping primitives:
   - `classify_level(title, tier)` — tier-aware level regex matcher; returns canonical unabbreviated form
   - `classify_function(title)` — keyword-based mapping to one of the 6 BUILD_SPEC functions, with a 7th "Other" bucket for unclassifiable titles
   - `fetch_greenhouse_jobs(slug, name)` — pulls one company's public board with per-company error handling
   - `classify_jobs()` — composes the above into `ClassifiedPosting` records
   - `load_competitor_config()` — reads tier assignments from JSON
2. **`src/data/competitors.json`** — 7 primary + 18 secondary competitors. Editable without touching code.
3. **`scripts/refresh_postings.py`** — runnable entrypoint that auto-creates two new Sheet tabs (`Scraped — Pending Review`, `Scraper Run Log`), wipes + rewrites Pending Review each run, and appends one log row per company.
4. **`src/sheets.py`** — added write-capable helpers (`open_workbook_for_writing`, `get_or_create_worksheet`, `append_rows`, `replace_data_rows`). Read scope and write scope are separate so the Streamlit app stays read-only by default.
5. README updated with the scraper usage guide and the list of companies still on non-Greenhouse infrastructure.

#### First live run (production)

- 25 companies probed, all returned status `ok` (zero board failures)
- 108 leadership postings classified and written to Pending Review tab
- Split: 59 primary + 49 secondary
- Level breakdown: 52 Head of, 33 Director, 17 Senior Director, 6 VP, 0 SVP (matches the "senior leadership doesn't post publicly" pattern)
- Function breakdown: 50 Other, 19 Revenue, 16 Product, 10 Operations, 8 Finance, 5 Engineering — the high "Other" count (46%) is honest signal, not a bug, and tells sourcers exactly which rows need manual classification

#### Bumps along the way

- **First run hit `403 Caller does not have permission`** because the service account was still Viewer from the Session 3 setup. Bumping to Editor fixed it. Documented this gotcha in the scraper setup instructions.
- **Engineering fallback was misleading.** First version of the function classifier defaulted to "Engineering" when no keyword matched. Sheriff flagged this — sourcers would see 55 Engineering rows and assume the classifier was working when half were Marketing/Comms/Legal/HR titles. Changed fallback to "Other" — now sourcers can see exactly which rows need manual triage at a glance.

#### Mid-session refinement — Growth added as a 7th function

After the first live run, several "Other" rows turned out to be legitimate Growth roles (Director of Organic Growth & Discoverability, Head of Integrated Campaigns, Head of Growth Marketing, etc.). Sourcer requested adding **Growth** as a classifier function. Implemented with a deliberately conservative priority — Growth fires only after Revenue, Operations, and Product have a chance to match, so mixed titles like "Head of Sales, Growth" stay Revenue and "Director of Product, Growth/AI" stays Product. Net effect: 7 rows moved Other → Growth, no rows displaced from established functions.

**Asymmetry to be aware of:** BUILD_SPEC still locks Sections 2-4 to 6 functions (no Growth). The scraper and Section 1 surface Growth, but Sections 2-4 will continue to show only the 6 originals until BUILD_SPEC is formally expanded with Growth × all 3 levels of comp + talent-pool data.

#### What's next

- **User action (sourcers):** triage the first batch of 108 rows in the `Scraped — Pending Review` tab. Keep, edit, or delete each. Copy approved rows into the `Postings` tab. Pay extra attention to `function = Other` rows.
- **Code owner action:** evaluate Phase 1B candidate — Ashby scraper for Ramp (and any other Ashby-hosted competitors discovered later). Same shape as Phase 1A: fetch → classify → write to Pending Review.
- **Future BUILD_SPEC expansion:** if Growth proves useful in practice, expand from 6 to 7 functions formally — add Growth × Senior Director / Vice President / Senior Vice President rows to `comp_benchmarks.csv` and `talent_pool.csv`, update Section 2 heatmap, update Section 4 sourcing engine dropdown.

---

### Session 2 — May 7, 2026 (Thu AM)

**Goal:** Sync to latest, see what changed overnight.

#### What happened

1. **Pulled `origin/main`.** Fast-forward update from `68f3000` → `bd9bf0e`. Single new commit: `bd9bf0e Heather (#3)`.
2. **Workflow upgrade observed.** The `(#3)` indicates a Pull Request was opened, reviewed (or at least merged) on GitHub, and squash-merged. This is a step up from the local cherry-pick pattern used in Session 1.
3. **Substantial diff in PR #3** — 10 files, including a new `.streamlit/config.toml`, updates to `BUILD_SPEC.md`, all 4 data CSVs, three section scaffolds (`competitive_landscape.py`, `difficulty_heatmap.py`, `sourcing_engine.py`), and a small tweak to `src/xray.py`.
4. **New remote branch:** `origin/heather` (note the cleaner name — dropped the `verify/` prefix). Either the source branch for PR #3 not auto-deleted on merge, or a fresh branch for the next round.

#### State at end of session

- `main` at `bd9bf0e`, working tree clean
- `origin/heather` exists — TBD whether it's leftover from PR #3 or in-flight new work
- Local sync confirmed

---

## Recurring Issues & Patterns to Remember

### "Why does my branch keep coming back?"

Deleting a branch only on the remote (`git push origin --delete <branch>`) doesn't kill the contributor's local copy. Their next push recreates the remote branch with whatever local history they have.

**Fix:** When cleaning up a branch, both sides must delete it:
- Remote (anyone with push access): `git push origin --delete <branch>`
- Contributor's local (only they can do this): `git branch -D <branch>`

### "I want some of their changes but not all"

Three escalating granularities:
1. **By commit** (cleanest) — ask contributor to commit logical pieces separately, then `git cherry-pick <SHA>` only the ones you want.
2. **By file** — `git checkout <branch> -- <files>` to grab specific files.
3. **By line/hunk** — `git checkout -p <branch> -- <files>` for interactive hunk-by-hunk selection.

### "Their Cursor doesn't look like mine"

Most often it's a **mode** issue, not a layout issue:
- **Cursor's standalone Agents view** has no file explorer or editor — only the agent runner UI. Fix: `Cmd+O` to open a folder as a workspace.
- For actual layout differences (panel positions, etc.): `Cmd+Shift+P` → **"View: Reset View Locations"**.
- For matching settings end-to-end: use **Profile export/import** (`Profiles: Export Profile` → share → `Profiles: Import Profile`).

### "How do I update my local from GitHub?"

Standard sync pattern:
```bash
git fetch origin --prune
git pull --ff-only origin main
git status        # confirm clean and up to date
```

The `--prune` cleans up stale remote-tracking refs for branches that were deleted on GitHub.

---

## Decisions Log

| Date | Decision | Why |
|---|---|---|
| 2026-05-06 | Section 2 difficulty composite reduced from 3 inputs to 2 (dropped comp inflation) | Comp inflation was hard to source reliably from public data; cutting was cleaner than carrying a placeholder |
| 2026-05-06 | Section 1 panel renamed "Trends and Insights" → "Industry Signals" | Better describes the panel; spec now allows non-Tier 1 fintech news, not just direct competitor coverage |
| 2026-05-06 | Comp benchmark data uses synthetic test values, not real numbers | Compliance — repo only contains public-source / synthetic data |
| 2026-05-07 | Workflow shifts from local cherry-picks to GitHub PRs | More review, better record, cleaner history |
| 2026-05-12 | Collab model: code owner (Heather) + data partner; both edit data via Google Sheets, only code owner edits Python | Two non-engineers can't sustainably both edit Python; spreadsheets match how recruiters already work |
| 2026-05-12 | First "real data" problem area is Section 1 (competitor postings) | Most automatable section + highest stakeholder visibility + sets up the Sheets backend other sections will reuse |
| 2026-05-12 | Scrapers first, no manual hand-curation baseline | "Time isn't an issue; get the tool right" — no throw-away work |
| 2026-05-12 | Google Sheets auth: service account, not publish-to-web | Affirm Workspace restricts publish-to-web to Affirm-only; service account is the standard enterprise pattern and works regardless of publish-to-web policy |
| 2026-05-12 | Phase 1A scope expanded from 4 named competitors to 25 Greenhouse-hosted Consumer Tech + Fintech companies | Probe revealed direct competitors barely post leadership roles publicly; broadening the company list gives meaningful signal volume |
| 2026-05-12 | Level filter relaxed from BUILD_SPEC strict (SD/VP/SVP) to include Director + Head of | 23 hits vs 177 hits across 879 candidate jobs — strict filter would produce a near-empty tool that looks broken on first run |
| 2026-05-12 | Two-tier filter: broad for direct competitors, narrower for the broader Consumer Tech + Fintech list | Pragmatic compromise — direct competitor Director signal is valuable; consumer-tech "Director" titles are too often senior IC to be useful as leadership signal |
| 2026-05-12 | Function classifier fallback is "Other," not "Engineering" | Engineering fallback would hide misclassifications. "Other" surfaces them honestly so sourcers know which rows need manual classification before promoting to Postings |
| 2026-05-12 | Added Growth as a 7th classifier function (scraper-only, not BUILD_SPEC) | Several "Other" rows were legitimate Growth roles (Organic Growth, Growth Marketing, Integrated Campaigns). Sections 2-4 still show 6 functions until BUILD_SPEC is formally expanded |
| 2026-05-12 | Growth placed AFTER Revenue/Product in classifier priority | Conservative — pure Growth titles fire as Growth, but mixed titles ("Head of Sales, Growth", "Director of Product, Growth/AI") stay with their primary function |

---

## Open Questions / TODOs

- [x] Confirm whether `origin/heather` (new branch as of May 7) is leftover from PR #3 or in-flight work — *resolved Session 2: was in-flight; later merged via PR #4*
- [x] Establish the formula combining the 2 difficulty inputs into low/medium/high — *resolved: tertile bucket sum, locked in BUILD_SPEC.md*
- [ ] Decide whether contributor branches should be auto-deleted on PR merge (GitHub setting)
- [ ] **Phase 1 open:** where does the app run for stakeholder access? (local + Notion publish vs Streamlit Community Cloud vs internal Affirm hosting)
- [x] **Phase 1 open:** function classification tiebreaker policy when a title maps to multiple functions (e.g. "VP of Product Engineering") — *resolved: first-match-wins with documented priority order; "Other" fallback surfaces misses*
- [ ] **Phase 1 open:** stale-posting rule — drop after 30 days? 60? When the company removes it?
- [x] **Phase 1 open:** Google Sheets service account setup (needed for the scraper to write back to the workbook) — *resolved: service account upgraded to Editor on May 12; scraper runs end-to-end*
- [ ] **Phase 1A:** sourcers run the first triage pass on the 108 scraped rows; refine which functions/levels need classifier tweaks
- [ ] **Phase 1B candidate:** Ashby scraper for Ramp and any other Ashby-hosted competitors
- [ ] **Phase 1C candidate:** Workday + custom-ATS scrapers for Klarna, Coinbase, Plaid, DoorDash, Uber, Notion, OpenAI, Shopify (harder — Workday usually requires headless browser)

---

## How to Add to This Log

When something notable happens — a merge, a problem we solved, a decision, a workflow change — add a brief entry:

1. **For new sessions:** add a `### Session N — Date` block under "Session Log" with what/problems/solutions/state.
2. **For decisions:** add a row to the "Decisions Log" table.
3. **For recurring issues:** add a subsection under "Recurring Issues & Patterns to Remember."
4. **For TODOs:** add a checkbox under "Open Questions / TODOs"; check it off when done.

Keep entries general enough to be useful as a reference without re-reading every detail. Specifics belong in commit messages and `BUILD_SPEC.md`.
