"""Create the activity catalogue.

Three tables: the activities themselves, the competency codes each works on, and
the vetted H5P package an activity of that kind plays.

Two constraints carry decisions rather than mere shapes. The competency link has
**no foreign key** to `ref_competencies`, because a competency row belongs to one
edition of the referential while the catalogue must outlive editions; the link is
the business code, and ADR-013 explains the trade-off. The H5P library check
allows exactly what ADR-012 allows, so that admitting a second type takes a
migration and an amended ADR rather than a configuration change.

Revision ID: 0005_catalog_activities
Revises: 0004_referential_competencies
Create Date: 2026-08-15
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0005_catalog_activities"
down_revision: str | None = "0004_referential_competencies"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "catalog_activities",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("kind", sa.String(length=16), nullable=False),
        sa.Column(
            "status", sa.String(length=16), server_default="draft", nullable=False
        ),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "kind IN ('h5p', 'phet', 'video')", name="ck_catalog_activities_kind"
        ),
        sa.CheckConstraint(
            "status IN ('draft', 'published', 'archived')",
            name="ck_catalog_activities_status",
        ),
        sa.CheckConstraint(
            "duration_minutes BETWEEN 1 AND 60", name="ck_catalog_activities_duration"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code", name="uq_catalog_activities_code"),
    )
    op.create_index(
        "ix_catalog_activities_status", "catalog_activities", ["status"], unique=False
    )

    op.create_table(
        "catalog_activity_competencies",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("activity_id", sa.UUID(), nullable=False),
        sa.Column("competency_code", sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(
            ["activity_id"], ["catalog_activities.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "activity_id", "competency_code", name="uq_catalog_activity_competencies"
        ),
    )
    op.create_index(
        "ix_catalog_activity_competencies_code",
        "catalog_activity_competencies",
        ["competency_code"],
        unique=False,
    )

    op.create_table(
        "catalog_h5p_packages",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("activity_id", sa.UUID(), nullable=False),
        sa.Column("library_name", sa.String(length=100), nullable=False),
        sa.Column("library_version", sa.String(length=20), nullable=False),
        sa.Column("object_key", sa.String(length=500), nullable=False),
        sa.Column("sha256", sa.String(length=64), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("licence", sa.String(length=100), nullable=False),
        sa.Column("source", sa.String(length=500), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "library_name = 'H5P.TrueFalse' AND library_version = '1.8'",
            name="ck_catalog_h5p_packages_allowed_library",
        ),
        sa.CheckConstraint(
            "char_length(sha256) = 64", name="ck_catalog_h5p_packages_digest"
        ),
        sa.CheckConstraint("size_bytes > 0", name="ck_catalog_h5p_packages_size"),
        sa.ForeignKeyConstraint(
            ["activity_id"], ["catalog_activities.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("activity_id", name="uq_catalog_h5p_packages_activity"),
        sa.UniqueConstraint("sha256", name="uq_catalog_h5p_packages_sha256"),
    )


def downgrade() -> None:
    op.drop_table("catalog_h5p_packages")
    op.drop_index(
        "ix_catalog_activity_competencies_code",
        table_name="catalog_activity_competencies",
    )
    op.drop_table("catalog_activity_competencies")
    op.drop_index("ix_catalog_activities_status", table_name="catalog_activities")
    op.drop_table("catalog_activities")
