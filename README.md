# tempest-watch

A personal Pokémon TCG price-tracking and deal-detection system — respectful multi-source ingestion, an LLM-driven listing matcher with a span-grounded confidence pipeline, and a Three.js card archive with holographic shader effects.

**Status:** in design / pre-MVP

---

## About

I collect Pokémon TCG, currently working through the Silver Tempest master set (~245 cards including reverse holos). Like most collectors who've been at it a while, I've given up on opening packs — the variance never quite works out, and you end up with five Galarian Slowpokes instead of the alt art you actually wanted. So I buy singles.

The problem with buying singles is the daily grind: refreshing PriceCharting, eBay, and Carousell SG across hundreds of cards. Singapore-local pricing on Carousell in particular isn't covered well by any existing aggregator — and that gap is the one I actually care about. This project is my answer to it.

It pulls from a handful of trusted sources on respectful intervals, matches messy listing titles to a canonical card database using an LLM with structured-output confidence scoring, scores each listing against rolling-window price baselines, and pings me on Telegram when something undervalued shows up for a card I still need.

I'm also using this as a deep-end portfolio project. The intent is to over-engineer the parts that are interesting to over-engineer — the ingestion architecture, the matcher's confidence pipeline, the holographic foil shader on the frontend — and to keep everything else boring and reliable. Concretely, it's where I'm stretching three muscles at once: AI engineering and multi-agent orchestration, full-stack delivery, and 3D/shader frontend work.

## Why "tempest-watch"

The name layers two things. The obvious one is Silver Tempest, the Pokémon set this project starts with. The less obvious one is *That Time I Got Reincarnated as a Slime*, where the protagonist Rimuru takes the surname "Tempest" as part of his sworn bond with Veldora the Storm Dragon — and later names the entire Jura Tempest Federation after it. I liked the idea of naming something after a friendship that fundamentally changes both parties; it's not a bad metaphor for a collector and the system they build to keep the hobby sustainable.

"Watch" is the functional half — this is a monitoring and alerting system at its core.

Silver Tempest is the starting scope, not a permanent constraint. The architecture is set-agnostic and will generalise to arbitrary sets, and eventually sealed product, once the MVP is reliable.

## What it does

- Tracks a personal watchlist of cards I still need from the master set.
- Ingests listings from multiple sources, normalises them, and resolves each one to a canonical card.
- Scores every listing against a rolling-window market baseline, condition-aware and currency-normalised, and flags genuine undervaluations.
- Sends a Telegram notification — price, condition, source, and a deep link back into the app — when an undervalued listing appears for a needed card. Users can set per-card price thresholds.
- Surfaces price history per card: a global market-trend baseline overlaid with locally observed Singapore sold data.

## Architecture

The system is a staged pipeline with a durable store between every stage, so any stage can be rebuilt or replayed without re-running the ones before it:

```
ingest (raw) -> normalise -> match -> score -> alert
```

Raw source payloads are persisted before anything touches them. That single decision means the matcher can be rebuilt and re-tested against months of real listings without re-scraping a single source.

### The matcher

The matcher is the part I'm deliberately over-engineering. Listing titles are messy ("lugia vstar alt art FULL ART swsh12 NM!!"), and getting card identity, condition, and price right is the difference between a useful alert and noise. The pipeline is tiered, so it escalates only when it has to and keeps cost and latency bounded:

1. **Deterministic match** — set number plus normalised card name, fuzzy-matched against the canonical Silver Tempest dictionary. Resolves the large majority of listings at near-zero cost, no LLM involved.
2. **Contextual LLM pass** — runs only on listings the deterministic stage can't confidently resolve. Optionally reads attached listing images when the text alone is ambiguous.
3. **Span-grounding adjudicator** — drops any extracted field (card identity, condition/grade, price, currency) that isn't grounded in the source listing text. No claim survives that can't be traced back to what the seller actually wrote.
4. **Confidence judge** — scores the final match. The score is not decorative: it gates whether a notification fires, and routes low-confidence matches to a human-review queue rather than silently trusting them.

The flow is orchestrated as an explicit state graph (LangGraph) — nodes for each stage, conditional edges for the escalation logic, and a human-in-the-loop interrupt for review. Model calls go directly to the LLM endpoint rather than through a managed abstraction layer.

### The frontend

- A React + Three.js card archive: each card rendered in 3D with a flip animation, a 360° view, and a holographic foil shader for the relevant rarities.
- Per-card detail view: price-history chart, an AI-generated trend summary, and live listings across sources.
- A collection completion dashboard: progress by rarity tier, percentage toward the master set, and estimated cost-to-complete.
- A virtual companion avatar that moves around the app and reacts to navigation (a deeper conversational version is post-MVP).

Design and UI/UX worked through in Figma, with Claude in the loop for mockups and iteration.

## Data sources

