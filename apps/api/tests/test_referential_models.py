"""Static contract tests for the school referential models."""

from sqlalchemy import CheckConstraint, ForeignKeyConstraint, UniqueConstraint, inspect

from app.core.db import Base
from app.models import Competency, CompetencyPrerequisite, Domain, Level, Subject
from app.models.referential import ReferentialVersion

VERSIONED_TABLES = (
    "ref_levels",
    "ref_subjects",
    "ref_domains",
    "ref_competencies",
)


def test_referential_tables_are_registered_in_base_metadata() -> None:
    for table in ("ref_versions", *VERSIONED_TABLES, "ref_competency_prerequisites"):
        assert table in Base.metadata.tables


def test_every_referential_row_belongs_to_a_version() -> None:
    """A row without a version would belong to no edition of the referential."""
    for model in (Level, Subject, Domain, Competency, CompetencyPrerequisite):
        assert inspect(model).columns["version_id"].nullable is False


def test_a_code_is_unique_inside_its_version_and_not_beyond() -> None:
    """Two editions may name the same competency; one edition may not, twice."""
    for table_name in VERSIONED_TABLES:
        table = Base.metadata.tables[table_name]
        scoped = [
            [column.name for column in constraint.columns]
            for constraint in table.constraints
            if isinstance(constraint, UniqueConstraint)
        ]
        assert ["version_id", "code"] in scoped
        assert ["code"] not in scoped


def test_each_versioned_table_can_be_referenced_with_its_version() -> None:
    """The `(id, version_id)` key is what composite foreign keys point at."""
    for table_name in VERSIONED_TABLES:
        table = Base.metadata.tables[table_name]
        keys = [
            [column.name for column in constraint.columns]
            for constraint in table.constraints
            if isinstance(constraint, UniqueConstraint)
        ]
        assert ["id", "version_id"] in keys


def test_children_reference_their_parent_together_with_the_version() -> None:
    """A single-column reference would let a row point across editions."""
    expected = {
        "ref_domains": {("subject_id", "version_id")},
        "ref_competencies": {("domain_id", "version_id"), ("level_id", "version_id")},
        "ref_competency_prerequisites": {
            ("competency_id", "version_id"),
            ("prerequisite_id", "version_id"),
        },
    }
    for table_name, awaited in expected.items():
        table = Base.metadata.tables[table_name]
        composite = {
            tuple(element.parent.name for element in constraint.elements)
            for constraint in table.constraints
            if isinstance(constraint, ForeignKeyConstraint)
            and len(constraint.elements) > 1
        }
        assert composite == awaited


def test_deleting_a_version_takes_its_content_with_it() -> None:
    for table_name in (*VERSIONED_TABLES, "ref_competency_prerequisites"):
        table = Base.metadata.tables[table_name]
        for constraint in table.foreign_key_constraints:
            assert constraint.ondelete == "CASCADE"


def test_a_competency_cannot_be_its_own_prerequisite() -> None:
    table = CompetencyPrerequisite.__table__
    checks = {
        constraint.name
        for constraint in table.constraints
        if isinstance(constraint, CheckConstraint)
    }
    assert "ck_ref_prerequisites_not_self" in checks


def test_a_prerequisite_pair_cannot_be_declared_twice() -> None:
    primary_key = [
        column.name for column in CompetencyPrerequisite.__table__.primary_key
    ]
    assert primary_key == ["competency_id", "prerequisite_id"]


def test_only_one_version_may_be_published() -> None:
    """A partial index, so drafts and archives stay as numerous as needed."""
    indexes = {index.name: index for index in ReferentialVersion.__table__.indexes}
    published = indexes["uq_ref_versions_single_published"]

    assert published.unique is True
    assert "published" in str(published.dialect_options["postgresql"]["where"])


def test_the_version_status_is_closed_to_three_values() -> None:
    checks = {
        constraint.name
        for constraint in ReferentialVersion.__table__.constraints
        if isinstance(constraint, CheckConstraint)
    }
    assert "ck_ref_versions_status" in checks
