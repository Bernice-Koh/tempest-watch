---
name: commit
description: Create focused, atomic commits in the Conventional Commits style. Personal-project version — see docs/CONVENTIONS.md.
allowed-tools: Bash(git status:*), Bash(git add:*), Bash(git commit:*), Bash(git diff:*), Bash(git log:*), Read, Write(.git/COMMIT_EDITMSG), Glob
---

# /commit

Create one or more **atomic** commits following [Conventional Commits](https://www.conventionalcommits.org/).

`docs/CONVENTIONS.md` is the source of truth for commit format. This command implements that policy — when in doubt, read the conventions doc.

## Arguments

- `/commit` — group all uncommitted changes into the smallest sensible commits.
- `/commit <path> [<path> ...]` — restrict to specified paths. Globs allowed.

## The philosophy

One concern per commit. If the word "and" would naturally appear in the subject line, split the commit. Smaller is almost always better — you can always squash later, you cannot easily split.

Good:
```
feat(sources): add pokemontcg.io client
feat(models): add canonical card table
feat(jobs): add daily price snapshot job
```

Bad:
```
feat: add pokemontcg client, card model, and price job
```

## Execution

### Step 0 — Safety

Before staging anything, scan for files that look like secrets: `.env`, `.env.*` (except `.env.example`), `*.pem`, `*.key`, anything matching `*credentials*`, `*secrets*`, `*password*`, `*token*`. If any are present in the working tree or args, **stop** and ask the user before proceeding.

### Step 1 — Survey

```bash
git status
git diff --staged
git diff
git log --oneline -5
```

### Step 2 — Group

Read the diff and identify the smallest logical units. Each group becomes one commit. Split aggressively: features vs tests vs docs vs config are almost always separate commits.

### Step 3 — Stage explicitly

**Never** `git add .` or `git add -A`. Stage explicit paths only:

```bash
git add backend/src/sources/pokemontcg.py
git add backend/tests/sources/test_pokemontcg.py
```

If a single file contains changes that belong to two commits, use `git add -p` to stage hunks selectively.

### Step 4 — Write the message

Format:

```
<type>(<scope>): <description>

[optional body — explain WHY if not obvious from the diff]
```

Types (from `docs/CONVENTIONS.md`): `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `ci`.

Subject rules:
- imperative mood ("add X", not "added X" or "adds X")
- lowercase, no trailing period
- ≤ 72 characters
- scope is the module or domain (`backend`, `frontend`, `sources`, `agents`, `db`, etc.) — optional but recommended

Write the message with the Write tool to `.git/COMMIT_EDITMSG`, then:

```bash
git commit -F .git/COMMIT_EDITMSG
```

**Never** use `$()` substitution in the commit command. **Never** use `--no-verify` unless the user explicitly asks.

### Step 5 — Verify and loop

```bash
git status
```

If there are remaining changes, return to Step 2 for the next commit.

## Branch protection

If `git commit` fails because direct commits to `main` are blocked (we configure this once we have a real remote), create a branch named `<type>/<short-slug>` (e.g. `feat/pokemontcg-client`) and retry the commit. Inform the user.

## What to avoid

- `git add .` / `git add -A` — silently picks up `.env`, OS files, IDE configs.
- `git commit --no-verify` — bypasses pre-commit checks the project relies on.
- Mixing unrelated changes in one commit — makes review and revert harder.
- Long subject lines, past-tense verbs, trailing periods.
- Committing `.env` or anything secret-looking. If you find one staged, unstage it and ask.