| Source | Access | Role |
|---|---|---|
| pokemontcg.io | Free API (key for higher limits) | Canonical card metadata, official images, set lists, and an embedded TCGplayer / Cardmarket market-price baseline |
| eBay | Free Browse API | Live global asking prices, high volume — note this is active listings only; sold/completed data isn't exposed on the free APIs |
| PriceCharting | Respectful scrape | Historical sold-average data, used to backfill price trends |
| Carousell SG | Respectful, watch list-driven scrape | Singapore-local listings — the gap no existing aggregator covers, and the reason this project exists |

A deliberate constraint shapes the design: free sources give a *current* price snapshot, not history. So the canonical market baseline is snapshotted into a time series from day one and accrues forward, with PriceCharting used to backfill. Carousell ingestion is driven by per-card search queries scoped to my needed list rather than a broad crawl, which keeps request volume low and the footprint respectful.

## Engineering notes / design decisions

- **Persist raw, then transform.** Raw payloads are stored untouched so the pipeline is replayable and sources are never hit twice for the same data.
- **Identity is write-once; price is append-only.** Every listing is keyed on its stable source ID. The expensive matcher runs once per listing and caches its result; subsequent polls only diff price and status, appending `(listing_id, price, currency, observed_at, status)` observations rather than overwriting. This one model yields per-listing price history and, when listings sell or vanish, a locally observed sold dataset.
- **Re-poll is not re-match.** Cheap source polling is scheduled and ongoing; the LLM identity pipeline is not re-run unless a listing's title materially changes.
- **Condition-aware, currency-normalised scoring.** A cheap listing is only a deal like-for-like — raw NM vs a graded slab are different markets. Prices are normalised to a single currency at ingest, and "undervalued" is measured as a discount to a trailing-window *median* baseline (median, because TCG prices have fat tails).
- **One Postgres, deferred blob storage.** A single PostgreSQL instance — managed Postgres on AWS RDS in production, local docker-compose Postgres in development and tests — holds the canonical card DB, normalised listings, the price time series, and raw payloads (as JSONB). Card images stay as CDN URLs rather than being re-hosted. Object storage is introduced only if raw volume forces it.
- **Lean by choice.** Managed Postgres on RDS for production, and the rest deployed lean by hand — single box for the app, manual deploy, no IaC, direct LLM endpoints. RDS earns its place because backups, patching, and disk aren't where I want to spend attention; everything else stays small on purpose so the focus is on the interesting parts (the matcher, the shader).
- **Eval-driven matcher.** A small labelled set of real listings with known-correct matches is maintained from early on, so the precision/recall impact of each pipeline stage is measured rather than assumed.

## Tech stack

- **Frontend:** React, TypeScript, Three.js (3D card archive, holographic foil shader), Vite, npm. Figma for design and UI/UX.
- **Backend:** Python 3.13, FastAPI, managed with [uv](https://docs.astral.sh/uv/).
- **AI / agents:** LLM matcher with structured outputs; tiered multi-agent pipeline (deterministic match, contextual pass, span-grounding adjudicator, confidence judge) orchestrated with LangGraph; direct LLM API integration.
- **Data:** PostgreSQL with SQLAlchemy 2.x + Alembic. AWS RDS in production, docker-compose Postgres locally.
- **Ingestion:** Playwright for browser-based scraping; REST clients for API sources.
- **Alerting:** Telegram bot (notification-only).

## Roadmap

The ordering principle is to get a boring end-to-end loop that pings my phone with one real deal as fast as possible, then make each stage smarter.

- **M0 — The spine.** Pull the canonical Silver Tempest card database from pokemontcg.io, and start a daily price-snapshot job immediately so history begins accruing on day one.
- **M1 — Prove the pipeline, no AI.** One ingestion source end-to-end (eBay), the deterministic matcher, and persisted listings. No LLM yet.
- **M2 — Make it useful daily.** Scoring against the rolling baseline, Telegram alerts, and per-card price thresholds. The first point at which it earns its keep.
- **M3 — The interesting AI.** Add the LLM escalation, adjudicator, and judge for the ambiguous tail; add the Carousell scraper behind the same listing interface.
- **M4 — Frontend basics.** Collection tracker, completion dashboard, and per-card detail with price history.
- **M5 — The candy.** Three.js holographic archive, AI-generated trend summaries, and the companion avatar.

## Notes and non-goals

- Telegram is notification-only for now. A conversational bot is a post-MVP consideration once the core is stable.
- The companion avatar ships in M5 as a moving, reactive presence; deeper chatbot behaviour comes later.
- This is a personal project, built lean on purpose. The database runs on RDS in production so I'm not babysitting Postgres; everything else is hand-deployed and not intended to grow into a managed cloud service.

## Documentation

- [docs/CONVENTIONS.md](docs/CONVENTIONS.md) — engineering workflow, project shape, testing, git
- [docs/CODE_STYLE.md](docs/CODE_STYLE.md) — language-level style rules for Python and TypeScript
- [CLAUDE.md](CLAUDE.md) — collaboration rules for Claude Code on this repo
