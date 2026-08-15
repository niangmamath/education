"""Inspect an H5P package before it is ever allowed near the platform.

ADR-012 allows exactly one library for the pilot, `H5P.TrueFalse 1.8`, and
refuses every other type by default until it has been tested and explicitly
decided on. This module is where that refusal happens for a file, before any
byte reaches the bucket and before any row reaches the database.

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

# ADR-012: the only library the pilot admits. The database repeats this rule as
# a check constraint, so the two must be changed together, along with the ADR.
ALLOWED_LIBRARY: Final = ("H5P.TrueFalse", "1.8")

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
    if (name, version) != ALLOWED_LIBRARY:
        allowed = f"{ALLOWED_LIBRARY[0]} {ALLOWED_LIBRARY[1]}"
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
