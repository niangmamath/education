"""What an assignment looks like on the wire.

The Parent view and the Élève view differ on purpose. A parent needs to know
which child an assignment is for and who gave it; a child needs neither — every
row they see is theirs, and saying so on each one would be noise.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.assignment import MAX_NOTE_LENGTH


class AssignmentCreateRequest(BaseModel):
    """What a parent submits to give an activity."""

    model_config = ConfigDict(extra="forbid")

    child_id: uuid.UUID
    activity_code: str = Field(min_length=1, max_length=50)
    note: str | None = Field(default=None, max_length=MAX_NOTE_LENGTH)
    # A date and not a moment: a child's week is counted in days.
    due_on: date | None = None


class AssignedActivity(BaseModel):
    """The activity, as much of it as an assignment needs to show."""

    model_config = ConfigDict(from_attributes=True)

    code: str
    title: str
    kind: str
    duration_minutes: int


class AssignmentPublic(BaseModel):
    """One assignment, as a parent sees it."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    child_id: uuid.UUID
    child_pseudonym: str
    status: str
    note: str | None
    due_on: date | None
    activity: AssignedActivity
    assigned_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    cancelled_at: datetime | None


class ChildAssignmentPublic(BaseModel):
    """One assignment, as the child it belongs to sees it."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: str
    note: str | None
    due_on: date | None
    activity: AssignedActivity
    assigned_at: datetime
    started_at: datetime | None
    completed_at: datetime | None


class ActivityContent(BaseModel):
    """A short-lived way to fetch one package, and what it plays.

    The link is signed and expires. It is not a location a client may keep: the
    bucket is private, by ADR-008, and access to a content follows the
    assignment rather than the content.

    This is not yet the isolated runtime origin ADR-012 asks for. Serving the
    unpacked package under its own domain and CSP is infrastructure, and the
    xAPI endpoint that will capture what happens in it is step 11.
    """

    library_name: str
    library_version: str
    package_url: str
    expires_in: int
