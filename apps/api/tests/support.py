"""Helpers shared by the referential tests.

Only one edition of the referential may be in force at a time, and a partial
unique index enforces it. Any test that publishes an edition therefore collides
with whatever the machine already has published — which, since 07.3, is the
normal state of a working database rather than an oddity.

Rather than require a pristine database, these tests step the incumbent aside
for their duration and put it back afterwards. They then neither depend on the
local state nor destroy it.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import Engine, text
from sqlalchemy.orm import Session

from app.models.referential import VERSION_STATUS_DRAFT
from app.referential.publication import published_version


@contextmanager
def no_edition_in_force(engine: Engine, cleanup_prefix: str) -> Iterator[None]:
    """Leave no edition published, then restore the one that was.

    `cleanup_prefix` names the test editions to delete on the way out, so that
    the incumbent can be put back without a second edition claiming the index.
    """
    with Session(engine) as session:
        incumbent = published_version(session)
        incumbent_code = incumbent.code if incumbent is not None else None
        if incumbent is not None:
            incumbent.status = VERSION_STATUS_DRAFT
            session.commit()

    try:
        yield
    finally:
        with engine.begin() as connection:
            connection.execute(
                text("DELETE FROM ref_versions WHERE code LIKE :pattern"),
                {"pattern": f"{cleanup_prefix}%"},
            )
            if incumbent_code is not None:
                connection.execute(
                    text(
                        "UPDATE ref_versions SET status = 'published' WHERE code = :code"
                    ),
                    {"code": incumbent_code},
                )
