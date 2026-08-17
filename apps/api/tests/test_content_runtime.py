"""Laying a content out, and the ticket that lets it be fetched.

The runtime sits on its own origin, so no session cookie reaches it. What
replaces the cookie is tested here: a ticket that opens exactly one content, for
a while, and the endpoint the content origin asks before serving a byte.

The deployment side is tested on a temporary directory rather than on the shared
volume — what matters is that an archive lands where it should and nowhere else.
"""

from __future__ import annotations

import json
import uuid
import zipfile
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
import redis.asyncio as redis
from fastapi.testclient import TestClient

from app.content.deploy import (
    DeploymentRefused,
    deploy_libraries,
    deploy_package,
    deployed_contents,
    is_deployed,
)
from app.content.tokens import mint_ticket, read_ticket, revoke_ticket
from app.core.config import settings
from app.core.security import hash_session_token
from app.main import app

ACCESS_URL = "/api/v1/internal/content-access"
DIGEST = "a" * 64
OTHER_DIGEST = "b" * 64


@pytest.fixture
def runtime(tmp_path: Path) -> Path:
    root = tmp_path / "runtime"
    root.mkdir()
    return root


@pytest.fixture
async def client_redis() -> Any:
    client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    yield client
    await client.aclose()


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


def package(path: Path, entries: dict[str, bytes] | None = None) -> Path:
    manifest = {
        "title": "Question",
        "mainLibrary": "H5P.TrueFalse",
        "license": "U",
        "preloadedDependencies": [
            {"machineName": "H5P.TrueFalse", "majorVersion": "1", "minorVersion": "8"}
        ],
    }
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("h5p.json", json.dumps(manifest))
        archive.writestr("content/content.json", json.dumps({"correct": "true"}))
        for name, body in (entries or {}).items():
            archive.writestr(name, body)
    return path


class TestDeployment:
    def test_a_package_is_laid_out_under_its_digest(
        self, runtime: Path, tmp_path: Path
    ) -> None:
        report = deploy_package(runtime, package(tmp_path / "p.h5p"), DIGEST)

        assert report.path == f"content/{DIGEST}"
        assert (runtime / "content" / DIGEST / "h5p.json").is_file()
        assert (runtime / "content" / DIGEST / "content" / "content.json").is_file()
        assert is_deployed(runtime, DIGEST) is True

    def test_redeploying_the_same_digest_replaces_it(
        self, runtime: Path, tmp_path: Path
    ) -> None:
        """The digest names the folder, so this is idempotent by construction."""
        deploy_package(runtime, package(tmp_path / "p.h5p"), DIGEST)
        deploy_package(runtime, package(tmp_path / "p.h5p"), DIGEST)

        assert deployed_contents(runtime) == [DIGEST]

    def test_two_contents_do_not_collide(self, runtime: Path, tmp_path: Path) -> None:
        deploy_package(runtime, package(tmp_path / "un.h5p"), DIGEST)
        deploy_package(runtime, package(tmp_path / "deux.h5p"), OTHER_DIGEST)

        assert deployed_contents(runtime) == sorted([DIGEST, OTHER_DIGEST])

    @pytest.mark.parametrize("name", ["../evade.txt", "/etc/passwd"])
    def test_an_entry_leaving_the_folder_is_refused(
        self, runtime: Path, tmp_path: Path, name: str
    ) -> None:
        """The same refusal as the inspection of 08.2, repeated where it writes.

        Not distrust of the earlier check but of the interval between them: what
        is opened here was read back from storage.
        """
        archive = package(tmp_path / "hostile.h5p", {name: b"x"})

        with pytest.raises(DeploymentRefused):
            deploy_package(runtime, archive, DIGEST)

    @pytest.mark.parametrize("digest", ["court", "../../etc", "a" * 63, "A" * 64 + "!"])
    def test_a_digest_that_is_not_one_is_refused(
        self, runtime: Path, tmp_path: Path, digest: str
    ) -> None:
        """It becomes a directory name, so it is checked before it is one."""
        with pytest.raises(DeploymentRefused):
            deploy_package(runtime, package(tmp_path / "p.h5p"), digest)

    def test_an_archive_without_a_manifest_leaves_nothing_behind(
        self, runtime: Path, tmp_path: Path
    ) -> None:
        empty = tmp_path / "vide.h5p"
        with zipfile.ZipFile(empty, "w") as archive:
            archive.writestr("content/content.json", "{}")

        with pytest.raises(DeploymentRefused):
            deploy_package(runtime, empty, DIGEST)
        assert deployed_contents(runtime) == []

    def test_libraries_are_laid_out_with_an_inventory_of_their_digests(
        self, runtime: Path, tmp_path: Path
    ) -> None:
        """ADR-012 asks for frozen artefacts; one nobody can name is not frozen."""
        prepared = tmp_path / "prepared"
        (prepared / "H5P.TrueFalse-1.8").mkdir(parents=True)
        (prepared / "H5P.TrueFalse-1.8" / "library.json").write_text("{}")

        inventory = deploy_libraries(runtime, prepared)

        assert "H5P.TrueFalse-1.8/library.json" in inventory
        assert len(inventory["H5P.TrueFalse-1.8/library.json"]) == 64
        assert json.loads((runtime / "inventory.json").read_text()) == inventory

    def test_libraries_from_a_missing_directory_are_refused(
        self, runtime: Path, tmp_path: Path
    ) -> None:
        with pytest.raises(DeploymentRefused):
            deploy_libraries(runtime, tmp_path / "absent")


