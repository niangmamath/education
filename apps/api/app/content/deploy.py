"""Lay a vetted package out where the content origin can serve it.

A `.h5p` is an archive, and the player needs individual files it can fetch one
at a time. Deployment is the step between the two, and it is where the archive
is finally opened — after it has been inspected in 08.2, never before.

**This used to write to a disk shared with the content origin.** That worked
on a single machine, where the API and nginx are two processes with the same
filesystem underneath them. It stops working the moment they become two
separate services, because a platform that runs them that way — Render among
others — attaches a persistent disk to exactly one service; the other cannot
see it, whatever is on it. Deployment now puts each file in the private
runtime bucket instead, and the content origin fetches it back through a
signed URL minted per request (`app/api/v1/internal.py`). Nothing about the
ticket that gates a request changes — only where the bytes it unlocks live.

The extraction repeats the path checks the inspection already ran. That is not
distrust of the earlier check but of the interval between them: the archive was
inspected at registration, and what is opened here is read again from storage.
Two cheap checks around a real one is the usual shape of not being sorry.

The libraries are laid out once and shared by every content. They come from a
directory prepared offline, per ADR-012's third condition, and an inventory of
their digests is written beside them: what is being served must be nameable, or
"the libraries we froze" means nothing.

The player bundle is not laid out here any more. It carries no ticket — it is
useless without a content to play — so it ships baked into the content
origin's own image (`infrastructure/nginx/Dockerfile`) instead of the runtime
bucket: one artefact, versioned with the code that builds the image, needing
no signed URL because nothing here would still be secret at that point.
"""

from __future__ import annotations

import hashlib
import json
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from app.catalog.storage import ObjectStore, S3ObjectStore
from app.core.config import settings

CONTENT_ROOT: Final = "content"
LIBRARIES_ROOT: Final = "libraries"
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


def content_store() -> ObjectStore:
    """The bucket the deployed runtime lives in.

    A different bucket from the one packages wait in before they are vetted
    (ADR-008): a package is what an operator has verified, a deployed content
    is what the origin actually serves, and merging the two would let a change
    meant for one silently reach the other.
    """
    return S3ObjectStore(bucket=settings.S3_BUCKET_H5P_RUNTIME)


def deploy_package(store: ObjectStore, package: Path, digest: str) -> DeploymentReport:
    """Open one vetted package under `content/<digest>/`, and nowhere else.

    The digest names the prefix, so redeploying the same bytes is idempotent and
    two different packages can never collide.
    """
    prefix = _content_prefix(digest)

    files = 0
    written = 0
    manifest_seen = False
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
            name = _safe_name(entry.filename)
            if name == "h5p.json":
                manifest_seen = True
            data = archive.read(entry)
            store.put_bytes(f"{prefix}/{name}", data)
            files += 1
            written += len(data)

    if not manifest_seen:
        # An object with no manifest is not a content: taking it back out is
        # cheaper than teaching every reader of the bucket to recognise one.
        store.remove_prefix(f"{prefix}/")
        raise DeploymentRefused("Le paquet déployé ne contient pas de « h5p.json ».")

    return DeploymentReport(
        digest=digest, files=files, bytes_written=written, path=prefix
    )


def deploy_libraries(store: ObjectStore, prepared: Path) -> dict[str, str]:
    """Put the offline-prepared libraries in place and write down what they are.

    Returns the inventory: every file, by its digest. ADR-012 asks for libraries
    frozen as internal artefacts; an artefact nobody can name is not frozen.
    """
    if not prepared.is_dir():
        raise DeploymentRefused(f"« {prepared} » n’est pas un dossier.")

    store.remove_prefix(f"{LIBRARIES_ROOT}/")

    inventory: dict[str, str] = {}
    for path in sorted(prepared.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(prepared).as_posix()
        store.put(f"{LIBRARIES_ROOT}/{relative}", path)
        inventory[relative] = _digest(path)

    store.put_bytes(
        INVENTORY, json.dumps(inventory, indent=2, sort_keys=True).encode("utf-8")
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

    This works on the **local, offline** tree that `deploy_libraries` will later
    upload, not on the runtime bucket itself: preparing a library is something an
    operator does by hand, ahead of a deployment, and touching the live runtime
    for it would let a half-prepared tree reach it.

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
    # Fixed before the loop touches the filesystem: a library usually spans many
    # entries (`library.json`, `semantics.json`, `dist/*.js`...), and the first
    # one written creates the folder this same check reads. Asking `.exists()`
    # live inside the loop found that folder it had just created and skipped
    # every other entry of the very library it was adding — leaving one file
    # behind and nothing to play.
    already_present = {path.name for path in prepared.iterdir() if path.is_dir()}
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
            if library in already_present:
                continue

            added.add(library)
            destination = _safe_local_destination(prepared, entry.filename)
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


def deployed_contents(store: ObjectStore) -> list[str]:
    """Every content digest currently laid out."""
    prefixes = store.list_prefixes(f"{CONTENT_ROOT}/")
    return sorted(
        prefix.removeprefix(f"{CONTENT_ROOT}/").rstrip("/") for prefix in prefixes
    )


def is_deployed(store: ObjectStore, digest: str) -> bool:
    return store.exists(f"{_content_prefix(digest)}/h5p.json")


def _content_prefix(digest: str) -> str:
    if not digest.isalnum() or len(digest) != 64:
        # The digest becomes part of an object key, so it is checked before it
        # is used as one.
        raise DeploymentRefused(f"Empreinte invalide : « {digest} ».")
    return f"{CONTENT_ROOT}/{digest}"


def _safe_name(name: str) -> str:
    """The key suffix an archive entry may be written under, refusing anything
    that would leave its content's prefix.

    A bucket key is a string with no filesystem underneath it to canonicalise —
    there is no symlink to resolve and nothing to `resolve()` against, so what
    protected a real directory (a final check against the target after
    resolution) has no equivalent here. Rejecting a leading slash and any `..`
    or empty segment is the whole of what is needed instead: a key built only
    from segments that are neither of those cannot address anything outside the
    prefix it is joined onto.
    """
    normalized = name.replace("\\", "/")
    if normalized.startswith("/"):
        raise DeploymentRefused(f"Chemin absolu dans l’archive : « {name} ».")
    if any(part in ("", "..") for part in normalized.split("/")):
        raise DeploymentRefused(f"Chemin remontant dans l’archive : « {name} ».")
    return normalized


def _safe_local_destination(target: Path, name: str) -> Path:
    """Where an entry may be written on the local, offline library tree.

    Unlike `_safe_name`, this does land on a real filesystem — `merge_libraries`
    prepares a tree by hand, ahead of any deployment — so the same belt-and-braces
    resolution check as before still applies.
    """
    if name.startswith("/") or Path(name).is_absolute():
        raise DeploymentRefused(f"Chemin absolu dans l’archive : « {name} ».")
    if ".." in Path(name).parts:
        raise DeploymentRefused(f"Chemin remontant dans l’archive : « {name} ».")

    destination = (target / name).resolve()
    if not destination.is_relative_to(target.resolve()):
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
