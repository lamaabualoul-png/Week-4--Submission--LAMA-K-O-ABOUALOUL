# Starter — Link Shortener

A tiny FastAPI + SQLite service that you will make easier for a coding agent to understand and modify. The application already works; you will add repository guidance, one scoped instruction, one reusable workflow, and complete one feature.

## Setup

```bash
pip install -r requirements.txt
pytest                       # 13 tests should pass
uvicorn main:app --reload    # http://localhost:8000  (docs at /docs)
```

## Try it

```bash
curl -X POST localhost:8000/shorten -H 'Content-Type: application/json' \
  -d '{"url":"https://example.com"}'
# -> {"code":"b","short_url":"/b"}  then GET localhost:8000/<code> redirects
```

## Files

- `main.py` — the app (`POST /shorten`, `GET /{code}`)
- `tests/` — pytest suite (`test_main.py` original, `test_alias.py` for custom aliases, `conftest.py` isolates the DB)
- `AGENTS.md`, `tests/AGENTS.md`, `.agents/skills/implement-feature/SKILL.md` — agent guidance, scoped rule, reusable workflow
- `writeup.md`, `docs/plan-and-review.md` — assignment writeup and plan/implement/review record
- `docs/TASKS.md` — choose one feature to implement

Start by running the existing tests, then read all three files before adding agent guidance.


## Custom alias

```bash
curl -X POST localhost:8000/shorten -H 'Content-Type: application/json' \
  -d '{"url":"https://example.com","alias":"hello"}'   # -> {"code":"hello",...}; reuse -> 409
```
