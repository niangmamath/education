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

from app.content import deploy
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


class TestImportingLibrariesFromAPackage:
    """Taking a downloaded package's libraries into the shared tree.

    This is the whole of "preparing a library offline" once a new type is
    admitted: an `.h5p` already carries what it needs to play, so nothing is
    fetched from the network and nothing is built.
    """

    def _package(self, path: Path, libraries: dict[str, str]) -> Path:
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("h5p.json", json.dumps({"title": "Essai"}))
            archive.writestr("content/content.json", "{}")
            for folder, payload in libraries.items():
                archive.writestr(f"{folder}/library.json", payload)
        return path

    def test_a_package_gives_up_its_libraries(self, tmp_path: Path) -> None:
        prepared = tmp_path / "libraries"
        prepared.mkdir()
        package = self._package(
            tmp_path / "essai.h5p",
            {"H5P.Blanks-1.14": "{}", "H5P.Question-1.5": "{}"},
        )

        report = deploy.merge_libraries(prepared, package)

        assert report.added == ["H5P.Blanks-1.14", "H5P.Question-1.5"]
        assert (prepared / "H5P.Blanks-1.14" / "library.json").is_file()

    def test_every_file_of_a_multi_file_library_survives(self, tmp_path: Path) -> None:
        """The bug this pins: `.exists()` checked live inside the loop found the
        folder the first file of the same library had just created, and skipped
        every entry after it — a real H5P library ships `library.json`,
        `semantics.json` and a `dist/` bundle, not just one file."""
        prepared = tmp_path / "libraries"
        prepared.mkdir()
        with zipfile.ZipFile(tmp_path / "essai.h5p", "w") as archive:
            archive.writestr("h5p.json", json.dumps({"title": "Essai"}))
            archive.writestr("content/content.json", "{}")
            archive.writestr("H5P.Dictation-1.3/library.json", "{}")
            archive.writestr("H5P.Dictation-1.3/semantics.json", "[]")
            archive.writestr("H5P.Dictation-1.3/dist/h5p-dictation.js", "//")

        deploy.merge_libraries(prepared, tmp_path / "essai.h5p")

        assert (prepared / "H5P.Dictation-1.3" / "library.json").is_file()
        assert (prepared / "H5P.Dictation-1.3" / "semantics.json").is_file()
        assert (prepared / "H5P.Dictation-1.3" / "dist" / "h5p-dictation.js").is_file()

    def test_a_second_package_does_not_take_the_first_one_s_libraries_away(
        self, tmp_path: Path
    ) -> None:
        """`deploy_libraries` wipes the tree, which is right for laying it out
        once and would be catastrophic here: importing a second type must not
        remove the first."""
        prepared = tmp_path / "libraries"
        prepared.mkdir()
        deploy.merge_libraries(
            prepared, self._package(tmp_path / "un.h5p", {"H5P.Blanks-1.14": "{}"})
        )

        deploy.merge_libraries(
            prepared, self._package(tmp_path / "deux.h5p", {"H5P.DragText-1.10": "{}"})
        )

        assert (prepared / "H5P.Blanks-1.14").is_dir()
        assert (prepared / "H5P.DragText-1.10").is_dir()

    def test_a_library_already_present_is_left_exactly_as_it_is(
        self, tmp_path: Path
    ) -> None:
        """Two packages often share a dependency, and the first to arrive is the
        one that was vetted with it. Overwriting it would change what an already
        deployed content plays without changing its digest."""
        prepared = tmp_path / "libraries"
        (prepared / "H5P.Question-1.5").mkdir(parents=True)
        (prepared / "H5P.Question-1.5" / "library.json").write_text("vérifiée")
        package = self._package(tmp_path / "essai.h5p", {"H5P.Question-1.5": "autre"})

        report = deploy.merge_libraries(prepared, package)

        assert report.added == []
        assert report.found == ["H5P.Question-1.5"]
        assert (
            prepared / "H5P.Question-1.5" / "library.json"
        ).read_text() == "vérifiée"

    def test_a_content_only_export_is_reported_as_carrying_nothing(
        self, tmp_path: Path
    ) -> None:
        """The trap. h5p.org hands out archives holding nothing but `h5p.json`
        and `content/`; they look like packages and cannot play alone. The
        pilot's own vetted file is one of those. Reporting it as « nothing to
        add » would be indistinguishable from the harmless case."""
        prepared = tmp_path / "libraries"
        prepared.mkdir()
        package = self._package(tmp_path / "seul.h5p", {})

        report = deploy.merge_libraries(prepared, package)

        assert report.found == []
        assert report.added == []

    def test_the_content_folder_is_never_taken_for_a_library(
        self, tmp_path: Path
    ) -> None:
        """`content/` is laid out per content by `deploy_package`, not shared."""
        prepared = tmp_path / "libraries"
        prepared.mkdir()
        package = self._package(tmp_path / "essai.h5p", {"H5P.Blanks-1.14": "{}"})

        deploy.merge_libraries(prepared, package)

        assert not (prepared / "content").exists()

    def test_an_entry_climbing_out_of_the_tree_is_refused(self, tmp_path: Path) -> None:
        prepared = tmp_path / "libraries"
        prepared.mkdir()
        package = tmp_path / "hostile.h5p"
        with zipfile.ZipFile(package, "w") as archive:
            archive.writestr("h5p.json", "{}")
            archive.writestr("H5P.Blanks-1.14/../../dehors.txt", "non")

        with pytest.raises(deploy.DeploymentRefused):
            deploy.merge_libraries(prepared, package)

    def test_a_file_that_is_not_an_archive_is_refused(self, tmp_path: Path) -> None:
        prepared = tmp_path / "libraries"
        prepared.mkdir()
        package = tmp_path / "pas-un-zip.h5p"
        package.write_text("bonjour")

        with pytest.raises(deploy.DeploymentRefused):
            deploy.merge_libraries(prepared, package)
