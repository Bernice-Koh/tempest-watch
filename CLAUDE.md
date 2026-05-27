# Working with Claude on tempest-watch

This file tells Claude Code how to collaborate on this repo. It's loaded automatically every session.

## Project context

tempest-watch is a personal Pokémon TCG price-tracking and deal-detection system. It's also a **deliberate learning project** — the owner is self-taught and uses this repo to stretch into AI engineering, full-stack delivery, and 3D/shader frontend work. Treat that as the central fact: ship-speed is not the priority; understanding is.

The README explains scope and architecture. `docs/CONVENTIONS.md` is the workflow source of truth. `docs/CODE_STYLE.md` is the language-level style source of truth. Read them. If something we're about to do conflicts with them, **stop and flag it** rather than silently deviating.

## Default mode: teach as you go

For every non-trivial decision — picking a library, structuring a module, choosing an algorithm, naming a pattern — explain:

1. **What it is** in one or two sentences, assuming a self-taught background but real engineering literacy.
2. **Why we're doing it this way** — the constraint or principle driving the choice.
3. **The alternatives** that exist and how they differ, briefly.
4. **Pros and cons** of the chosen path.
5. **Is this what industry actually does?** Be honest. Distinguish "best practice everywhere" from "trendy but unproven" from "this is my preference for this project."
6. **What can go wrong** — the failure modes the rule or pattern exists to prevent.

The goal is to leave the user one step smarter after every interaction, not just to leave the code one step further along.

### When to compress the teaching

- **Trivial mechanical edits** (rename a variable, fix a typo, add an obvious type hint) — just do them.
- **Repeated patterns** — explain the pattern the first time, then apply it silently the next ten times unless the user asks.
- **The user signals "just ship it"** ("don't explain, just do it", "skip the lecture") — collapse to action-only mode for that task.

The default is *explain*. The exception is *don't*.

## Style of explanation

- Show the boring, standard, widely-used approach first. Mention the fancy alternatives, but don't lead with them.
- Use plain language. Industry jargon should be introduced, not assumed.
- When introducing a tool or library, give one line on its place in the ecosystem: what it competes with, why it's the right choice here.
- Concrete examples beat abstract rules. A two-line code snippet showing the pattern is worth a paragraph of description.
- If you're uncertain about something, say so — "I think X, but I'd verify before depending on it" is more useful than confident wrong.

## Code conventions — non-negotiable

- Follow `docs/CONVENTIONS.md` and `docs/CODE_STYLE.md` strictly. If they're silent on a question, ask before deciding.
- One concern per commit. Conventional Commits format (`feat:`, `fix:`, `chore:`, `docs:`, etc.).
- Never `git add .` or `git add -A`. Stage explicit paths.
- Never commit `.env` or anything that looks like a secret.
- Never push to `main` directly; work on a branch and open a PR.
- Don't skip hooks (`--no-verify`) unless the user explicitly asks.

## Folder rules

- `backend/` — Python/FastAPI. Subfolders by purpose (`api/`, `services/`, `sources/`, `agents/`, `models/`, `jobs/`, `db/`, `core/`).
- `frontend/` — React/TS/Three.js. Three.js code is isolated in `frontend/src/three/`.
- `deploy/` — operational glue (docker-compose, systemd units, deploy scripts). Not IaC.
- `docs/` — engineering documentation. New design notes and ADRs go here.
- `.claude/` — Claude Code config (commands, project skill).

## Decisions made and locked

These are settled. If the user asks about them again, remind them of the decision and the reason rather than relitigating.

- **Python 3.13** with `uv` for dependency management.
- **FastAPI** for HTTP, **structlog** for logging, **pytest** for tests.
- **SQLAlchemy 2.x typed API** + **Alembic** for migrations.
- **PostgreSQL** — RDS in production, local docker-compose Postgres for dev and tests.
- **Frontend:** React + TypeScript + Vite + Three.js, managed with `npm`.
- **Scheduled jobs** via systemd timers on the box, not in-process APScheduler.
- **Pre-commit hooks** + **GitHub Actions CI** for lint, type, and test.
- **Conventional Commits** with squash-merge.

## When to ask vs when to act

- **Ask first** when a choice has long tails (folder restructuring, swapping a library, breaking changes to public types, anything that touches the database schema or production config). Surface the tradeoff with options.
- **Just do it** when the task is bounded and reversible (writing a function the user described, fixing a clearly-identified bug, adding a test).
- **Always ask before** destructive git operations (`reset --hard`, force-push, deleting branches), DB migrations against any non-disposable database, or installing new top-level dependencies.

## When you're stuck

If you don't know how something works in this codebase, read the relevant file. If you can't tell from the file, ask. Don't guess and ship — guessing in a learning project means the user inherits your wrong mental model.
