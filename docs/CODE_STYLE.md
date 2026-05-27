# Code Style

Language-level rules for writing code in this repo. Workflow, folder structure, testing strategy, and git rules live in [CONVENTIONS.md](CONVENTIONS.md) — this file is only about how the code itself reads.

Each rule has a short *why* attached. The rules aren't arbitrary; knowing *why* lets you make judgement calls on the edge cases the rules don't cover.

## Universal principles

### Comments are for *why*, not *what*

Code is for *what*. If a comment restates what the code does, delete it or rewrite the code so the comment isn't needed.

> *Why:* "what" comments rot — the code changes, the comment doesn't, and now you have a confidently-wrong lie sitting next to working code. "Why" comments rarely rot, because the reason for a decision usually outlives the decision.

`# HACK:` and `# FIXME:` are fine and useful, but include a date and brief context. Future-you will thank present-you.

### Names carry the explanation

Prefer a longer, clearer name over a shorter name plus a comment.

> *Why:* names appear at every call site. A comment appears once. Investing in the name pays back every time someone reads the call.

`fetch_carousell_listings_for_watched_cards()` beats `fetch()` with a docstring. `is_eligible_for_alert` beats `flag` with a comment.

### Boundary checks vs internal trust

Validate inputs at system boundaries: HTTP request bodies, external API responses, file contents. Inside a module, trust the types and don't re-validate.

> *Why:* defensive validation everywhere makes code unreadable and slow, and the redundant checks rot independently. One layer of strict validation at the boundary protects everything inside.

---

## Python

### Type hints everywhere

Every function signature has parameter and return type hints. Internal variables get hints when the type isn't obvious from the right-hand side.

> *Why:* `mypy --strict` is gated in CI. More importantly, types are the most honest documentation — they can't be wrong without breaking the build.

Modern union syntax (`str | None`, not `Optional[str]`). Python 3.13 supports this without `from __future__ import annotations`.

### Docstrings

Google-style docstrings on every public function and class. Module docstring at the top of every file: one to three sentences on purpose and dependencies.

```python
def score_listing(listing: Listing, baseline: PriceBaseline) -> DealScore:
    """Compute how undervalued a listing is against its baseline.

    Args:
        listing: A normalised listing with currency-converted price.
        baseline: The trailing-window median for this card and condition.

    Returns:
        A DealScore with the discount ratio and the threshold-relative rating.
    """
```

> *Why:* docstrings are the contract. Anyone calling the function — including future-you six months from now — should not need to read the body to use it correctly.

Private helpers (`_leading_underscore`) can skip docstrings if the name and signature are obvious.

### Naming

| Kind | Convention | Example |
|---|---|---|
| Modules, files | `snake_case` | `price_baseline.py` |
| Functions, variables | `snake_case` | `compute_median()` |
| Classes | `PascalCase` | `PriceBaseline` |
| Constants | `UPPER_SNAKE` | `MAX_LISTINGS_PER_POLL` |
| Type aliases | `PascalCase` | `ListingId = str` |
| "Private" by convention | leading `_` | `_normalise_title()` |

### Module structure

A module has one purpose, stated in its docstring. If a module gains a second purpose, split it.

> *Why:* "two purposes in one file" is the start of every god-class. Catch it early.

### Pydantic vs SQLAlchemy vs dataclass

Three different things, three different uses. Don't conflate them.

| Use | When |
|---|---|
| `pydantic.BaseModel` | Anything crossing a system boundary: HTTP request/response bodies, external API payloads, structured LLM outputs, config loaded from `.env`. Validates on construction. |
| SQLAlchemy `Mapped[...]` model | Anything that maps to a database table. Lives in `models/`. Never returned directly from API handlers. |
| `@dataclass` | Plain internal value objects with no validation and no DB mapping. Used for in-memory results between layers. |

> *Why:* using a SQLAlchemy model as an HTTP response leaks DB columns into your public API, and using Pydantic for DB models gives up the ORM's relationship-management. The boundary between layers is exactly where the type changes.

### FastAPI handler patterns

Handlers in `api/` are thin. They:

1. Take typed request models (Pydantic).
2. Pull a DB session and any dependencies from `Depends(...)`.
3. Call into a `services/` function with plain arguments.
4. Map the service's return into a typed response model.
5. Catch typed exceptions and map to HTTP responses (preferably via exception handlers, not per-handler `try/except`).

```python
@router.post("/cards/{card_id}/threshold", response_model=ThresholdResponse)
def set_threshold(
    card_id: str,
    body: ThresholdRequest,
    session: Session = Depends(get_session),
) -> ThresholdResponse:
    threshold = card_service.set_threshold(session, card_id, body.max_price)
    return ThresholdResponse.from_domain(threshold)
```

> *Why:* if every handler can do its job in five lines, business logic is reachable from jobs, tests, and other entrypoints — and the route module stays scannable.

### SQLAlchemy patterns

- Use the 2.x typed declarative API: `class Card(Base): id: Mapped[str] = mapped_column(primary_key=True)`. The legacy `Column(...)` style is out.
- One `Base` per project, defined in `db/base.py`.
- Sessions are scoped per-request (FastAPI) or per-job-run (scheduled jobs), opened by a context manager, never global.
- Write queries with `select(...)`, not the legacy `Query` interface.
- Prefer `session.scalars(select(Card).where(...))` over raw SQL. Drop to raw SQL only for things the ORM makes ugly (CTEs, window functions, bulk upserts) — and write the raw SQL in `db/queries/` so it's visible.

