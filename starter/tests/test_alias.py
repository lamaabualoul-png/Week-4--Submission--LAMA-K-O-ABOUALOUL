"""Behavioral tests for the custom-alias feature (dirST /shorten with `alias`)."""


def shorten(client, url="https://example.com", **extra):
    return client.post("/shorten", json={"url": url, **extra})


def test_custom_alias_is_used_as_code(client):
    r = shorten(client, alias="promo")
    assert r.status_code == 200
    assert r.json() == {"code": "promo", "short_url": "/promo"}


def test_custom_alias_redirects_to_original_url(client):
    shorten(client, url="https://example.org/page", alias="my-link")
    r = client.get("/my-link", follow_redirects=False)
    assert r.status_code == 307
    assert r.headers["location"] == "https://example.org/page"


def test_duplicate_alias_returns_409(client):
    assert shorten(client, alias="taken").status_code == 200
    r = shorten(client, url="https://other.com", alias="taken")
    assert r.status_code == 409
    assert r.json() == {"detail": "alias already taken"}


def test_duplicate_alias_does_not_overwrite_original(client):
    shorten(client, url="https://first.com", alias="keep")
    shorten(client, url="https://second.com", alias="keep")
    r = client.get("/keep", follow_redirects=False)
    assert r.headers["location"] == "https://first.com"


def test_aliases_are_case_sensitive(client):
    assert shorten(client, alias="Abc").status_code == 200
    assert shorten(client, alias="abc").status_code == 200


def test_alias_cannot_shadow_builtin_routes(client):
    for reserved in ["docs", "redoc", "openapi.json", "shorten"]:
        assert shorten(client, alias=reserved).status_code in (400, 409)
    # the built-in page must still be served
    assert client.get("/docs").status_code == 200


def test_invalid_alias_characters_return_400(client):
    for bad in ["has space", "a/b", "q?x", "", "x" * 33]:
        r = shorten(client, alias=bad)
        assert r.status_code == 400, bad


def test_alias_still_requires_valid_url(client):
    r = shorten(client, url="ftp://nope", alias="okalias")
    assert r.status_code == 400


def test_no_alias_still_generates_code(client):
    r = shorten(client)
    assert r.status_code == 200
    assert r.json()["code"]


def test_generated_code_skips_a_code_claimed_as_alias(client):
    # Row ids 1, 2, 3 would auto-generate "b", "c", "d". Claim "d" as an alias
    # on row 2 so the third auto-generated code would collide with it.
    first = shorten(client).json()["code"]
    claimed = shorten(client, url="https://claimed.com", alias="d")
    assert claimed.json()["code"] == "d"
    third = shorten(client, url="https://third.com")
    assert third.status_code == 200
    assert len({first, "d", third.json()["code"]}) == 3
    # the alias must still point at the url that claimed it
    r = client.get("/d", follow_redirects=False)
    assert r.headers["location"] == "https://claimed.com"
