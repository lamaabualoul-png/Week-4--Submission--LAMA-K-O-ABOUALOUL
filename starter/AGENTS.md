# Agent guide — Link Shortener

A tiny FastAPI + SQLite service. `POST /shorten` stores a URL and returns a short
code; `GET /{code}` redirects (307) to the stored URL. That is the whole product.

## Where things are

| Path | Purpose |
| --- | --- |
| `main.py` | The entire app: DB helpers, `encode()`, both routes |
| `tests/test_main.py` | Original behavioral tests |
| `tests/conftest.py` | Gives every test its own temporary database |
| `tests/AGENTS.md` | Extra rules that apply only when editing tests |
| `docs/TASKS.md` | Candidate features; one is implemented (see `writeup.md`) |
| `.agents/skills/implement-feature/` | Reusable workflow for adding a feature |

## Commands (run from this directory)

```bash
pip install -r requirements.txt
pytest                         # must stay green
uvicorn main:app --reload      # http://localhost:8000, docs at /docs
```

## Behavior to preserve

- Codes are base62 of the row id; the redirect status is 307.
- Bad URL (not http/https) -> 400 `{"detail": ...}`. Unknown code -> 404.
- Errors are `HTTPException` with a `detail` message, never a traceback.
- `GET /{code}` is a catch-all, so any new fixed route must not be shadowable by it.

## Product boundaries

In scope: shortening, redirecting, and small per-link features (alias, stats, expiry).
Out of scope unless asked: auth, users, rate limiting, a frontend, another database,
splitting `main.py` into packages, new dependencies.

## Change workflow

1. **Understand** - read the task, `main.py`, and the nearest tests.
2. **Test** - add a failing behavioral test (success and failure) first.
3. **Implement** - smallest change that makes it pass; keep new behavior in `main.py`.
4. **Verify** - run `pytest`; report what passed and any remaining risk.

For a feature, follow `.agents/skills/implement-feature/SKILL.md`.
Ask a person before adding dependencies or changing the database schema destructively.
