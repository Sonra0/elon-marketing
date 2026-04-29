"""pytest config.

Two test scopes:
- unit: pure-python, no Postgres or network. Always runs.
- integration: requires DATABASE_URL pointing at a real Postgres + pgvector.
  Skipped when not provided.

NOTE: env defaults are set at module load (before any `from elon...` import the
suite triggers) so cached Settings see them.
"""

from __future__ import annotations

import base64
import os

import nacl.utils
import pytest

# Module-level env defaults — must run before any `elon.*` import.
os.environ.setdefault("SECRET_BOX_KEY", base64.b64encode(nacl.utils.random(32)).decode())
os.environ.setdefault("ANTHROPIC_API_KEY", "sk-test")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/15")


def pytest_collection_modifyitems(config, items):
    if not os.getenv("DATABASE_URL"):
        skip_int = pytest.mark.skip(reason="integration tests require DATABASE_URL")
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_int)
