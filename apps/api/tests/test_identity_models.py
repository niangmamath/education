"""Static contract tests for identity and family SQLAlchemy models."""

from sqlalchemy import UniqueConstraint, inspect

from app.core.db import Base
from app.models import Child, Parent


def test_identity_tables_are_registered_in_base_metadata() -> None:
    assert "auth_parents" in Base.metadata.tables
    assert "auth_children" in Base.metadata.tables


def test_parent_contract() -> None:
    mapper = inspect(Parent)
    columns = mapper.columns
    assert columns["email"].nullable is False
    assert columns["password_hash"].nullable is False
    assert columns["display_name"].nullable is False
    assert "children" in mapper.relationships


def test_child_contract_and_family_relationship() -> None:
    mapper = inspect(Child)
    columns = mapper.columns
    assert columns["parent_id"].nullable is False
    assert columns["pseudonym"].nullable is False
    assert columns["pin_hash"].nullable is False
    assert columns["date_of_birth"].nullable is True
    assert "parent" in mapper.relationships


def test_parent_email_uniqueness_is_declared_once() -> None:
    """Email uniqueness comes from a named constraint, never a duplicated index.

    Declaring ``unique=True`` together with ``index=True`` on the column would emit a
    unique index instead of the constraint and leave the model out of step with the
    migration, so both are asserted here.
    """
    table = Parent.__table__
    unique_constraints = [
        constraint
        for constraint in table.constraints
        if isinstance(constraint, UniqueConstraint)
    ]
    assert [constraint.name for constraint in unique_constraints] == [
        "uq_auth_parents_email"
    ]
    assert [column.name for column in unique_constraints[0].columns] == ["email"]
    assert table.indexes == set()


def test_child_indexes_cover_only_the_parent_foreign_key() -> None:
    table = Child.__table__
    assert {index.name for index in table.indexes} == {"ix_auth_children_parent_id"}
    assert {constraint.name for constraint in table.constraints} >= {
        "uq_auth_children_pseudonym",
        "ck_auth_children_pseudonym_length",
    }


def test_child_parent_foreign_key_cascades() -> None:
    foreign_keys = list(Child.__table__.c.parent_id.foreign_keys)
    assert len(foreign_keys) == 1
    assert foreign_keys[0].target_fullname == "auth_parents.id"
    assert foreign_keys[0].ondelete == "CASCADE"
