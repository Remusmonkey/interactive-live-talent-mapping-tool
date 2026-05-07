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

---

## Open Questions / TODOs

- [ ] Confirm whether `origin/heather` (new branch as of May 7) is leftover from PR #3 or in-flight work
- [ ] Establish the formula combining the 2 difficulty inputs into low/medium/high (still TBD per `BUILD_SPEC.md`)
- [ ] Decide whether contributor branches should be auto-deleted on PR merge (GitHub setting)

---

## How to Add to This Log

When something notable happens — a merge, a problem we solved, a decision, a workflow change — add a brief entry:

1. **For new sessions:** add a `### Session N — Date` block under "Session Log" with what/problems/solutions/state.
2. **For decisions:** add a row to the "Decisions Log" table.
3. **For recurring issues:** add a subsection under "Recurring Issues & Patterns to Remember."
4. **For TODOs:** add a checkbox under "Open Questions / TODOs"; check it off when done.

Keep entries general enough to be useful as a reference without re-reading every detail. Specifics belong in commit messages and `BUILD_SPEC.md`.
