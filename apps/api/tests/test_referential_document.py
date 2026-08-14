"""What the file itself must look like, one value at a time.

These tests need no database: they check the reading of a file, not its effect.
"""

from __future__ import annotations

from typing import Any

import pytest
from pydantic import ValidationError

from app.referential.document import ReferentialDocument
from app.referential.validation import issues_from_validation_error


def minimal_document() -> dict[str, Any]:
    """One coherent edition, small enough that a test can break one thing in it."""
    return {
        "version": {"code": "test-doc", "label": "Édition de test"},
        "levels": [{"code": "cp", "label": "Cours préparatoire", "position": 1}],
        "subjects": [
            {
                "code": "math",
                "label": "Mathématiques",
                "position": 1,
                "domains": [
                    {"code": "math-num", "label": "Nombres et calcul", "position": 1}
                ],
            }
        ],
        "competencies": [
            {
                "code": "cp-math-num-01",
                "label": "Dénombrer jusqu’à 100",
                "description": None,
                "position": 1,
                "level": "cp",
                "domain": "math-num",
                "prerequisites": [],
            }
        ],
    }


def test_a_coherent_file_is_read() -> None:
    document = ReferentialDocument.model_validate(minimal_document())

    assert document.version.code == "test-doc"
    assert [level.code for level in document.levels] == ["cp"]
    assert [domain.code for _, domain in document.domains()] == ["math-num"]


def test_an_unknown_key_is_refused_rather_than_ignored() -> None:
    """A mistyped key silently dropped would lose part of the referential."""
    payload = minimal_document()
    payload["levels"][0]["libelle"] = "Cours préparatoire"

    with pytest.raises(ValidationError):
        ReferentialDocument.model_validate(payload)


@pytest.mark.parametrize(
    "code",
    ["CP", "cp lecture", "cp_lecture", "-cp", "cp-", "cp--01", "é", ""],
)
def test_a_code_that_is_not_a_code_is_refused(code: str) -> None:
    payload = minimal_document()
    payload["levels"][0]["code"] = code

    with pytest.raises(ValidationError):
        ReferentialDocument.model_validate(payload)


def test_a_position_starts_at_one() -> None:
    payload = minimal_document()
    payload["levels"][0]["position"] = 0

    with pytest.raises(ValidationError):
        ReferentialDocument.model_validate(payload)


def test_an_empty_label_is_refused() -> None:
    payload = minimal_document()
    payload["subjects"][0]["label"] = "   "

    with pytest.raises(ValidationError):
        ReferentialDocument.model_validate(payload)


def test_a_missing_version_is_refused() -> None:
    payload = minimal_document()
    del payload["version"]

    with pytest.raises(ValidationError):
        ReferentialDocument.model_validate(payload)


def test_a_shape_failure_becomes_an_issue_that_names_the_line() -> None:
    """Whatever refuses the file, the operator reads one kind of report."""
    payload = minimal_document()
    payload["competencies"][0]["position"] = -1

    with pytest.raises(ValidationError) as failure:
        ReferentialDocument.model_validate(payload)

    issues = issues_from_validation_error(failure.value)
    assert [issue.path for issue in issues] == ["competencies[0].position"]
