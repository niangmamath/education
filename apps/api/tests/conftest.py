"""What every test run must leave behind: nothing of its own.

Several modules build a family to test with — a parent, her children, their
assignments, attempts and readings — and most of them never took it back. After
a few dozen runs the database held five hundred parents and four hundred
children, all fictional, all invisible until somebody counted them. Nothing
broke, which is exactly why it went unnoticed: leaked rows are quiet.

They are not harmless, though. A test that reads "every child of this parent"
passes either way, but a page, a query plan or a person looking at the database
sees a crowd that no one intended.

So the sweep lives here, once, rather than in each module that remembers. Every
test address belongs to `example.com` — RFC 2606, and the project's own
convention — so that is what it looks for.

**The demonstration data is spared by name.** It also lives at `example.com`, and
a developer who seeds a demonstration and then runs the tests should not find it
gone. `--clean` is what removes that, deliberately, by hand.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine, text

from app.core.db import sync_database_url

DEMO_PREFIX = "demo-"


@pytest.fixture(scope="session", autouse=True)
def sweep_test_accounts() -> Iterator[None]:
    """Remove the fictional accounts a run created, once it is over.

    Deleting a parent takes her children, their assignments, attempts, responses
    and readings with her, by the cascades the schema already declares. There is
    nothing else to chase.
    """
    yield

    engine = create_engine(sync_database_url())
    try:
        with engine.begin() as connection:
            connection.execute(
                text(
                    "DELETE FROM auth_parents "
                    "WHERE email LIKE '%@example.com' AND email NOT LIKE :demo"
                ),
                {"demo": f"{DEMO_PREFIX}%"},
            )
    finally:
        engine.dispose()
