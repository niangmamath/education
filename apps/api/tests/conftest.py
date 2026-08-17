"""What every test run must leave behind: nothing of its own, and nothing else.

Several modules build a family to test with — a parent, her children, their
assignments, attempts and readings — and most of them never took it back. After
a few dozen runs the database held five hundred and sixty parents and four
hundred children, all fictional, all invisible until somebody counted them.
Nothing broke, which is exactly why it went unnoticed: leaked rows are quiet.

**The first version of this sweep was worse than the leak.** It deleted every
account at `example.com`, which is also where a person testing the product by
hand puts theirs — that domain is reserved for exactly this kind of use, RFC
2606, so it is the obvious thing to type. An account created deliberately in the
morning was gone by the first `pytest` of the afternoon, silently, and the person
who created it had no way to guess why.

So the sweep matches the **shape** the modules generate and nothing else: a short
lowercase prefix, a hyphen, and the thirty-two hexadecimal characters of a
`uuid4().hex`. Nobody types that by hand, and a module added later gets swept
without anyone maintaining a list — as long as it follows the same convention,
which every one of them already does.

Anything that does not match that shape is left alone, whatever domain it is on.
A sweep that deletes more than it recognises is a sweep nobody can trust.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine, text

from app.core.db import sync_database_url

# `prefix-<32 hex>@example.com`, and nothing else.
GENERATED_ACCOUNT = r"^[a-z]+-[0-9a-f]{32}@example\.com$"


@pytest.fixture(scope="session", autouse=True)
def sweep_generated_accounts() -> Iterator[None]:
    """Remove the accounts a run generated, once it is over.

    Deleting a parent takes her children, their assignments, attempts, responses
    and readings with her, by the cascades the schema already declares. There is
    nothing else to chase.
    """
    yield

    engine = create_engine(sync_database_url())
    try:
        with engine.begin() as connection:
            connection.execute(
                text("DELETE FROM auth_parents WHERE email ~ :shape"),
                {"shape": GENERATED_ACCOUNT},
            )
    finally:
        engine.dispose()
