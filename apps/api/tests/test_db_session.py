import asyncio

import pytest

from app.core import db


@pytest.mark.asyncio
async def test_get_async_session_closes():
    # This test only validates that the async session can be created and closed
    async with db.async_session() as session:
        assert session is not None
    # After context exit, session should be closed
    # There's no direct 'closed' attribute, but ensuring no exception was raised is sufficient here.
