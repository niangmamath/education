"""What the file must be true about itself, read as a whole.

No database here either. These checks exist so that a hand-written referential
is refused with its line numbers rather than with an `IntegrityError`, and so
that a prerequisite cycle — which no constraint can express — is caught before
anything is written.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.referential.document import ReferentialDocument, read_json
from app.referential.validation import validate_document
from tests.test_referential_document import minimal_document

SHIPPED_FILE = (
    Path(__file__).resolve().parents[1]
    / "seeds"
    / "referential"
    / "fictif-2026-01.json"
)


def competency(
    code: str, prerequisites: list[str] | None = None, **overrides: Any
) -> dict[str, Any]:
    payload = {
        "code": code,
        "label": f"Compétence {code}",
        "description": None,
        "position": 1,
        "level": "cp",
        "domain": "math-num",
        "prerequisites": prerequisites or [],
    }
    payload.update(overrides)
    return payload


def issues_for(payload: dict[str, Any]) -> list[str]:
    document = ReferentialDocument.model_validate(payload)
    return [str(issue) for issue in validate_document(document)]


def test_a_coherent_document_raises_nothing() -> None:
    assert issues_for(minimal_document()) == []


class TestDuplicates:
    def test_a_level_code_declared_twice_is_refused(self) -> None:
        payload = minimal_document()
        payload["levels"].append(
            {"code": "cp", "label": "Cours préparatoire bis", "position": 2}
        )

        issues = issues_for(payload)

        assert issues == ["levels[1].code : code « cp » déjà déclaré par levels[0]"]

    def test_two_levels_may_not_share_a_rank(self) -> None:
        """Their order would be undefined, and school years have one."""
        payload = minimal_document()
        payload["levels"].append(
            {"code": "ce1", "label": "Cours élémentaire", "position": 1}
        )

        assert issues_for(payload) == [
            "levels[1].position : rang « 1 » déjà déclaré par levels[0]"
        ]

    def test_a_domain_code_is_unique_across_the_whole_edition(self) -> None:
        """The database says so too: `uq_ref_domains_version_code` is not scoped
        to the subject."""
        payload = minimal_document()
        payload["subjects"].append(
            {
                "code": "fr",
                "label": "Français",
                "position": 2,
                "domains": [{"code": "math-num", "label": "Homonyme", "position": 1}],
            }
        )

        assert issues_for(payload) == [
            "subjects[1].domains[0].code : code « math-num » déjà déclaré par "
            "subjects[0].domains[0]"
        ]

    def test_two_competencies_of_the_same_shelf_may_not_share_a_rank(self) -> None:
        payload = minimal_document()
        payload["competencies"].append(competency("cp-math-num-02"))

        assert issues_for(payload) == [
            "competencies[1].position : le rang 1 est déjà pris dans ce domaine et "
            "à ce niveau par competencies[0]"
        ]

    def test_the_same_rank_at_another_level_is_fine(self) -> None:
        payload = minimal_document()
        payload["levels"].append(
            {"code": "ce1", "label": "Cours élémentaire", "position": 2}
        )
        payload["competencies"].append(competency("ce1-math-num-01", level="ce1"))

        assert issues_for(payload) == []


class TestReferences:
    def test_a_competency_cannot_point_at_a_level_the_file_does_not_declare(
        self,
    ) -> None:
        payload = minimal_document()
        payload["competencies"][0]["level"] = "cm2"

        assert issues_for(payload) == [
            "competencies[0].level : le niveau « cm2 » n’est pas déclaré dans ce fichier"
        ]

    def test_a_competency_cannot_point_at_an_undeclared_domain(self) -> None:
        payload = minimal_document()
        payload["competencies"][0]["domain"] = "math-geo"

        assert issues_for(payload) == [
            "competencies[0].domain : le domaine « math-geo » n’est pas déclaré dans "
            "ce fichier"
        ]

    def test_a_prerequisite_must_be_a_competency_of_the_file(self) -> None:
        payload = minimal_document()
        payload["competencies"][0]["prerequisites"] = ["cp-math-num-99"]

        assert issues_for(payload) == [
            "competencies[0].prerequisites[0] : la compétence « cp-math-num-99 » "
            "n’est pas déclarée dans ce fichier"
        ]

    def test_every_mistake_is_reported_in_one_pass(self) -> None:
        """A file written by hand deserves all its errors at once."""
        payload = minimal_document()
        payload["competencies"][0]["level"] = "cm2"
        payload["competencies"][0]["domain"] = "math-geo"

        assert len(issues_for(payload)) == 2


class TestPrerequisiteTree:
    def test_a_competency_cannot_be_its_own_prerequisite(self) -> None:
        payload = minimal_document()
        payload["competencies"][0]["prerequisites"] = ["cp-math-num-01"]

        assert issues_for(payload) == [
            "competencies[0].prerequisites[0] : une compétence ne peut pas être son "
            "propre prérequis"
        ]

    def test_the_same_prerequisite_cannot_be_declared_twice(self) -> None:
        payload = minimal_document()
        payload["competencies"].append(
            competency(
                "cp-math-num-02",
                prerequisites=["cp-math-num-01", "cp-math-num-01"],
                position=2,
            )
        )

        assert issues_for(payload) == [
            "competencies[1].prerequisites[1] : prérequis « cp-math-num-01 » déjà "
            "déclaré par competencies[1].prerequisites[0]"
        ]

    def test_a_two_step_cycle_is_caught(self) -> None:
        """No constraint can express this: both rows are perfectly legal."""
        payload = minimal_document()
        payload["competencies"][0]["prerequisites"] = ["cp-math-num-02"]
        payload["competencies"].append(
            competency("cp-math-num-02", prerequisites=["cp-math-num-01"], position=2)
        )

        assert issues_for(payload) == [
            "competencies[0].prerequisites : cycle de prérequis : "
            "cp-math-num-01 → cp-math-num-02 → cp-math-num-01"
        ]

    def test_a_longer_cycle_is_caught_too(self) -> None:
        payload = minimal_document()
        payload["competencies"][0]["prerequisites"] = ["cp-math-num-03"]
        payload["competencies"].append(
            competency("cp-math-num-02", prerequisites=["cp-math-num-01"], position=2)
        )
        payload["competencies"].append(
            competency("cp-math-num-03", prerequisites=["cp-math-num-02"], position=3)
        )

        issues = issues_for(payload)

        assert len(issues) == 1
        assert "cycle de prérequis" in issues[0]

    def test_the_same_loop_is_reported_once(self) -> None:
        """Found from three starting points, it is still one cycle."""
        payload = minimal_document()
        payload["competencies"][0]["prerequisites"] = ["cp-math-num-02"]
        payload["competencies"].append(
            competency("cp-math-num-02", prerequisites=["cp-math-num-03"], position=2)
        )
        payload["competencies"].append(
            competency("cp-math-num-03", prerequisites=["cp-math-num-01"], position=3)
        )

        assert len(issues_for(payload)) == 1

    def test_a_diamond_is_not_a_cycle(self) -> None:
        """Two paths reaching the same competency are ordinary, not circular."""
        payload = minimal_document()
        payload["competencies"].append(
            competency("cp-math-num-02", prerequisites=["cp-math-num-01"], position=2)
        )
        payload["competencies"].append(
            competency("cp-math-num-03", prerequisites=["cp-math-num-01"], position=3)
        )
        payload["competencies"].append(
            competency(
                "cp-math-num-04",
                prerequisites=["cp-math-num-02", "cp-math-num-03"],
                position=4,
            )
        )

        assert issues_for(payload) == []


class TestShippedReferential:
    def test_the_fictional_referential_passes_every_check(self) -> None:
        """The file the project ships must be importable, not merely present."""
        document = ReferentialDocument.model_validate(read_json(SHIPPED_FILE))

        assert validate_document(document) == []

    def test_the_fictional_referential_covers_the_five_primary_years(self) -> None:
        document = ReferentialDocument.model_validate(read_json(SHIPPED_FILE))

        assert [level.code for level in document.levels] == [
            "cp",
            "ce1",
            "ce2",
            "cm1",
            "cm2",
        ]
        assert len(document.competencies) > 0
