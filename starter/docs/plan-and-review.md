# Agent session record: Custom alias

Three separate stages, as the assignment requires. Stage 1 and 3 made no edits.

## Stage 1 - PLAN (read-only)

**Task:** Custom alias - `POST /shorten` accepts optional `alias`; use it as the code
if available, otherwise return 409.

**Inspection of `main.py`:** codes are `encode(row_id)`; `code` has a UNIQUE
constraint; `GET /{code}` is a catch-all registered after `/shorten`.

**Proposed plan**
1. Add `alias: str | None = None` to `ShortenRequest`.
2. If `alias` is given: validate it, check availability, store it as `code`.
3. Return 409 `{"detail": "alias already taken"}` when it is unavailable.
4. Tests (new, in `tests/`): alias works and redirects; duplicate alias -> 409;
   invalid alias -> 400; no-alias behavior unchanged.

**Risks the plan surfaced (beyond the task text)**
- **Collision with generated codes.** Generated codes are base62 of the row id
  (`1`, `2`, ... `a`, `b`...). If someone claims alias `"b"`, a later auto-generated
  code `"b"` hits the UNIQUE constraint and `/shorten` would 500. Generated codes
  must skip codes already in use.
- **Shadowed paths.** FastAPI serves `/docs`, `/redoc`, `/openapi.json` before the
  catch-all, so an alias of `docs` would be stored but unreachable. Reserve these.
- **Unsafe alias characters.** Aliases land in a URL path; restrict to
  `[A-Za-z0-9_-]`, 1-32 chars, to avoid `/`, spaces, `?`, `#`.
- **Test isolation.** Tests share `links.db`; a fixed alias like `"promo"` would
  make tests fail on the second run. Needs a per-test temporary database.
- **Race on alias claim.** Two simultaneous requests could both pass an existence
  check; rely on the UNIQUE constraint and map `IntegrityError` to 409.

## Stage 2 - IMPLEMENT (via `.agents/skills/implement-feature/SKILL.md`)

Followed the skill's seven steps. Tests were written first and confirmed failing
for the expected reason (200 returned where 400/409 expected) - 7 red. While
re-reading my own tests before implementing I caught a bug in the collision
test (alias `"c"` does not collide with anything; row 3 -> `"d"` does) and fixed
the test first. Implementation then took `pytest` from 7 red to 13 green.
Files changed: `main.py`; added `tests/`, `pytest.ini`, `.gitignore`.

## Stage 3 - REVIEW (read-only)

**Decision: REVISE**

Checked: success path, duplicate -> 409, invalid -> 400, reserved names, collision
with generated codes, original tests unchanged, tests order-independent.

Findings:
1. `except sqlite3.IntegrityError` mapped *every* integrity error to
   `409 "alias already taken"`. A race on an auto-generated code (no alias
   supplied) would be mislabeled. **Fix applied:** only translate to 409 when an
   alias was supplied; otherwise re-raise.

Residual risks (accepted, out of scope): the check-then-claim loop in
`next_free_code` is not atomic under heavy concurrency (a second writer could win
the same code; the UNIQUE constraint still prevents duplicates). Reserved-name
list is hand-maintained.

**Re-review after fix: ACCEPT** - `pytest`: 13 passed (3 original + 10 new).
