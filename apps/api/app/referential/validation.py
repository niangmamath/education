"""What the file must be true about itself before anything is written.

The database already refuses a great deal: a code declared twice inside a
version, a competency borrowing a domain from another edition, a competency
requiring itself. Repeating those checks here is not redundant — an import
report that names the offending line of the file is worth more than an
`IntegrityError`, and a file is refused as a whole rather than half applied.

One check has no database equivalent at all: a cycle in the prerequisite tree.
`A` requires `B` which requires `A` is a perfectly legal pair of rows, and no
constraint can express its impossibility. It is caught here, and only here.

Every check collects rather than raises, so a hand-written file gets all of its
mistakes back in one pass instead of one per run.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from pydantic import ValidationError

from app.referential.document import CompetencyIn, ReferentialDocument

_WHITE, _GREY, _BLACK = 0, 1, 2


@dataclass(frozen=True, slots=True)
class ImportIssue:
    """One reason the file cannot be imported, pointing at where it happens."""

    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.path} : {self.message}"


def issues_from_validation_error(error: ValidationError) -> list[ImportIssue]:
    """Turn a Pydantic failure into the same issues as every other check.

    The caller reports one list, whatever refused the file.
    """
    return [
        ImportIssue(path=_format_location(detail["loc"]), message=detail["msg"])
        for detail in error.errors()
    ]


def _format_location(location: Iterable[int | str]) -> str:
    """`("competencies", 3, "position")` reads back as `competencies[3].position`."""
    parts: list[str] = []
    for part in location:
        if isinstance(part, int):
            parts.append(f"[{part}]")
        else:
            parts.append(f".{part}" if parts else str(part))
    return "".join(parts) or "document"


def validate_document(document: ReferentialDocument) -> list[ImportIssue]:
    """Every reason the document cannot be imported, in reading order."""
    issues: list[ImportIssue] = []
    issues += _check_levels(document)
    issues += _check_subjects_and_domains(document)
    issues += _check_competencies(document)
    issues += _check_prerequisites(document)
    return issues


def _check_levels(document: ReferentialDocument) -> list[ImportIssue]:
    issues: list[ImportIssue] = []
    seen_codes: dict[str, int] = {}
    seen_positions: dict[int, int] = {}
    for index, level in enumerate(document.levels):
        path = f"levels[{index}]"
        first = seen_codes.get(level.code)
        if first is None:
            seen_codes[level.code] = index
        else:
            issues.append(
                _duplicate(f"{path}.code", "code", level.code, f"levels[{first}]")
            )
        held_by = seen_positions.get(level.position)
        if held_by is None:
            seen_positions[level.position] = index
        else:
            issues.append(
                _duplicate(
                    f"{path}.position", "rang", level.position, f"levels[{held_by}]"
                )
            )
    return issues


def _check_subjects_and_domains(document: ReferentialDocument) -> list[ImportIssue]:
    """Subjects order among themselves, domains among their siblings.

    Domain codes, on the other hand, are unique across the whole edition and not
    merely inside their subject: that is what `uq_ref_domains_version_code`
    enforces, and the file is checked against the same rule.
    """
    issues: list[ImportIssue] = []
    subject_codes: dict[str, int] = {}
    subject_positions: dict[int, int] = {}
    domain_codes: dict[str, str] = {}

    for index, subject in enumerate(document.subjects):
        path = f"subjects[{index}]"
        first = subject_codes.get(subject.code)
        if first is None:
            subject_codes[subject.code] = index
        else:
            issues.append(
                _duplicate(f"{path}.code", "code", subject.code, f"subjects[{first}]")
            )
        held_by = subject_positions.get(subject.position)
        if held_by is None:
            subject_positions[subject.position] = index
        else:
            issues.append(
                _duplicate(
                    f"{path}.position", "rang", subject.position, f"subjects[{held_by}]"
                )
            )

        domain_positions: dict[int, int] = {}
        for domain_index, domain in enumerate(subject.domains):
            domain_path = f"{path}.domains[{domain_index}]"
            declared_at = domain_codes.get(domain.code)
            if declared_at is None:
                domain_codes[domain.code] = domain_path
            else:
                issues.append(
                    _duplicate(f"{domain_path}.code", "code", domain.code, declared_at)
                )
            sibling = domain_positions.get(domain.position)
            if sibling is None:
                domain_positions[domain.position] = domain_index
            else:
                issues.append(
                    _duplicate(
                        f"{domain_path}.position",
                        "rang",
                        domain.position,
                        f"{path}.domains[{sibling}]",
                    )
                )
    return issues


def _check_competencies(document: ReferentialDocument) -> list[ImportIssue]:
    """Codes, references to a level and a domain, and order inside a shelf.

    Two competencies of the same domain *and* the same level competing for the
    same rank leave their order undefined, which the reading routes of 07.3
    would have to break arbitrarily. Two competencies of the same domain at
    different levels may of course share a rank.
    """
    issues: list[ImportIssue] = []
    levels = {level.code for level in document.levels}
    domains = {domain.code for _, domain in document.domains()}

    seen_codes: dict[str, int] = {}
    seen_ranks: dict[tuple[str, str, int], int] = {}
    for index, competency in enumerate(document.competencies):
        path = f"competencies[{index}]"
        first = seen_codes.get(competency.code)
        if first is None:
            seen_codes[competency.code] = index
        else:
            issues.append(
                _duplicate(
                    f"{path}.code", "code", competency.code, f"competencies[{first}]"
                )
            )
        if competency.level not in levels:
            issues.append(
                ImportIssue(
                    path=f"{path}.level",
                    message=f"le niveau « {competency.level} » n’est pas déclaré dans ce fichier",
                )
            )
        if competency.domain not in domains:
            issues.append(
                ImportIssue(
                    path=f"{path}.domain",
                    message=f"le domaine « {competency.domain} » n’est pas déclaré dans ce fichier",
                )
            )
        shelf = (competency.domain, competency.level, competency.position)
        neighbour = seen_ranks.get(shelf)
        if neighbour is None:
            seen_ranks[shelf] = index
        else:
            issues.append(
                ImportIssue(
                    path=f"{path}.position",
                    message=(
                        f"le rang {competency.position} est déjà pris dans ce domaine et "
                        f"à ce niveau par competencies[{neighbour}]"
                    ),
                )
            )
    return issues


def _check_prerequisites(document: ReferentialDocument) -> list[ImportIssue]:
    """Known ends, no self-reference, no repetition, and no cycle."""
    issues: list[ImportIssue] = []
    known = {competency.code for competency in document.competencies}
    edges: dict[str, list[str]] = {}

    for index, competency in enumerate(document.competencies):
        path = f"competencies[{index}].prerequisites"
        resolved: list[str] = []
        seen: dict[str, int] = {}
        for rank, required in enumerate(competency.prerequisites):
            if required == competency.code:
                issues.append(
                    ImportIssue(
                        path=f"{path}[{rank}]",
                        message="une compétence ne peut pas être son propre prérequis",
                    )
                )
                continue
            if required not in known:
                issues.append(
                    ImportIssue(
                        path=f"{path}[{rank}]",
                        message=f"la compétence « {required} » n’est pas déclarée dans ce fichier",
                    )
                )
                continue
            first = seen.get(required)
            if first is not None:
                issues.append(
                    _duplicate(
                        f"{path}[{rank}]", "prérequis", required, f"{path}[{first}]"
                    )
                )
                continue
            seen[required] = rank
            resolved.append(required)
        edges[competency.code] = resolved

    issues += _check_cycles(document.competencies, edges)
    return issues


def _check_cycles(
    competencies: list[CompetencyIn], edges: dict[str, list[str]]
) -> list[ImportIssue]:
    """No competency may end up requiring itself through a chain.

    This is the check no constraint can replace. A cycle would leave the
    remediation engine of step 12 with no entry point: every competency in the
    loop would be waiting for another one in the same loop.
    """
    index_of = {competency.code: index for index, competency in enumerate(competencies)}
    return [
        ImportIssue(
            path=f"competencies[{index_of[cycle[0]]}].prerequisites",
            message="cycle de prérequis : " + " → ".join(cycle),
        )
        for cycle in _find_cycles(edges)
    ]


def _find_cycles(edges: dict[str, list[str]]) -> list[list[str]]:
    """Every distinct cycle reachable in the prerequisite graph.

    A depth-first walk that colours nodes: grey while on the current path, black
    once fully explored. Meeting a grey node means the path came back on itself,
    and the cycle is the tail of that path. The walk is iterative because a deep
    referential would otherwise depend on Python's recursion limit.
    """
    colours: dict[str, int] = {}
    cycles: list[list[str]] = []
    reported: set[tuple[str, ...]] = set()

    for start in edges:
        if colours.get(start, _WHITE) != _WHITE:
            continue
        colours[start] = _GREY
        path = [start]
        stack = [(start, iter(edges.get(start, ())))]
        while stack:
            node, children = stack[-1]
            descended = False
            for child in children:
                colour = colours.get(child, _WHITE)
                if colour == _GREY:
                    cycle = path[path.index(child) :] + [child]
                    signature = _cycle_signature(cycle)
                    if signature not in reported:
                        reported.add(signature)
                        cycles.append(cycle)
                elif colour == _WHITE:
                    colours[child] = _GREY
                    path.append(child)
                    stack.append((child, iter(edges.get(child, ()))))
                    descended = True
                    break
            if not descended:
                colours[node] = _BLACK
                stack.pop()
                path.pop()
    return cycles


def _cycle_signature(cycle: list[str]) -> tuple[str, ...]:
    """The same loop found from two starting points is one cycle, not two."""
    loop = cycle[:-1]
    start = loop.index(min(loop))
    return tuple(loop[start:] + loop[:start])


def _duplicate(path: str, what: str, value: object, first: str) -> ImportIssue:
    return ImportIssue(
        path=path, message=f"{what} « {value} » déjà déclaré par {first}"
    )
