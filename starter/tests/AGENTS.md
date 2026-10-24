# Test rules (apply only to files under `tests/`)

- Test through the public API with `TestClient`. Do not import or assert on
  private helpers or call SQLite directly (use `client` from `conftest.py`).
- Every behavior gets at least one success test and one failure/edge test
  (check status code **and** response body).
- Tests must be independent: no reliance on execution order, shared ids, or
  codes created by another test. The `conftest.py` autouse fixture gives each
  test a fresh database - never delete or bypass it.
- Assert observable behavior (status, JSON body, `location` header, later
  `GET` results), not implementation details such as how a code is generated.
- Use `follow_redirects=False` when checking redirects.
- Name tests `test_<behavior>_<expected result>`; keep each to one behavior.
