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
