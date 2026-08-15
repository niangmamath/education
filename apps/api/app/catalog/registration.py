"""Register a vetted H5P package against an activity.

Registration is the only way a package enters the platform. There is no editor
and no upload route, by ADR-006 and ADR-012: a file is inspected, stored in the
private bucket, and recorded, by someone with access to the server.

The order matters. The file is inspected first, so a refused type never reaches
storage; it is stored next; the row is written last, and if that write fails the
object is removed again. An object with no row would be an orphan nobody
inspects a second time.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.catalog.h5p import PackageFacts, inspect_package
from app.catalog.storage import ObjectStore
from app.models.catalog import ACTIVITY_KIND_H5P, Activity, H5PPackage


class RegistrationRefused(Exception):
    """The package cannot be attached to that activity."""


@dataclass
class RegistrationReport:
    activity_code: str
    library: str
    sha256: str
    size_bytes: int
    object_key: str


def register_package(
    session: Session,
    store: ObjectStore,
    activity_code: str,
    path: Path,
    licence: str,
    source: str,
) -> RegistrationReport:
    """Inspect, store, then record. The caller owns the transaction."""
    activity = session.scalars(
        select(Activity).where(Activity.code == activity_code)
    ).one_or_none()
    if activity is None:
        raise RegistrationRefused(
            f"Aucune activité ne porte le code « {activity_code} »."
        )
    if activity.kind != ACTIVITY_KIND_H5P:
        raise RegistrationRefused(
            f"L’activité « {activity_code} » est de type « {activity.kind} » et ne "
            "joue pas de paquet H5P."
        )
    if activity.h5p_package is not None:
        raise RegistrationRefused(
            f"L’activité « {activity_code} » a déjà un paquet. Retirez-le avant "
            "d’en enregistrer un autre."
        )

    facts = inspect_package(path)
    already = session.scalars(
        select(H5PPackage).where(H5PPackage.sha256 == facts.sha256)
    ).one_or_none()
    if already is not None:
        raise RegistrationRefused(
            "Ce fichier est déjà enregistré, à l’empreinte près, pour une autre "
            "activité."
        )

    object_key = _object_key(facts)
    store.put(object_key, facts.path)
    try:
        session.add(
            H5PPackage(
                activity_id=activity.id,
                library_name=facts.library_name,
                library_version=facts.library_version,
                object_key=object_key,
                sha256=facts.sha256,
                size_bytes=facts.size_bytes,
                licence=licence,
                source=source,
            )
        )
        session.flush()
    except Exception:
        # An object with no row is an orphan nobody will inspect again.
        store.remove(object_key)
        raise

    return RegistrationReport(
        activity_code=activity.code,
        library=f"{facts.library_name} {facts.library_version}",
        sha256=facts.sha256,
        size_bytes=facts.size_bytes,
        object_key=object_key,
    )


def _object_key(facts: PackageFacts) -> str:
    """The digest names the object, so the same bytes never sit twice."""
    return f"packages/{facts.sha256}.h5p"
