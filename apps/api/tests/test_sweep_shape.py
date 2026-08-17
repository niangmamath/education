"""The sweep must recognise what it deletes.

This exists because the first version did not. It removed every account at
`example.com`, which is where a person testing the product by hand puts theirs —
the domain is reserved for that, RFC 2606, so it is the obvious thing to type.
An account created in the morning was gone by the first `pytest` of the
afternoon, silently.

A sweep that deletes more than it recognises is a sweep nobody can trust, so the
shape it matches is pinned here.
"""

from __future__ import annotations

import re
import uuid

import pytest

from tests.conftest import GENERATED_ACCOUNT

SHAPE = re.compile(GENERATED_ACCOUNT)


@pytest.mark.parametrize("prefix", ["ten", "xapi", "prog", "dia", "cat", "exam", "asg"])
def test_it_matches_what_the_modules_generate(prefix: str) -> None:
    assert SHAPE.match(f"{prefix}-{uuid.uuid4().hex}@example.com")


@pytest.mark.parametrize(
    "address",
    [
        "camille.martin@example.com",
        "parent@example.com",
        "tidiane@example.com",
        "demo-parent.martin@example.com",
        "essai-2026@example.com",
        "ten-pas-un-uuid@example.com",
        "ten-0123456789abcdef@example.com",
    ],
)
def test_it_spares_anything_a_person_would_type(address: str) -> None:
    """Including the demonstration's own accounts, and short-hand test ones."""
    assert SHAPE.match(address) is None


def test_it_leaves_other_domains_alone() -> None:
    assert SHAPE.match(f"ten-{uuid.uuid4().hex}@studentconnect.local") is None
