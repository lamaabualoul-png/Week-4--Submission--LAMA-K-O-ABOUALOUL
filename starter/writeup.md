# Week 4 Writeup — Agent-Ready Link Shortener

**Feature implemented:** Task 1, Custom alias (`POST /shorten` accepts optional `alias`; 409 if taken).

**1. What is in `AGENTS.md` and why broadly available?**
It holds what every task needs: a one-paragraph product description, a file map, install/run/test commands, behavior to preserve (307 redirects, 400/404 error shapes, the catch-all `GET /{code}` route), product boundaries (no auth, no new dependencies, no restructuring), and the understand → test → implement → verify loop. At 46 lines, it stays cheap to load on every task.

**2. What did I scope, and when does it load?**
`tests/AGENTS.md` contains testing rules: use the public API through `TestClient`, cover success and failure, keep tests independent via the per-test database fixture, assert behavior rather than internals. It applies only to files under `tests/`. Loading it while editing only `main.py` would waste context on rules that cannot apply.

**3. What does the reusable workflow encode?**
`.agents/skills/implement-feature/SKILL.md` encodes the seven-step feature procedure: read the task and guidance; inspect related code and tests; state behavior and affected files; write a failing behavioral test and confirm it fails for the *expected* reason; make the smallest change; run `pytest`; summarize with a fixed template (behavior, files, tests, result, risks).

**4. How are the artifacts discovered or invoked?**
- `AGENTS.md`: read automatically as repository-root context under the cross-tool convention.
- `tests/AGENTS.md`: discovered through the same convention, as the nearest `AGENTS.md` to files being edited.
- Skill: the agent sees its `name` and `description` and loads the body when a feature task matches, or I invoke it by name. Other tools: Cursor `.cursor/skills/`, Claude Code `.claude/skills/` (same `SKILL.md` format).

**5. What did planning and review catch?**
Planning, done before any edit, found risks the task text did not mention: an alias such as `"d"` would collide with a later auto-generated code and crash `/shorten` with a 500; aliases like `docs` would be stored but shadowed by FastAPI's built-in routes; aliases need character limits because they appear in URL paths; and tests sharing `links.db` would fail on a second run. Each became code or a test. Review returned **REVISE**: my `IntegrityError` handler labeled every database conflict "alias already taken," including failures on auto-generated codes. I fixed it, and the second review returned ACCEPT with 13 passing tests (3 original, 10 new).

**6. What did I learn?**
Agents do best with a short always-on map plus narrow, conditional rules; a long single file dilutes both. Procedures belong in a skill, not in `AGENTS.md`. Separating plan, implement, and review stages produced better results than one pass, because the reviewer judged evidence (a failing-then-passing test) rather than the implementer's confidence. Finally, test infrastructure such as the isolated database is part of the agent-ready surface: without it, an agent's correct code looks flaky.

Session record: `docs/plan-and-review.md`.
