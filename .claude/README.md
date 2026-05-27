# .claude

Claude Code configuration for this repo. Claude Code reads this folder
automatically when run in the project root.

## Files

- `commands/commit.md` — `/commit` slash command. Atomic Conventional Commits, references `docs/CONVENTIONS.md`.
- `commands/pr.md` — `/pr` slash command. Opens a GitHub PR via `gh` with a conventional title and structured body.

The session persona (teach-as-you-go, locked decisions, when-to-ask-vs-act) lives in [`../CLAUDE.md`](../CLAUDE.md), which Claude Code auto-loads on every session.

## Adding a new command

Drop a markdown file into `commands/` with frontmatter:

```markdown
---
name: <slug>
description: <one-line description shown in the slash menu>
allowed-tools: Bash(git:*), Read, Write
---

# What the command does

…instructions for Claude…
```

Then `/` in a Claude Code session lists it.
