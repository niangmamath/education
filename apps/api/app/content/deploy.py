"""Lay a vetted package out where the content origin can serve it.

A `.h5p` is an archive, and the player needs a folder. Deployment is the step
between the two, and it is where the archive is finally opened — after it has
been inspected in 08.2, never before.

The extraction repeats the path checks the inspection already ran. That is not
distrust of the earlier check but of the interval between them: the archive was
inspected at registration, and what is opened here is read again from storage.
Two cheap checks around a real one is the usual shape of not being sorry.

The libraries are laid out once and shared by every content. They come from a
directory prepared offline, per ADR-012's third condition, and an inventory of
their digests is written beside them: what is being served must be nameable, or
"the libraries we froze" means nothing.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Final

CONTENT_ROOT: Final = "content"
LIBRARIES_ROOT: Final = "libraries"
PLAYER_ROOT: Final = "player"
INVENTORY: Final = "inventory.json"

# The same ceilings as the inspection of 08.2, repeated here on purpose.
MAX_ENTRIES: Final = 500
MAX_UNPACKED_BYTES: Final = 200 * 1024 * 1024


class DeploymentRefused(Exception):
    """The content cannot be laid out for serving."""


@dataclass
class DeploymentReport:
    digest: str
    files: int
    bytes_written: int
    path: str


def deploy_package(runtime_root: Path, package: Path, digest: str) -> DeploymentReport:
    """Open one vetted package under `content/<digest>/`, and nowhere else.

    The digest names the folder, so redeploying the same bytes is idempotent and
    two different packages can never collide.
    """
    target = _content_path(runtime_root, digest)
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)

    files = 0
    written = 0
    with zipfile.ZipFile(package) as archive:
        entries = archive.infolist()
        if len(entries) > MAX_ENTRIES:
            raise DeploymentRefused(
                f"L’archive contient {len(entries)} entrées, au-delà du plafond."
            )
        if sum(entry.file_size for entry in entries) > MAX_UNPACKED_BYTES:
            raise DeploymentRefused(
                "L’archive se déploie au-delà du plafond de taille."
            )

        for entry in entries:
            if entry.is_dir():
                continue
            destination = _safe_destination(target, entry.filename)
            destination.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(entry) as source, destination.open("wb") as handle:
                written += _copy(source, handle)
            files += 1

    if not (target / "h5p.json").is_file():
        shutil.rmtree(target)
        raise DeploymentRefused("Le paquet déployé ne contient pas de « h5p.json ».")

    return DeploymentReport(
        digest=digest,
        files=files,
        bytes_written=written,
        path=f"{CONTENT_ROOT}/{digest}",
    )


def deploy_libraries(runtime_root: Path, prepared: Path) -> dict[str, str]:
    """Put the offline-prepared libraries in place and write down what they are.

    Returns the inventory: every file, by its digest. ADR-012 asks for libraries
    frozen as internal artefacts; an artefact nobody can name is not frozen.
    """
    if not prepared.is_dir():
        raise DeploymentRefused(f"« {prepared} » n’est pas un dossier.")

    target = runtime_root / LIBRARIES_ROOT
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(prepared, target)

    inventory = {
        str(path.relative_to(target)): _digest(path)
        for path in sorted(target.rglob("*"))
        if path.is_file()
    }
    (runtime_root / INVENTORY).write_text(
        json.dumps(inventory, indent=2, sort_keys=True), encoding="utf-8"
    )
    return inventory


@dataclass(frozen=True)
class LibraryImport:
    """What a package turned out to carry, and what of it was new.

    The two numbers must not be confused, and the difference is the whole reason
    this returns a pair. `found` empty means the archive is a **content-only
    export**: it will not play unless its libraries are already in the tree, and
    the operator has to go back and download the full package. `found` non-empty
    with `added` empty means everything it carries was already there, which is
    the ordinary and harmless case.
    """

    found: list[str]
    added: list[str]


def merge_libraries(prepared: Path, package: Path) -> LibraryImport:
    """Add a package's own libraries to the prepared tree, without replacing it.

    An `.h5p` archive carries its libraries beside its content — one folder per
    library, named `H5P.Blanks-1.14` and so on — which is exactly what the player
    needs and exactly what the shared tree is missing when a new type arrives.
    Pulling them out of the file the operator downloaded is therefore the whole
    of "preparing a library offline": there is nothing to fetch from the network,
    and nothing to build.

    **Merged, never replaced.** `deploy_libraries` wipes the tree and copies a
    prepared folder over it, which is right for laying the whole thing out at
    once and wrong here: importing a second package must not take the first
    one's libraries away with it.

    A library already present is left exactly as it is, and its name is not
    returned. Two packages often share a dependency, and the first one to arrive
    is the one that was vetted with it — replacing it silently would change what
    a deployed content plays without changing its digest.

    Beware the content-only export: h5p.org will hand you an archive holding
    nothing but `h5p.json` and `content/`, which looks like a package and cannot
    play on its own. The pilot's own vetted file is one of those, which is why
    its libraries had to be prepared by hand. The report says so rather than
    reporting "nothing to add", because the two look identical from here and mean
    opposite things.
    """
    if not prepared.is_dir():
        raise DeploymentRefused(f"« {prepared} » n’est pas un dossier.")
    if not zipfile.is_zipfile(package):
        raise DeploymentRefused(f"« {package} » n’est pas une archive .h5p.")

    found: set[str] = set()
    added: set[str] = set()
    with zipfile.ZipFile(package) as archive:
        entries = archive.infolist()
        if len(entries) > MAX_ENTRIES:
            raise DeploymentRefused(
                f"L’archive contient {len(entries)} entrées, au-delà du plafond."
            )
        if sum(entry.file_size for entry in entries) > MAX_UNPACKED_BYTES:
            raise DeploymentRefused(
                "L’archive se déploie au-delà du plafond de taille."
            )

        for entry in entries:
            if entry.is_dir():
                continue
            library = _library_folder_of(entry.filename)
            if library is None:
                continue
            found.add(library)
            if (prepared / library).exists():
                continue

            added.add(library)
            destination = _safe_destination(prepared, entry.filename)
            destination.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(entry) as source, destination.open("wb") as handle:
                _copy(source, handle)

    return LibraryImport(found=sorted(found), added=sorted(added))


def _library_folder_of(name: str) -> str | None:
    """The library folder an archive entry belongs to, if it belongs to one.

    A library folder is named `Machine.Name-major.minor`. The archive's other
    top-level entries — `h5p.json`, `content/` — are not libraries and are laid
    out by `deploy_package` instead, per content.
    """
    head, separator, _ = name.replace("\\", "/").partition("/")
    if not separator or head in {"content", ".."} or head.startswith("."):
        return None
    stem, dash, version = head.rpartition("-")
    if not dash or not stem or not version[:1].isdigit():
        return None
    return head


def deploy_player(runtime_root: Path, prepared: Path) -> int:
    """Put the player bundle and our page in place.

    The bundle is an external artefact prepared offline, like the libraries. The
    page beside it is ours, versioned with the code, because it is the only part
    of this origin that we wrote and the only one that decides what leaves it.
    """
    if not prepared.is_dir():
        raise DeploymentRefused(f"« {prepared} » n’est pas un dossier.")

    target = runtime_root / PLAYER_ROOT
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(prepared, target)

    page = Path(__file__).resolve().parent / "page" / "play.html"
    shutil.copy2(page, target / "play.html")
    return sum(1 for path in target.rglob("*") if path.is_file())


def deployed_contents(runtime_root: Path) -> list[str]:
    """Every content digest currently laid out."""
    root = runtime_root / CONTENT_ROOT
    if not root.is_dir():
        return []
    return sorted(path.name for path in root.iterdir() if path.is_dir())


def is_deployed(runtime_root: Path, digest: str) -> bool:
    return (_content_path(runtime_root, digest) / "h5p.json").is_file()


def _content_path(runtime_root: Path, digest: str) -> Path:
    if not digest.isalnum() or len(digest) != 64:
        # The digest becomes a directory name, so it is checked before it is one.
        raise DeploymentRefused(f"Empreinte invalide : « {digest} ».")
    return runtime_root / CONTENT_ROOT / digest


def _safe_destination(target: Path, name: str) -> Path:
    """Where an entry may be written, refusing anything that leaves the folder."""
    if name.startswith("/") or Path(name).is_absolute():
        raise DeploymentRefused(f"Chemin absolu dans l’archive : « {name} ».")
    if ".." in Path(name).parts:
        raise DeploymentRefused(f"Chemin remontant dans l’archive : « {name} ».")

    destination = (target / name).resolve()
    if not destination.is_relative_to(target.resolve()):
        # Belt and braces: whatever the name looked like, this is where it lands.
        raise DeploymentRefused(f"Entrée sortant du dossier cible : « {name} ».")
    return destination


def _copy(source: object, handle: object) -> int:
    written = 0
    while True:
        block = source.read(1024 * 1024)  # type: ignore[attr-defined]
        if not block:
            return written
        handle.write(block)  # type: ignore[attr-defined]
        written += len(block)


def _digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()
