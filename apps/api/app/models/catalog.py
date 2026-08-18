"""The catalogue of activities a child can be given to do.

An activity is a piece of teaching material — an H5P exercise, a PhET
simulation, a video — together with what it is for: the competencies it works
on, roughly how long it takes, and whether it may be served at all.

The catalogue is **not** versioned the way the referential is. A referential
edition is frozen because traces point at it; a catalogue is editorial work that
should follow the programme in force rather than fork with every re-edition.
That is why an activity names the competencies it works on **by their business
code** and not by their row: `cm1-math-num-01` designates the same competency
from one edition to the next, so the catalogue survives a new edition instead of
being rebuilt with it. See ADR-013.

The price of that choice is that a link is not enforced by a foreign key. A code
that matches nothing is a dangling link, and `python -m app.catalog check` is
what finds them.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Final

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.referential import CODE_LENGTH, LABEL_LENGTH

# What an activity is made of. Only these three exist for the MVP, and each is
# rendered by a player the platform already owns.
ACTIVITY_KIND_H5P: Final = "h5p"
ACTIVITY_KIND_PHET: Final = "phet"
ACTIVITY_KIND_VIDEO: Final = "video"
# Authored here rather than imported: an initiation assessment ties each of its
# questions to a competency of our referential, and no external bank can supply
# a tie that exists nowhere but here.
ACTIVITY_KIND_ASSESSMENT: Final = "assessment"
# A remediation sheet, written here for the same reason and one more: a repair
# owes a **proof**, and a proof that cannot be attributed to the competency it
# repairs proves nothing. It also teaches before it asks, which no imported
# question bank does.
ACTIVITY_KIND_REMEDIATION: Final = "remediation"
ACTIVITY_KINDS: Final = (
    ACTIVITY_KIND_H5P,
    ACTIVITY_KIND_PHET,
    ACTIVITY_KIND_VIDEO,
    ACTIVITY_KIND_ASSESSMENT,
    ACTIVITY_KIND_REMEDIATION,
)

# The kinds this platform writes itself. They share one machinery: questions in
# `authored_questions`, attribution in `catalog_activity_questions`, grading on
# the server. What separates them is policy, not plumbing.
AUTHORED_KINDS: Final = (ACTIVITY_KIND_ASSESSMENT, ACTIVITY_KIND_REMEDIATION)

# An activity is prepared, then may be served, then stops being offered without
# ever disappearing: results of steps 10 to 12 will keep pointing at it.
ACTIVITY_STATUS_DRAFT: Final = "draft"
ACTIVITY_STATUS_PUBLISHED: Final = "published"
ACTIVITY_STATUS_ARCHIVED: Final = "archived"
ACTIVITY_STATUSES: Final = (
    ACTIVITY_STATUS_DRAFT,
    ACTIVITY_STATUS_PUBLISHED,
    ACTIVITY_STATUS_ARCHIVED,
)

# A Quick Repair lasts three to seven minutes, which is a product rule and not a
# guess. Nothing in the catalogue may claim to be shorter than a minute, and an
# activity longer than an hour is a course, not an activity.
MIN_DURATION_MINUTES: Final = 1
MAX_DURATION_MINUTES: Final = 60


class Activity(Base):
    """One thing a child can be asked to do."""

    __tablename__ = "catalog_activities"
    __table_args__ = (
        UniqueConstraint("code", name="uq_catalog_activities_code"),
        CheckConstraint(
            "kind IN ('h5p', 'phet', 'video', 'assessment', 'remediation')",
            name="ck_catalog_activities_kind",
        ),
        CheckConstraint(
            "status IN ('draft', 'published', 'archived')",
            name="ck_catalog_activities_status",
        ),
        CheckConstraint(
            f"duration_minutes BETWEEN {MIN_DURATION_MINUTES} AND {MAX_DURATION_MINUTES}",
            name="ck_catalog_activities_duration",
        ),
        # The reading routes serve published activities and filter on nothing
        # else half as often.
        Index("ix_catalog_activities_status", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    # The stable identifier the rest of the platform quotes. Unlike a
    # referential code, it is unique outright: there is one catalogue.
    code: Mapped[str] = mapped_column(String(CODE_LENGTH), nullable=False)
    title: Mapped[str] = mapped_column(String(LABEL_LENGTH), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    kind: Mapped[str] = mapped_column(String(16), nullable=False)
    status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default=ACTIVITY_STATUS_DRAFT,
        server_default=ACTIVITY_STATUS_DRAFT,
    )
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    # What a remediation sheet teaches before it asks anything, addressed to the
    # child. `summary` is the catalogue's description and is read by adults; this
    # is the sheet's own lesson, and it is the difference between a repair and a
    # second test. Empty for anything the platform did not write.
    guidance: Mapped[str | None] = mapped_column(Text, nullable=True)
    # La classe qu'une activité vise, par le code du niveau.
    #
    # Pour un examen d'entrée, c'est ce qui le désigne : il y en a un par classe
    # et la plateforme doit savoir lequel donner. Pour le reste du catalogue,
    # c'est une indication et rien de plus — une fiche de remédiation vise une
    # compétence, et une compétence porte déjà son niveau.
    #
    # Une chaîne et pas une clé étrangère, pour la raison d'ADR-013 : un niveau
    # appartient à une édition du référentiel, le catalogue lui survit.
    level_code: Mapped[str | None] = mapped_column(String(50), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    competencies: Mapped[list[ActivityCompetency]] = relationship(
        back_populates="activity", cascade="all, delete-orphan", passive_deletes=True
    )
    questions: Mapped[list[ActivityQuestion]] = relationship(
        back_populates="activity", cascade="all, delete-orphan", passive_deletes=True
    )
    h5p_package: Mapped[H5PPackage | None] = relationship(
        back_populates="activity", cascade="all, delete-orphan", passive_deletes=True
    )


class ActivityCompetency(Base):
    """What an activity works on, named by the competency's business code.

    No foreign key points at `ref_competencies`, and that is the decision of
    ADR-013 rather than an omission: a competency row belongs to one edition of
    the referential, so a real reference would have to be rewritten every time an
    edition is published. The code outlives editions, which is exactly the
    property the catalogue needs.
    """

    __tablename__ = "catalog_activity_competencies"
    __table_args__ = (
        UniqueConstraint(
            "activity_id",
            "competency_code",
            name="uq_catalog_activity_competencies",
        ),
        # Step 12 asks the reverse question — which activities repair this
        # competency — far more often than it asks this one.
        Index(
            "ix_catalog_activity_competencies_code",
            "competency_code",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    activity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("catalog_activities.id", ondelete="CASCADE"),
        nullable=False,
    )
    competency_code: Mapped[str] = mapped_column(String(CODE_LENGTH), nullable=False)

    activity: Mapped[Activity] = relationship(back_populates="competencies")


class ActivityQuestion(Base):
    """Which competency a given question of the content works on.

    Optional, and that is the point. Without these rows the platform cannot tell
    which question belongs to which competency — H5P does not say — so a reading
    applies to every competency of the activity, which is coarse but honest.
    With them, each question counts only towards what it actually works on.

    They are declared by whoever registers the activity, because only that
    person knows: nothing in a package states it.
    """

    __tablename__ = "catalog_activity_questions"
    __table_args__ = (
        UniqueConstraint(
            "activity_id",
            "question_ref",
            "competency_code",
            name="uq_catalog_activity_questions",
        ),
        Index("ix_catalog_activity_questions_activity", "activity_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    activity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("catalog_activities.id", ondelete="CASCADE"),
        nullable=False,
    )
    # As the content names it, exactly as in a response.
    question_ref: Mapped[str] = mapped_column(String(200), nullable=False)
    competency_code: Mapped[str] = mapped_column(String(CODE_LENGTH), nullable=False)

    activity: Mapped[Activity] = relationship(back_populates="questions")


class H5PPackage(Base):
    """The vetted H5P file an activity of kind `h5p` plays.

    ADR-012 refuses every type by default and admits only those decided on. That
    refusal is a check constraint rather than an application rule: adding a type
    requires a migration and an amended ADR, which is the deliberate friction the
    decision asked for.

    The version is **not** constrained. Freezing is done by the digest, which is
    what actually says "these are the bytes that were vetted"; two builds of one
    version are not the same file, and a version string cannot tell them apart.

    The digest and the size are recorded because a package is vetted once and
    served many times; anything that no longer matches its digest is no longer
    the file that was vetted.
    """

    __tablename__ = "catalog_h5p_packages"
    __table_args__ = (
        UniqueConstraint("activity_id", name="uq_catalog_h5p_packages_activity"),
        UniqueConstraint("sha256", name="uq_catalog_h5p_packages_sha256"),
        CheckConstraint(
            "library_name IN ("
            "'H5P.TrueFalse', 'H5P.MultiChoice', 'H5P.SingleChoiceSet', "
            "'H5P.Blanks', 'H5P.MarkTheWords', 'H5P.DragText', "
            "'H5P.DragQuestion', 'H5P.Dictation')",
            name="ck_catalog_h5p_packages_allowed_library",
        ),
        CheckConstraint("size_bytes > 0", name="ck_catalog_h5p_packages_size"),
        CheckConstraint(
            "char_length(sha256) = 64", name="ck_catalog_h5p_packages_digest"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    activity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("catalog_activities.id", ondelete="CASCADE"),
        nullable=False,
    )
    library_name: Mapped[str] = mapped_column(String(100), nullable=False)
    library_version: Mapped[str] = mapped_column(String(20), nullable=False)
    # Where the file sits in the private bucket. Never served directly: the
    # runtime origin is isolated, per ADR-012.
    object_key: Mapped[str] = mapped_column(String(500), nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    # ADR-012, condition 8: licence and provenance checked before publication.
    licence: Mapped[str] = mapped_column(String(100), nullable=False)
    source: Mapped[str] = mapped_column(String(500), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    activity: Mapped[Activity] = relationship(back_populates="h5p_package")


class AuthoredQuestion(Base):
    """One question of an activity this platform wrote itself.

    It serves both authored kinds — the initiation assessment and the
    remediation sheets — because they ask a question the same way and differ only
    in what surrounds it. Two tables holding the same four columns would drift,
    and the grading code would have to learn which one to look in.

    The wording lives here; the attribution — which competency the question works
    on — stays in `catalog_activity_questions`, where it already was. Splitting
    them is deliberate: the engine that reads a result must go on reading one
    table for attribution, whether the activity was imported or written here, and
    it must never learn the difference.

    `correct_index` is what a client is never given. The question travels to the
    browser without it, the answer comes back as an index, and the server is what
    compares. An assessment whose answers ship with it is a questionnaire.

    `explanation` is what a child is told **after** she has answered, and it is
    what makes a remediation sheet a repair rather than a second test. The
    assessment leaves it empty on purpose: telling a child the answer to a
    question that is measuring her would corrupt the very reading being taken.
    """

    __tablename__ = "authored_questions"
    __table_args__ = (
        UniqueConstraint(
            "activity_id", "question_ref", name="uq_authored_questions_ref"
        ),
        CheckConstraint("correct_index >= 0", name="ck_authored_questions_correct"),
        CheckConstraint(
            "jsonb_array_length(choices) >= 2", name="ck_authored_questions_choices"
        ),
        Index("ix_authored_questions_activity", "activity_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    activity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("catalog_activities.id", ondelete="CASCADE"),
        nullable=False,
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    # The same identifier the responses carry, so a reading joins to its wording
    # without inventing a second convention.
    question_ref: Mapped[str] = mapped_column(String(200), nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    choices: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    correct_index: Mapped[int] = mapped_column(Integer, nullable=False)
    # Said once the answer is in, never before.
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)

    activity: Mapped[Activity] = relationship()
