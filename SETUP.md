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
- [ ] **Node.js** (LTS) — confirm with `node --version` and `npm --version`
- [ ] **Editor** — Cursor, VS Code, or your preferred editor

### Configure Git locally

Run these once, replacing with your info:

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@company.com"
```

### Set up GitHub authentication (pick one)

**Option A — HTTPS + Personal Access Token (simpler)**

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token with `repo` scope
3. Save it somewhere safe — you'll paste it as your password the first time you push

**Option B — SSH key (one-time setup, no token to manage)**

```bash
ssh-keygen -t ed25519 -C "your.email@company.com"
cat ~/.ssh/id_ed25519.pub
```

Then add the public key to GitHub → Settings → SSH and GPG keys.

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

Once you've been invited:

- [ ] Accept the GitHub invite from your email
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

- [ ] **Framework** — Vite + React, Next.js, or other? (Netlify-friendly recommended)
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

### Deployment

- [ ] Connect repo to **Netlify** (or Vercel) for auto-deploy from `main`
- [ ] Enable **deploy previews** so every PR gets its own live URL
- [ ] Confirm the live URL works for everyone

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
| `permission denied` on push | Confirm you're a collaborator and your auth (PAT or SSH) is configured |
| Merge conflict | Pull `main`, resolve in your editor, commit, push |
| Accidentally committed to `main` directly | `git reset --soft HEAD~1`, then move changes to a branch |
| Need to undo a commit you already pushed | Use `git revert <commit>` — safer than `git reset` once shared |
| Push rejected because `main` moved | `git pull --rebase origin main`, then push again |

---

## Pre-Hackathon Tips

1. **Do Phase 1 + 3 before the hackathon starts** — getting setup eats real hackathon time.
2. **Phase 4 is the most important step to slow down for** — agreeing on the data contract and component ownership for 10 minutes saves you hours of merge pain later.
3. **Tag a working commit before final tweaks** — `git tag v0.1-demo` lets you roll back instantly if something breaks 10 minutes before presenting.
4. **Use the Netlify deploy preview URL** for the final demo — more reliable than running locally on someone's laptop.

---

Questions? Ping the team chat. Good luck.