> *Why:* the typed API plays well with `mypy --strict`. The legacy API doesn't, and mixing styles guarantees you'll have to relearn one of them in a panic.

### Async vs sync

Default to **sync**. Use async only when you need to make multiple external calls at the same time and wait on all of them together (e.g. fan out to three APIs, collect all three results). Async forces every function in its call chain to also be async — so you pay that cost across the whole stack, not just one function. For a single-user personal project, sync is fast enough and much easier to debug.

### Exceptions

- Define typed exceptions in `core/errors.py`, all subclassing a single `TempestWatchError`.
- Raise at the deepest layer that knows enough to name the failure (`ListingNotFound`, not generic `ValueError`).
- Catch at handler/job boundaries only. Internal code doesn't catch unless it can genuinely recover.

> *Why:* a typed exception at the boundary maps trivially to an HTTP code or a log line. A bare `except:` half-way down the stack hides the failure and breaks the stack trace.

---

## TypeScript

### Strict mode, no escape hatch

`strict: true` in `tsconfig.json`, no `any` without a `// reason:` comment explaining why no other type fits.

> *Why:* `any` is contagious. One `any` in a return type infects every caller. The `// reason:` comment makes it an explicit choice that survives code review (or self-review weeks later).

### Naming

| Kind | Convention | Example |
|---|---|---|
| Files | `kebab-case.ts` / `kebab-case.tsx` | `card-archive.tsx` |
| Components | `PascalCase` | `CardArchive` |
| Types, interfaces | `PascalCase` | `ListingResponse` |
| Functions, variables, hooks | `camelCase` | `useCardListings`, `formatPrice` |
| Constants | `UPPER_SNAKE` | `MAX_VISIBLE_CARDS` |

> *Why:* `kebab-case` for files avoids cross-platform case-sensitivity bugs (Windows is case-insensitive, Linux isn't — `Card.tsx` vs `card.tsx` will silently break a deploy).

### One exported component per file

Unless components are tightly coupled (a `<List>` and its `<ListItem>` rendered only by it), each component lives in its own file.

> *Why:* file path = component identity. Jumping to a component is a path lookup, not a fuzzy symbol search.

### JSDoc on exports only

Public components and exported functions get a short JSDoc that explains *intent* (what this is *for*, when to use it), never *what the code does*. Internal helpers skip JSDoc.

```ts
/**
 * Renders a single card in 3D with a flip animation. Used in the archive grid
 * and the per-card detail view. The holographic shader is applied only for
 * rarities listed in `HOLOFOIL_RARITIES`.
 */
export function CardMesh({ card }: { card: Card }) { ... }
```

### State management

- React local state (`useState`, `useReducer`) is the default.
- Server state (data from the API) goes through `react-query` / TanStack Query. Don't put server state in Redux/Zustand/Context.
- Global UI state (sidebar open, user theme) — Zustand if you need it, Context if it's truly tiny. Avoid prop drilling past three layers.

> *Why:* the most common React mistake is using a global store for data that's really server state, then writing a sync layer between them. Server-state libraries solve cache invalidation, loading states, and refetches for free.

### Styling

No inline styles. All styling goes in CSS/SCSS files. Do not use `style={{ ... }}` on JSX elements.

`!important` is banned except as a last resort when a third-party library leaves no other option — add a comment explaining why if you use it.

### Three.js isolation

All Three.js code lives in `frontend/src/three/`. React components import from there but never define scenes, shaders, or render loops inline.

> *Why:* a stray `useFrame` inside a React render function is a hot loop running at 60fps, gated by React's reconciler. That's a battery drain at best and a deadlock at worst. The discipline is: React owns the DOM tree, Three owns the canvas, they meet at exactly one boundary.

GLSL shader source: separate `.glsl` files imported as strings, or template literals in a dedicated `*.shader.ts` file. Never inline GLSL inside a component file.

### Imports

- Absolute imports from `@/` for anything inside `src/`. Relative imports only for siblings in the same folder.
- Group imports: external (`react`, `three`), then internal (`@/components/...`), then sibling (`./helper`).
- Never `import *`. Named imports only.

> *Why:* relative imports across many layers (`../../../components/foo`) break the moment you move a file. Absolute imports survive refactors.

---

## Cross-language

### File length

If a file is over ~400 lines, ask whether it has more than one purpose. The answer is almost always yes.

### Tests mirror source

Every source file has at most one matching test file, at the mirrored path:

```
backend/src/services/scoring.py
backend/tests/services/test_scoring.py
```

```
frontend/src/components/card-archive.tsx
frontend/src/components/card-archive.test.tsx
```

> *Why:* you should never have to ask "where are the tests for this file." The answer is always the mirrored path.

### Dead code

Delete it. Don't comment it out, don't add a `// removed` marker. Git remembers; the codebase shouldn't carry corpses.

> *Why:* commented-out code is a debugging trap — readers waste time wondering whether it's a clue or noise.
