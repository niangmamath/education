"""What the platform refuses to accept as an H5P package.

ADR-012 admits one library and refuses everything else by default. A package is
also an untrusted zip, so the inspection is tested against the shapes of archive
that exist to do harm: paths that climb out, paths that start at the root,
archives that unpack to far more than they weigh.

Every archive here is built in the test itself. The pilot package validated by
the spike of step 04 lives in `experiments/`, outside the tree the API container
mounts; it is exercised by hand through the command, and the report of 08.2
records the result. A test that could only run in one of the two places would be
worse than none.
"""

from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path
from typing import Any

import pytest

from app.catalog.h5p import (
    ALLOWED_LIBRARIES,
    MAX_ENTRIES,
    MAX_PACKAGE_BYTES,
    PackageRefused,
    inspect_package,
)


def manifest(
    library: str = "H5P.TrueFalse", major: str = "1", minor: str = "8", **extra: Any
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "title": "Question d’essai",
        "language": "fr",
        "mainLibrary": library,
        "embedTypes": ["iframe"],
        "license": "U",
        "preloadedDependencies": [
            {"machineName": library, "majorVersion": major, "minorVersion": minor}
        ],
    }
    payload.update(extra)
    return payload


def write_package(
    path: Path,
    manifest_payload: dict[str, Any] | str | None = None,
    entries: dict[str, bytes] | None = None,
) -> Path:
    """Build a `.h5p`, valid or deliberately not.

    Deflated rather than stored, because a real package is compressed and a
    decompression bomb only exists as compressed bytes.
    """
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        if manifest_payload is not None:
            raw = (
                manifest_payload
                if isinstance(manifest_payload, str)
                else json.dumps(manifest_payload)
            )
            archive.writestr("h5p.json", raw)
        archive.writestr("content/content.json", json.dumps({"correct": "true"}))
        for name, body in (entries or {}).items():
            archive.writestr(name, body)
    return path


class TestAllowedLibrary:
    def test_the_pilot_library_passes(self, tmp_path: Path) -> None:
        package = write_package(tmp_path / "ok.h5p", manifest())

        facts = inspect_package(package)

        assert facts.library_name in ALLOWED_LIBRARIES
        assert facts.library_version == "1.8"

    @pytest.mark.parametrize(
        "library",
        [
            # Bundles several questions under one activity; attributing each of
            # them means reading sub-content identifiers by hand, which is work
            # nobody has done. It can be added, but not by accident.
            "H5P.QuestionSet",
            # Times the child. This platform does not time a six-year-old.
            "H5P.ArithmeticQuiz",
            "H5P.InteractiveVideo",
            "H5P.Column",
            "H5P.Accordion",
        ],
    )
    def test_a_type_outside_the_list_is_refused(
        self, tmp_path: Path, library: str
    ) -> None:
        """The refusal is by default, so a new type is a decision, not a surprise."""
        package = write_package(tmp_path / "autre.h5p", manifest(library=library))

        with pytest.raises(PackageRefused) as refusal:
            inspect_package(package)

        assert "ADR-012" in str(refusal.value)

    @pytest.mark.parametrize("library", sorted(ALLOWED_LIBRARIES))
    def test_every_admitted_type_is_accepted(
        self, tmp_path: Path, library: str
    ) -> None:
        """The eight of the amended ADR-012, each because it does something the
        others cannot express."""
        package = write_package(tmp_path / "admis.h5p", manifest(library=library))

        assert inspect_package(package).library_name == library

    @pytest.mark.parametrize(("major", "minor"), [("1", "7"), ("1", "8"), ("2", "0")])
    def test_the_version_is_recorded_rather_than_pinned(
        self, tmp_path: Path, major: str, minor: str
    ) -> None:
        """Freezing is done by the digest, which says « these are the bytes that
        were vetted » — something a version string cannot say, since two builds
        of one version are not the same file. Pinning versions here would only
        refuse a package for being newer than a constant nobody raised."""
        package = write_package(
            tmp_path / "version.h5p", manifest(major=major, minor=minor)
        )

        assert inspect_package(package).library_version == f"{major}.{minor}"

    def test_a_package_that_hides_its_version_is_refused(self, tmp_path: Path) -> None:
        payload = manifest()
        payload["preloadedDependencies"] = [{"machineName": "H5P.TrueFalse"}]
        package = write_package(tmp_path / "sans-version.h5p", payload)

        with pytest.raises(PackageRefused):
            inspect_package(package)

    def test_a_main_library_absent_from_the_dependencies_is_refused(
        self, tmp_path: Path
    ) -> None:
        payload = manifest()
        payload["mainLibrary"] = "H5P.Autre"
        package = write_package(tmp_path / "incoherent.h5p", payload)

        with pytest.raises(PackageRefused):
            inspect_package(package)


