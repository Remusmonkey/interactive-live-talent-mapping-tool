# Team Setup Checklist — Interactive Live Talent Mapping Tool

Welcome to the team. This guide gets you from zero to "I can push code" in about 20 minutes. Work through it in order — Phase 1 is yours alone, Phase 2 is the repo owner's, Phase 3 is everyone confirming, and Phase 4 is a quick team huddle.

---

## Phase 1: Individual Setup (everyone, ~15 min)

Each person does this on their own machine.

### GitHub account

- [ ] Sign in to GitHub (or sign up at <https://github.com>)
- [ ] Verify your email is confirmed
- [ ] Share your GitHub username in the team chat so the repo owner can invite you

### Local tools

- [ ] **Git** — confirm with `git --version` (install from <https://git-scm.com> if missing)
- [ ] **GitHub CLI (`gh`)** — confirm with `gh --version` (install with `brew install gh` on macOS, or see <https://cli.github.com>)
- [ ] **Cursor** — download from <https://cursor.com>

### Configure Git locally

Run these once, replacing with your info:

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@company.com"
```

### Set up GitHub authentication (recommended: `gh`)

The reliable way on macOS is the GitHub CLI. It handles auth via your browser and configures git's credential helper so every push/pull works without prompting — including from inside Cursor's agent.

```bash
gh auth login
# Pick: GitHub.com → HTTPS → Login with a web browser → paste the one-time code
gh auth setup-git
gh auth status   # should say "Logged in to github.com"
```

After this, `git clone`, `git push`, and `git pull` all work seamlessly from any terminal — including the Cursor agent's non-interactive shell.

> **Why not just sign into GitHub from Cursor's settings?**
> Cursor's GitHub integration powers IDE features (PR review, source control panel) but does NOT consistently configure git's command-line credential helper. The Cursor agent runs `git push` non-interactively and fails with "Device not configured" when no credential helper is set up. `gh auth setup-git` is the one-shot fix.

#### Fallback paths (only if you can't install `gh`)

**HTTPS + Personal Access Token**

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token with `repo` scope, copy it
3. Run `git push -u origin <branch>` **in your own Terminal app** (not Cursor's agent). Enter your GitHub username, paste the token as the password. macOS Keychain caches it — subsequent pushes (including from Cursor) will work.

**SSH key**

```bash
ssh-keygen -t ed25519 -C "your.email@company.com"
cat ~/.ssh/id_ed25519.pub
```

Add the public key to GitHub → Settings → SSH and GPG keys, then clone using the `git@github.com:...` URL instead of HTTPS.

---

## Phase 2: Repo Setup (already done)

The repo is live at:

**<https://github.com/Remusmonkey/interactive-live-talent-mapping-tool>**

The repo owner needs to invite each teammate:

- [ ] GitHub → repo → **Settings → Collaborators → Add people**
- [ ] Invite each teammate by GitHub username
- [ ] Drop the repo URL in team chat

---

## Phase 3: First Sync (everyone, ~5 min)

Once you've been invited and accepted the GitHub invite from your email, pick **one** of the two paths below.

### Option A — Cursor Quickstart (recommended)

Open Cursor (with no folder, or any folder), open the chat, switch to **Agent mode**, and paste the prompt below. The agent will verify your auth, clone the repo, run the smoke test, and confirm you can push — all in one go.

> **Prerequisite:** you must have completed `gh auth login` + `gh auth setup-git` in Phase 1. The first step of the prompt checks for this and stops if you haven't.

```text
Help me set up the Interactive Live Talent Mapping Tool repo for the hackathon.

1. First, run `gh auth status` to confirm I'm authenticated with GitHub.
   - If it errors or says "not logged in," STOP and tell me to run:
     `gh auth login && gh auth setup-git`
     Then come back and re-run this prompt.

2. Ask me where to clone the repo (suggest ~/Desktop or ~/dev). Run:
   git clone https://github.com/Remusmonkey/interactive-live-talent-mapping-tool.git
   in that location.

3. cd into the cloned folder. Read README.md and SETUP.md for context.

4. Confirm I'm on `main` and run `git pull` so I'm at the latest.

5. Ask me my first name (lowercased, no spaces) — we'll use it for a test branch.

6. Then:
   - Create branch `test/<my-name>`
   - Append "<my name> setup complete" to SETUP_TEST.md
   - Commit with message `test: confirm <my name> setup`
   - Push with `git push -u origin test/<my-name>`

7. If the push succeeds:
   - Tell me to post "I can push" in the team chat.
   - Tell me to open the cloned folder in Cursor (File → Open Folder) so future
     work happens inside the repo.
   - Tell me to stay on `main` until the team huddle locks framework + language.

8. If anything fails, stop and explain the error — don't try to work around it.
```

### Option B — Manual checklist

If you prefer the command line:

- [ ] Clone the repo:

  ```bash
  git clone https://github.com/Remusmonkey/interactive-live-talent-mapping-tool.git
  cd interactive-live-talent-mapping-tool
  ```

- [ ] Confirm you can push by creating a test branch:

  ```bash
  git checkout -b test/<your-name>
  echo "<your name> setup complete" >> SETUP_TEST.md
  git add SETUP_TEST.md
  git commit -m "test: confirm <your name> setup"
  git push -u origin test/<your-name>
  ```

- [ ] Post "I can push" in team chat
- [ ] Repo owner deletes test branches once everyone's confirmed

---

## Phase 4: Team Agreements (5-min team huddle)

Lock these decisions before anyone starts coding. Each one will save real hours of merge pain later.

### Stack

- [ ] **Framework** — Vite + React, Next.js, or other?
- [ ] **Language** — TypeScript or JavaScript?
- [ ] **Styling** — Tailwind, CSS modules, or styled-components?
- [ ] **Component library** — shadcn/ui, Mantine, MUI, or roll our own?

### Structure

- [ ] **Folder convention** — agree on where `components/`, `data/`, `lib/`, `pages/` live
- [ ] **Branch naming** — e.g., `feat/<feature>`, `fix/<bug>`, `chore/<task>`
- [ ] **Commit style** — conventional commits (`feat:`, `fix:`, `chore:`) or freeform?

### Ownership

| Component | Owner |
|---|---|
| Competitive landscape view | |
| Hiring difficulty heat map | |
| Comp benchmarking | |
| Sourcing engine / X-Ray search strings | |
| Shared layout / nav / theming | |
| Mock data / data contracts | |

### Data contracts

- [ ] Agree on the shape of core objects — `Role`, `Company`, `CompBand`, `Candidate`, etc.
- [ ] One person checks in a `types.ts` file early so everyone codes against the same shapes

### Demo plan (running locally)

- [ ] Designate a **demo machine** — one teammate's laptop that will run the app for the final demo
- [ ] Confirm everyone can run the app locally (`npm install` → `npm run dev`)
- [ ] Practice the demo on the actual demo machine before the final presentation
- [ ] Have a backup plan — at least one other teammate should be able to run the demo if the primary machine fails

### Communication

- [ ] Where do PR review pings go? (Slack channel, DM, GitHub notifications?)
- [ ] Daily check-in cadence?

---

## Daily Workflow

```bash
# Start of session — get the latest
git checkout main
git pull

# Start a new feature
git checkout -b feat/heatmap

# ... code, code, code ...

git add .
git commit -m "feat: add base heatmap grid"
git push -u origin feat/heatmap
```

Then open a PR on GitHub → tag a teammate → merge into `main`. Repeat.

### Golden rules

1. **Never commit directly to `main`** — always work on a branch.
2. **Pull before you start** — `git pull` on `main` keeps your branch fresh.
3. **Small PRs over big PRs** — easier to review, fewer conflicts.
4. **One feature per branch** — don't mix the heat map and comp benchmarking on the same branch.

---

## Quick Troubleshooting

| Problem | Fix |
|---|---|
| `fatal: could not read Username for 'https://github.com': Device not configured` | No git credential helper is set up. Run `gh auth login && gh auth setup-git` (Phase 1), then retry the push. The Cursor agent can't respond to interactive prompts, so this fix is required before any push will work from the agent. |
| `permission denied` on push | Confirm you're a collaborator on the repo, and that `gh auth status` shows you're logged in. If using PAT/SSH instead, see Phase 1 fallback paths. |
| Merge conflict | Pull `main`, resolve in your editor, commit, push |
| Accidentally committed to `main` directly | `git reset --soft HEAD~1`, then move changes to a branch |
| Need to undo a commit you already pushed | Use `git revert <commit>` — safer than `git reset` once shared |
| Push rejected because `main` moved | `git pull --rebase origin main`, then push again |

---

## Pre-Hackathon Tips

1. **Do Phase 1 + 3 before the hackathon starts** — getting setup eats real hackathon time.
2. **Phase 4 is the most important step to slow down for** — agreeing on the data contract and component ownership for 10 minutes saves you hours of merge pain later.
3. **Tag a working commit before final tweaks** — `git tag v0.1-demo` lets you roll back instantly if something breaks 10 minutes before presenting.
4. **Practice the demo on the actual demo machine the night before** — avoids "works on my laptop" surprises and gives you time to fix anything that breaks under pressure.

---

Questions? Ping the team chat. Good luck.
