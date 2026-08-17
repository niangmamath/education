"""Inspect an H5P package before it is ever allowed near the platform.

ADR-012 refuses every content type by default and admits only those that have
been tested and explicitly decided on. This module is where that refusal happens
for a file, before any byte reaches the bucket and before any row reaches the
database.

The pilot admitted exactly one type, `H5P.TrueFalse 1.8`. The amendment of 17
August 2026 widens the list to eight, because one type cannot carry a subject:
a dictation needs to be heard, an ordering needs to be dragged, and a
true-or-false question can express neither.

An `.h5p` file is a zip archive, and a zip archive is an untrusted input. The
inspection therefore reads entries without extracting them: nothing is written
to disk, so a crafted entry name cannot escape anywhere. The checks below are
deliberately dull — a size ceiling, an entry-count ceiling, a refusal of
absolute and climbing paths, a refusal of anything that is not a plain file —
because dull checks are the ones that hold.

The digest is computed from the bytes actually read, so what is recorded is what
was inspected, not what a filename claimed.
"""

from __future__ import annotations

import hashlib
import json
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Final

# ADR-012, amended: the libraries this platform admits. The database repeats this
# list as a check constraint, so the two must be changed together, along with the
# ADR — that friction is the decision, not an inconvenience.
#
# Each one is here because it does something the others cannot, and because one
# package answers for **one** competency: a single content, a single score, a
# single reading. `H5P.QuestionSet` is deliberately absent for that reason — it
# bundles several questions under one activity, and attributing each of them
# would mean reading sub-content identifiers out of the archive by hand. It can
# be added, but not for free, and not by accident.
#
# `H5P.Dictation` is the one that pays a real debt: everything else this
# platform can ask, it can already ask in a sheet it wrote itself. Hearing a
# sound is the one thing it cannot, and phonology without sound is a pis-aller
# we have written down as one since the initiation assessment.
ALLOWED_LIBRARIES: Final[frozenset[str]] = frozenset(
    {
        "H5P.TrueFalse",
        "H5P.MultiChoice",
        "H5P.SingleChoiceSet",
        "H5P.Blanks",
        "H5P.MarkTheWords",
        "H5P.DragText",
        "H5P.DragQuestion",
        "H5P.Dictation",
    }
)

# The version is recorded rather than pinned in code. Freezing is done by the
# digest, which is what actually says "this is the file that was vetted": two
# builds of the same library version are not the same bytes, and the digest
# knows it while a version string does not. Pinning versions here would only
# refuse a file for being newer than a constant nobody remembered to raise.

MAX_PACKAGE_BYTES: Final = 20 * 1024 * 1024
MAX_ENTRIES: Final = 500
# A zip that unpacks to far more than it weighs is a decompression bomb, whether
# or not anyone intended it.
MAX_EXPANSION_RATIO: Final = 100

MANIFEST: Final = "h5p.json"


class PackageRefused(Exception):
    """The file is not a package this platform will accept."""


@dataclass(frozen=True)
class PackageFacts:
    """What inspection established about a file, and nothing it merely claims."""

    path: Path
    library_name: str
    library_version: str
    sha256: str
    size_bytes: int
    title: str
    declared_licence: str


def inspect_package(path: Path) -> PackageFacts:
    """Read the package and establish what it is, or refuse it.

    Every refusal is a `PackageRefused` naming what was wrong, because the
    person running the command is the one who has to fix the file.
    """
    if not path.is_file():
        raise PackageRefused(f"« {path} » n’est pas un fichier.")

    size = path.stat().st_size
    if size == 0:
        raise PackageRefused("Le fichier est vide.")
    if size > MAX_PACKAGE_BYTES:
        raise PackageRefused(
            f"Le fichier pèse {size} octets, au-delà du plafond de "
            f"{MAX_PACKAGE_BYTES} octets."
        )

    digest = _digest(path)

    if not zipfile.is_zipfile(path):
        raise PackageRefused(
            "Le fichier n’est pas une archive zip ; un .h5p en est une."
        )

    with zipfile.ZipFile(path) as archive:
        _refuse_hostile_archive(archive, size)
        manifest = _read_manifest(archive)

    name, version = _library_of(manifest)
    if name not in ALLOWED_LIBRARIES:
        allowed = ", ".join(sorted(ALLOWED_LIBRARIES))
        raise PackageRefused(
            f"Type H5P « {name} {version} » refusé. ADR-012 n’autorise que "
            f"{allowed} ; tout autre type demande un test et une décision "
            "explicites, puis une migration."
        )

    return PackageFacts(
        path=path,
        library_name=name,
        library_version=version,
        sha256=digest,
        size_bytes=size,
        title=str(manifest.get("title") or path.stem),
        declared_licence=str(manifest.get("license") or "U"),
    )