class TestHostileArchives:
    def test_a_path_climbing_out_of_the_archive_is_refused(
        self, tmp_path: Path
    ) -> None:
        """Zip slip: the entry name is the attack, and nothing is extracted."""
        package = write_package(
            tmp_path / "slip.h5p", manifest(), {"../../etc/passwd": b"x"}
        )

        with pytest.raises(PackageRefused) as refusal:
            inspect_package(package)

        assert "remontant" in str(refusal.value)

    def test_an_absolute_path_is_refused(self, tmp_path: Path) -> None:
        package = write_package(
            tmp_path / "absolu.h5p", manifest(), {"/etc/shadow": b"x"}
        )

        with pytest.raises(PackageRefused) as refusal:
            inspect_package(package)

        assert "absolu" in str(refusal.value)

    def test_an_archive_of_too_many_entries_is_refused(self, tmp_path: Path) -> None:
        entries = {f"content/f{index}.txt": b"x" for index in range(MAX_ENTRIES + 1)}
        package = write_package(tmp_path / "nombreux.h5p", manifest(), entries)

        with pytest.raises(PackageRefused) as refusal:
            inspect_package(package)

        assert "entrées" in str(refusal.value)

    def test_a_decompression_bomb_is_refused(self, tmp_path: Path) -> None:
        """Compresses to nothing, unpacks to a great deal. Intent is irrelevant."""
        package = write_package(
            tmp_path / "bombe.h5p", manifest(), {"content/gros.bin": b"\0" * 5_000_000}
        )

        with pytest.raises(PackageRefused) as refusal:
            inspect_package(package)

        assert "décompression" in str(refusal.value)


class TestMalformedFiles:
    def test_a_file_that_is_not_a_zip_is_refused(self, tmp_path: Path) -> None:
        package = tmp_path / "faux.h5p"
        package.write_bytes(b"ceci n'est pas une archive")

        with pytest.raises(PackageRefused) as refusal:
            inspect_package(package)

        assert "zip" in str(refusal.value)

    def test_an_empty_file_is_refused(self, tmp_path: Path) -> None:
        package = tmp_path / "vide.h5p"
        package.write_bytes(b"")

        with pytest.raises(PackageRefused):
            inspect_package(package)

    def test_a_missing_file_is_refused(self, tmp_path: Path) -> None:
        with pytest.raises(PackageRefused):
            inspect_package(tmp_path / "absent.h5p")

    def test_an_archive_without_a_manifest_is_refused(self, tmp_path: Path) -> None:
        package = write_package(tmp_path / "sans-manifeste.h5p", None)

        with pytest.raises(PackageRefused) as refusal:
            inspect_package(package)

        assert "h5p.json" in str(refusal.value)

    def test_a_manifest_that_is_not_json_is_refused(self, tmp_path: Path) -> None:
        package = write_package(tmp_path / "casse.h5p", "{ceci n'est pas du json")

        with pytest.raises(PackageRefused) as refusal:
            inspect_package(package)

        assert "JSON" in str(refusal.value)

    def test_a_manifest_that_is_not_an_object_is_refused(self, tmp_path: Path) -> None:
        package = write_package(tmp_path / "liste.h5p", "[]")

        with pytest.raises(PackageRefused):
            inspect_package(package)

    def test_a_file_beyond_the_size_ceiling_is_refused(self, tmp_path: Path) -> None:
        package = tmp_path / "enorme.h5p"
        package.write_bytes(b"\0" * (MAX_PACKAGE_BYTES + 1))

        with pytest.raises(PackageRefused) as refusal:
            inspect_package(package)

        assert "plafond" in str(refusal.value)


class TestDigest:
    def test_the_digest_is_of_the_bytes_and_not_of_the_name(
        self, tmp_path: Path
    ) -> None:
        """Same bytes under two names are one package."""
        payload = io.BytesIO()
        with zipfile.ZipFile(payload, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("h5p.json", json.dumps(manifest()))
        raw = payload.getvalue()

        first = tmp_path / "un.h5p"
        second = tmp_path / "deux.h5p"
        first.write_bytes(raw)
        second.write_bytes(raw)

        assert inspect_package(first).sha256 == inspect_package(second).sha256