class TestTickets:
    async def test_a_ticket_names_one_content_and_one_assignment(
        self, client_redis: Any
    ) -> None:
        assignment_id = uuid.uuid4()

        token = await mint_ticket(client_redis, assignment_id, DIGEST)
        ticket = await read_ticket(client_redis, token)

        assert ticket is not None
        assert ticket.assignment_id == assignment_id
        assert ticket.content_digest == DIGEST
        await revoke_ticket(client_redis, token)

    async def test_a_value_that_was_never_minted_opens_nothing(
        self, client_redis: Any
    ) -> None:
        assert await read_ticket(client_redis, "jamais-emis") is None

    async def test_a_revoked_ticket_opens_nothing(self, client_redis: Any) -> None:
        token = await mint_ticket(client_redis, uuid.uuid4(), DIGEST)

        await revoke_ticket(client_redis, token)

        assert await read_ticket(client_redis, token) is None

    async def test_the_store_holds_the_digest_of_the_ticket_and_not_the_ticket(
        self, client_redis: Any
    ) -> None:
        """Whoever reads the store learns which contents are open, never the
        tickets that open them — exactly as for sessions."""
        token = await mint_ticket(client_redis, uuid.uuid4(), DIGEST)

        keys = [key async for key in client_redis.scan_iter("content-ticket:*")]

        assert not any(token in key for key in keys)
        await revoke_ticket(client_redis, token)

    async def test_a_ticket_expires_on_its_own(self, client_redis: Any) -> None:
        token = await mint_ticket(client_redis, uuid.uuid4(), DIGEST)

        remaining = await client_redis.ttl(
            f"content-ticket:{hash_session_token(token)}"
        )

        assert 0 < remaining <= 30 * 60
        await revoke_ticket(client_redis, token)


class TestWhatTheOriginAsks:
    """The endpoint nginx calls before serving a byte.

    The ticket is a **path segment**. It used to be a query parameter, and that
    was wrong for a reason worth keeping: the H5P player builds asset URLs by
    joining path segments, so a query string was dropped the moment it fetched
    anything of its own, and every asset reached the origin unticketed. No test
    caught it because these tests wrote the URI by hand, and a hand writes the
    URI the design expects rather than the one the player produces.
    """

    async def test_a_valid_ticket_for_that_content_is_allowed(
        self, client: TestClient, client_redis: Any
    ) -> None:
        token = await mint_ticket(client_redis, uuid.uuid4(), DIGEST)

        response = client.get(
            ACCESS_URL,
            headers={"X-Original-URI": f"/t/{token}/content/{DIGEST}/h5p.json"},
        )

        assert response.status_code == 204
        await revoke_ticket(client_redis, token)

    async def test_a_library_needs_only_a_valid_ticket(
        self, client: TestClient, client_redis: Any
    ) -> None:
        """Libraries are shared by every content, so no digest is checked."""
        token = await mint_ticket(client_redis, uuid.uuid4(), DIGEST)

        response = client.get(
            ACCESS_URL,
            headers={"X-Original-URI": f"/t/{token}/libraries/H5P.TrueFalse-1.8/x.js"},
        )

        assert response.status_code == 204
        await revoke_ticket(client_redis, token)

    async def test_a_deep_asset_path_is_allowed(
        self, client: TestClient, client_redis: Any
    ) -> None:
        """What the player actually asks for, not what a hand would write."""
        token = await mint_ticket(client_redis, uuid.uuid4(), DIGEST)

        response = client.get(
            ACCESS_URL,
            headers={
                "X-Original-URI": f"/t/{token}/content/{DIGEST}/content/images/a.png"
            },
        )

        assert response.status_code == 204
        await revoke_ticket(client_redis, token)

    async def test_a_ticket_for_another_content_is_refused(
        self, client: TestClient, client_redis: Any
    ) -> None:
        """One ticket opens one content, and nothing helps guess a second."""
        token = await mint_ticket(client_redis, uuid.uuid4(), DIGEST)

        response = client.get(
            ACCESS_URL,
            headers={"X-Original-URI": f"/t/{token}/content/{OTHER_DIGEST}/h5p.json"},
        )

        assert response.status_code == 403
        await revoke_ticket(client_redis, token)

    def test_a_path_without_a_ticket_segment_is_refused(
        self, client: TestClient
    ) -> None:
        """The old shape, and any other: not a different way in, no way in."""
        response = client.get(
            ACCESS_URL, headers={"X-Original-URI": f"/content/{DIGEST}/h5p.json"}
        )

        assert response.status_code == 403

    def test_a_request_with_no_uri_at_all_is_refused(self, client: TestClient) -> None:
        assert client.get(ACCESS_URL).status_code == 403

    def test_an_invented_ticket_is_refused(self, client: TestClient) -> None:
        response = client.get(
            ACCESS_URL,
            headers={"X-Original-URI": f"/t/invente/content/{DIGEST}/x"},
        )

        assert response.status_code == 403

    async def test_the_answer_carries_nothing_but_its_status(
        self, client: TestClient, client_redis: Any
    ) -> None:
        """nginx has no use for a body, and one that explained itself would
        explain itself to whoever asked."""
        token = await mint_ticket(client_redis, uuid.uuid4(), DIGEST)

        allowed = client.get(
            ACCESS_URL,
            headers={"X-Original-URI": f"/t/{token}/content/{DIGEST}/x"},
        )
        refused = client.get(
            ACCESS_URL,
            headers={"X-Original-URI": f"/t/x/content/{DIGEST}/x"},
        )

        assert allowed.content == b""
        assert b"ticket" not in refused.content.lower()
        await revoke_ticket(client_redis, token)