def _digest(path: Path) -> str:
    """The SHA-256 of the bytes on disk, read in chunks rather than at once."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _refuse_hostile_archive(archive: zipfile.ZipFile, packed_size: int) -> None:
    """Refuse the shapes of archive that exist to do harm."""
    entries = archive.infolist()
    if len(entries) > MAX_ENTRIES:
        raise PackageRefused(
            f"L’archive contient {len(entries)} entrées, au-delà du plafond de "
            f"{MAX_ENTRIES}."
        )

    unpacked = 0
    for entry in entries:
        name = entry.filename
        if name.startswith("/") or Path(name).is_absolute():
            raise PackageRefused(f"Chemin absolu dans l’archive : « {name} ».")
        if ".." in Path(name).parts:
            raise PackageRefused(f"Chemin remontant dans l’archive : « {name} ».")
        # Symlinks and devices are stored in the upper half of the mode; a
        # package has no business carrying either.
        if entry.create_system == 3 and (entry.external_attr >> 16) & 0o170000 not in (
            0o100000,
            0o040000,
            0,
        ):
            raise PackageRefused(
                f"Entrée qui n’est pas un fichier simple : « {name} »."
            )
        unpacked += entry.file_size

    if unpacked > packed_size * MAX_EXPANSION_RATIO:
        raise PackageRefused(
            f"L’archive se déploie en {unpacked} octets pour {packed_size} "
            "compressés, ce qui est le profil d’une bombe de décompression."
        )


def _read_manifest(archive: zipfile.ZipFile) -> dict[str, object]:
    try:
        raw = archive.read(MANIFEST)
    except KeyError:
        raise PackageRefused(f"L’archive ne contient pas de « {MANIFEST} ».") from None

    try:
        manifest = json.loads(raw)
    except json.JSONDecodeError as error:
        raise PackageRefused(
            f"« {MANIFEST} » n’est pas un JSON valide : {error}"
        ) from None

    if not isinstance(manifest, dict):
        raise PackageRefused(f"« {MANIFEST} » ne décrit pas un objet.")
    return manifest


def _library_of(manifest: dict[str, object]) -> tuple[str, str]:
    """The main library and its version, as the manifest declares them.

    A package names its main library, then repeats it among its dependencies
    with the version. Both must agree, or the file does not say what it plays.
    """
    main = manifest.get("mainLibrary")
    if not isinstance(main, str) or not main:
        raise PackageRefused(f"« {MANIFEST} » ne nomme pas de « mainLibrary ».")

    dependencies = manifest.get("preloadedDependencies")
    if not isinstance(dependencies, list):
        raise PackageRefused(
            f"« {MANIFEST} » ne liste pas de « preloadedDependencies »."
        )

    for dependency in dependencies:
        if not isinstance(dependency, dict):
            continue
        if dependency.get("machineName") != main:
            continue
        major = dependency.get("majorVersion")
        minor = dependency.get("minorVersion")
        if major is None or minor is None:
            raise PackageRefused(
                f"La bibliothèque « {main} » est déclarée sans version."
            )
        return main, f"{major}.{minor}"

    raise PackageRefused(
        f"La bibliothèque principale « {main} » ne figure pas dans les dépendances, "
        "donc sa version est inconnue."
    )
