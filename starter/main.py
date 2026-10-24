"""Link Shortener — starter app for Week 5.

A deliberately tiny FastAPI service you will make *agent-native*. Run it, read it,
then use your coding agent (Antigravity by default) plus the tasks in docs/TASKS.md.

Run:
    pip install -r requirements.txt
    uvicorn main:app --reload
Test:
    pytest
"""
import re
import sqlite3
import string
from contextlib import closing
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

DB_PATH = Path(__file__).parent / "links.db"
ALPHABET = string.ascii_letters + string.digits
ALIAS_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,32}$")
# Paths served before the catch-all `GET /{code}`; an alias with these names
# would be stored but could never be reached.
RESERVED_ALIASES = {"shorten", "docs", "redoc", "openapi.json"}

app = FastAPI(title="Link Shortener")


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with closing(get_db()) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS links (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE,
                url  TEXT NOT NULL
            )"""
        )
        conn.commit()


init_db()


def encode(n: int) -> str:
    """Base62-encode a row id into a short code."""
    base = len(ALPHABET)
    if n == 0:
        return ALPHABET[0]
    chars = []
    while n > 0:
        n, r = divmod(n, base)
        chars.append(ALPHABET[r])
    return "".join(reversed(chars))


class ShortenRequest(BaseModel):
    url: str
    alias: str | None = None


def code_exists(conn: sqlite3.Connection, code: str) -> bool:
    return conn.execute("SELECT 1 FROM links WHERE code = ?", (code,)).fetchone() is not None


def next_free_code(conn: sqlite3.Connection, start: int) -> str:
    """Encode `start`, moving forward past codes already claimed (e.g. as aliases)."""
    n = start
    while code_exists(conn, encode(n)):
        n += 1
    return encode(n)


@app.post("/shorten")
def shorten(req: ShortenRequest):
    if not req.url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="url must start with http:// or https://")
    if req.alias is not None and not ALIAS_PATTERN.fullmatch(req.alias):
        raise HTTPException(
            status_code=400,
            detail="alias must be 1-32 characters: letters, digits, '-' or '_'",
        )
    if req.alias in RESERVED_ALIASES:
        raise HTTPException(status_code=409, detail="alias already taken")
    with closing(get_db()) as conn:
        try:
            cur = conn.execute(
                "INSERT INTO links (url, code) VALUES (?, ?)", (req.url, req.alias)
            )
            row_id = cur.lastrowid
            code = req.alias or next_free_code(conn, row_id)
            if req.alias is None:
                conn.execute("UPDATE links SET code = ? WHERE id = ?", (code, row_id))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.rollback()
            if req.alias is None:
                raise  # not an alias problem; surface it rather than mislabel it
            raise HTTPException(status_code=409, detail="alias already taken")
    return {"code": code, "short_url": f"/{code}"}


@app.get("/{code}")
def redirect(code: str):
    with closing(get_db()) as conn:
        row = conn.execute("SELECT url FROM links WHERE code = ?", (code,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="unknown code")
    return RedirectResponse(url=row["url"], status_code=307)
