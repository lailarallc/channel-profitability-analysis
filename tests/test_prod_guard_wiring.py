"""The prod guard sits in front of the Postgres read in scripts/generate_json.py.

_pg_connect() reads DATABASE_URL, or localhost:5432 when POSTGRES_PASSWORD is
set -- a `fly proxy` tunnel to production when one is open. These tests fake
a flyctl listener and assert nothing connects. psycopg2 is stubbed so this
runs in CI, where only pytest is installed.
"""

import importlib.util
import pathlib
import sys
import types

import pytest

SCRIPTS = pathlib.Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import prod_guard  # noqa: E402  (scripts/prod_guard.py, as the script imports it)


@pytest.fixture
def gen(monkeypatch):
    seen = []
    monkeypatch.delenv("ALLOW_PROD_DB", raising=False)
    monkeypatch.setattr(prod_guard, "_listener", lambda port: seen.append(port) or "flyctl")
    spec = importlib.util.spec_from_file_location("generate_json", SCRIPTS / "generate_json.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod._HAS_PG = True
    mod.psycopg2 = types.SimpleNamespace(connect=lambda *a, **kw: pytest.fail("connected"))
    mod.seen = seen
    return mod


def test_database_url_refuses_fly_tunnel(gen, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://localhost:5432/db")
    with pytest.raises(prod_guard.ProdDatabaseError):
        gen._pg_connect()
    assert gen.seen == [5432]


def test_password_fallback_refuses_fly_tunnel(gen, monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("POSTGRES_PASSWORD", "x")
    with pytest.raises(prod_guard.ProdDatabaseError):
        gen.fetch_live_channel_data()
    assert gen.seen == [5432]
