"""Create the versioned school referential.

Levels, subjects, domains and competencies all belong to a version, and every
child row repeats its parent's `version_id` inside a composite foreign key. That
is what keeps a version coherent: nothing can point across editions, and the
database is what refuses it rather than the import code.

Revision ID: 0004_referential_competencies
Revises: 0003_family_code_child_status
Create Date: 2026-08-14
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0004_referential_competencies"
down_revision: str | None = "0003_family_code_child_status"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "ref_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("label", sa.String(length=200), nullable=False),
        sa.Column(
            "status", sa.String(length=16), server_default="draft", nullable=False
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "status IN ('draft', 'published', 'archived')",
            name="ck_ref_versions_status",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code", name="uq_ref_versions_code"),
    )
    # Partial index: any number of drafts and archives, never two published.
    op.create_index(
        "uq_ref_versions_single_published",
        "ref_versions",
        ["status"],
        unique=True,
        postgresql_where=sa.text("status = 'published'"),
    )

    op.create_table(
        "ref_levels",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("label", sa.String(length=200), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["version_id"], ["ref_versions.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id", "version_id", name="uq_ref_levels_id_version"),
        sa.UniqueConstraint("version_id", "code", name="uq_ref_levels_version_code"),
    )

    op.create_table(
        "ref_subjects",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("label", sa.String(length=200), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["version_id"], ["ref_versions.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id", "version_id", name="uq_ref_subjects_id_version"),
        sa.UniqueConstraint("version_id", "code", name="uq_ref_subjects_version_code"),
    )

    op.create_table(
        "ref_domains",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("subject_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("label", sa.String(length=200), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["subject_id", "version_id"],
            ["ref_subjects.id", "ref_subjects.version_id"],
            name="fk_ref_domains_subject",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id", "version_id", name="uq_ref_domains_id_version"),
        sa.UniqueConstraint("version_id", "code", name="uq_ref_domains_version_code"),
    )

    op.create_table(
        "ref_competencies",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("domain_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("level_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("label", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["domain_id", "version_id"],
            ["ref_domains.id", "ref_domains.version_id"],
            name="fk_ref_competencies_domain",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["level_id", "version_id"],
            ["ref_levels.id", "ref_levels.version_id"],
            name="fk_ref_competencies_level",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id", "version_id", name="uq_ref_competencies_id_version"),
        sa.UniqueConstraint(
            "version_id", "code", name="uq_ref_competencies_version_code"
        ),
    )

    op.create_table(
        "ref_competency_prerequisites",
        sa.Column("competency_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("prerequisite_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.CheckConstraint(
            "competency_id <> prerequisite_id", name="ck_ref_prerequisites_not_self"
        ),
        sa.ForeignKeyConstraint(
            ["competency_id", "version_id"],
            ["ref_competencies.id", "ref_competencies.version_id"],
            name="fk_ref_prerequisites_competency",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["prerequisite_id", "version_id"],
            ["ref_competencies.id", "ref_competencies.version_id"],
            name="fk_ref_prerequisites_prerequisite",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("competency_id", "prerequisite_id"),
    )


def downgrade() -> None:
    op.drop_table("ref_competency_prerequisites")
    op.drop_table("ref_competencies")
    op.drop_table("ref_domains")
    op.drop_table("ref_subjects")
    op.drop_table("ref_levels")
    op.drop_index(
        "uq_ref_versions_single_published",
        table_name="ref_versions",
        postgresql_where=sa.text("status = 'published'"),
    )
    op.drop_table("ref_versions")
