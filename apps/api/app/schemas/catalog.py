"""What the catalogue looks like on the wire.

Business codes are exposed and database identifiers are not, as everywhere else
on this API: a code is what the rest of the platform quotes, and a UUID would
tempt a client to store something it should not.

A package's storage key, digest and provenance stay out of the responses. A
client needs to know that an activity has a package and what type it plays, not
where the file sits: the runtime origin of ADR-012 is what will hand it over,
and no bucket path belongs in a client's hands.
"""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

Item = TypeVar("Item")


class ActivityH5P(BaseModel):
    """What an H5P activity plays, without saying where the file lives."""

    model_config = ConfigDict(from_attributes=True)

    library_name: str
    library_version: str


class ActivityPublic(BaseModel):
    """One activity of the catalogue."""

    model_config = ConfigDict(from_attributes=True)

    code: str
    title: str
    summary: str | None
    kind: str
    duration_minutes: int
    competencies: list[str] = Field(default_factory=list)
    h5p: ActivityH5P | None = None


class CatalogPage(BaseModel, Generic[Item]):
    """One page of the catalogue.

    Unlike a referential listing, no edition is named: the catalogue is not
    versioned, by ADR-013. What the competency codes resolve to does depend on
    the edition in force, and `python -m app.catalog check` is what keeps that
    honest.
    """

    items: list[Item]
    page: int
    page_size: int
    total: int
