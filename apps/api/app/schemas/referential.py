"""What the referential looks like on the wire.

Every response carries the edition it was read from. A client that keeps a list
of competencies can therefore tell whether it is still looking at the edition in
force, instead of assuming so.

Business codes are exposed and database identifiers are not: `cm1-math-num-01`
means the same thing from one edition to the next, whereas a UUID is reminted
with every import and would tempt a client to store something transient.
"""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

Item = TypeVar("Item")


class EditionPublic(BaseModel):
    """The edition a response was read from."""

    model_config = ConfigDict(from_attributes=True)

    code: str
    label: str


class LevelPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    label: str
    position: int


class DomainPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    label: str
    position: int


class SubjectPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    label: str
    position: int
    domains: list[DomainPublic] = Field(default_factory=list)


class CompetencyPublic(BaseModel):
    """A competency, named by the codes of its domain and its level.

    Prerequisites are deliberately absent. The tree is modelled since 07.1 and
    belongs to the remediation of step 12; exposing it before anything reads it
    would freeze a shape nobody has needed yet.
    """

    model_config = ConfigDict(from_attributes=True)

    code: str
    label: str
    description: str | None
    position: int
    level: str
    domain: str
    subject: str


class Page(BaseModel, Generic[Item]):
    """One page of a listing, and the edition it came from.

    `edition` is `null` when no edition is in force. That is not an error: the
    referential simply has nothing published yet, and `items` is empty. A client
    can tell that apart from an edition that happens to hold nothing.
    """

    edition: EditionPublic | None
    items: list[Item]
    page: int
    page_size: int
    total: int
