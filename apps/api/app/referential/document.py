"""The shape of a referential import file.

Pydantic checks here what can be checked on one value at a time: a code that
looks like a code, a label that is not empty, a position that starts at one.
Everything that needs to read the file as a whole — a code declared twice, a
competency pointing at a level the file does not contain, a cycle in the
prerequisite tree — belongs to `validation.py`, because those answers only exist
once every line has been read.

Unknown keys are refused rather than ignored. A referential is written by hand,
and a mistyped key that is silently dropped is exactly the kind of loss an
import must not cover up.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated, Any, Final

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from app.models.referential import CODE_LENGTH, LABEL_LENGTH

# Lower case, digits and single hyphens: `cm1-math-num-01` reads the same in a
# URL, in a log line and in a spreadsheet.
CODE_PATTERN: Final = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"

Code = Annotated[
    str,
    StringConstraints(pattern=CODE_PATTERN, min_length=1, max_length=CODE_LENGTH),
]
Label = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=LABEL_LENGTH),
]
Position = Annotated[int, Field(ge=1)]


class _Node(BaseModel):
    """Common configuration: nothing unexpected gets through."""

    model_config = ConfigDict(extra="forbid")


class VersionIn(_Node):
    """The edition the file describes."""

    code: Code
    label: Label


class LevelIn(_Node):
    code: Code
    label: Label
    position: Position


class DomainIn(_Node):
    code: Code
    label: Label
    position: Position


class SubjectIn(_Node):
    code: Code
    label: Label
    position: Position
    domains: list[DomainIn] = Field(default_factory=list)


class CompetencyIn(_Node):
    """A competency, attached to one domain and one level by their codes."""

    code: Code
    label: Label
    description: str | None = None
    position: Position
    level: Code
    domain: Code
    prerequisites: list[Code] = Field(default_factory=list)


class ReferentialDocument(_Node):
    """One edition of the referential, as written in a file."""

    version: VersionIn
    levels: list[LevelIn] = Field(default_factory=list)
    subjects: list[SubjectIn] = Field(default_factory=list)
    competencies: list[CompetencyIn] = Field(default_factory=list)

    def domains(self) -> list[tuple[SubjectIn, DomainIn]]:
        """Every domain with the subject it belongs to, in file order."""
        return [
            (subject, domain) for subject in self.subjects for domain in subject.domains
        ]


def read_json(path: Path) -> Any:
    """Read the file as JSON, leaving both failures to the caller.

    `OSError` means the file could not be read at all; `json.JSONDecodeError`
    means it is not JSON. The two deserve different exit codes, so neither is
    caught here.
    """
    return json.loads(path.read_text(encoding="utf-8"))
