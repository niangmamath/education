"""Reading the competency graph of the published referential.

Two callers need the same graph for two different questions, and both belong
here rather than duplicated where they are asked.

The assessment (étape 14) asks *"which competencies are ready to be tested
right now"* — a class's competencies whose prerequisites, staying inside that
same class, are already mastered. It calls `load` scoped to one class: only
that class's competencies become nodes, so a prerequisite edge reaching
outside the class is never resolved and `frontier` cannot see it. That is
deliberate, not a limitation to work around — the palier a child is tested on
stays bounded to her declared class, and a descent into an earlier class stays
the diagnostic's reactive business, never a proactive scan of the whole
programme (décision du propriétaire, 25 août 2026).

The diagnostic (étape 12) asks the opposite question — *"what, anywhere in the
referential, explains this one gap"* — and calls `load` unscoped, so
`unmet_ancestors` can walk as many hops as it takes, across classes and
subjects, exactly as the seed data's own prerequisite edges already do.

Nothing here is stored. Like every derived reading since ADR-015, the graph is
rebuilt from `ref_competencies` and `ref_competency_prerequisites` at the
moment it is asked for.
"""

from __future__ import annotations

import uuid
from collections.abc import Iterable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.referential import (
    VERSION_STATUS_PUBLISHED,
    Competency,
    CompetencyPrerequisite,
    Domain,
    Level,
    ReferentialVersion,
)


class Node:
    """Where one competency sits, and the order it is taught in."""

    __slots__ = ("code", "label", "domain_code", "domain_label", "level_code", "order")

    def __init__(
        self,
        code: str,
        label: str,
        domain_code: str,
        domain_label: str,
        level_code: str,
        order: tuple[int, int],
    ) -> None:
        self.code = code
        self.label = label
        self.domain_code = domain_code
        self.domain_label = domain_label
        self.level_code = level_code
        # (domain position, competency position): the order a programme
        # teaches a class's competencies in, domain by domain.
        self.order = order


class CompetencyGraph:
    """The nodes loaded and the direct-prerequisite edges between them.

    An edge is only present here when **both** ends were loaded as nodes.
    Scoping which nodes are loaded — the whole referential, or one class —
    is therefore what scopes the edges too, without a second flag to keep in
    step with the first.
    """

    __slots__ = ("nodes", "prerequisites")

    def __init__(
        self, nodes: dict[str, Node], prerequisites: dict[str, list[str]]
    ) -> None:
        self.nodes = nodes
        self.prerequisites = prerequisites

    def frontier(
        self, codes: Iterable[str], *, mastered: set[str], tested: set[str]
    ) -> list[str]:
        """Of `codes`, which are ready to be tested now: not yet tested, and
        every prerequisite this graph knows about is already mastered.

        `codes` comes from the catalogue, not from this graph — ADR-013 keeps
        a competency's business code outside any foreign key to the
        referential, so a class's assessment may name a code the published
        edition does not carry (an older edition, or none published at all).
        Such a code is treated as having no prerequisite rather than being
        dropped: the catalogue is what says what a child is asked, and the
        referential only refines *when*, never *whether*.

        A competency with no prerequisite in this graph — none at all, or all
        of them outside its scope — is ready by default; a class's programme
        has to start somewhere. Ordered as the programme teaches them, domain
        by domain where the graph places them, alphabetically otherwise, so a
        served palier reads as a lesson plan and not as a database dump.
        """
        ready = [
            code
            for code in codes
            if code not in tested
            and all(p in mastered for p in self.prerequisites.get(code, ()))
        ]
        return sorted(
            ready,
            key=lambda code: (
                self.nodes[code].order if code in self.nodes else (10**9, 0),
                code,
            ),
        )

    def unmet_ancestors(self, code: str, *, mastered: set[str]) -> list[str]:
        """Every prerequisite behind `code` that is not yet mastered, however
        many hops back it takes.

        A branch stops the moment it reaches a mastered node: mastered is
        evidence against being the cause (ADR-015). An unmet branch keeps
        being walked, whether or not it has ever been tested — an untested
        prerequisite is exactly what `unobserved-prerequisite` needs to find,
        several classes back if that is where the chain leads.
        """
        found: list[str] = []
        seen: set[str] = {code}
        stack = list(self.prerequisites.get(code, ()))
        while stack:
            node = stack.pop()
            if node in seen:
                continue
            seen.add(node)
            if node in mastered:
                continue
            found.append(node)
            stack.extend(self.prerequisites.get(node, ()))
        return found


async def load(db: AsyncSession, *, level_code: str | None = None) -> CompetencyGraph:
    """The published edition's competency graph, scoped to one class or not.

    An unpublished referential yields an empty graph rather than an error: a
    caller with nothing to place should say so plainly, the way `_tree` in the
    diagnostic already does.
    """
    version = await db.scalar(
        select(ReferentialVersion).where(
            ReferentialVersion.status == VERSION_STATUS_PUBLISHED
        )
    )
    if version is None:
        return CompetencyGraph({}, {})

    query = (
        select(
            Competency.id,
            Competency.code,
            Competency.label,
            Competency.position,
            Domain.code,
            Domain.label,
            Domain.position,
            Level.code,
        )
        .join(Domain, Domain.id == Competency.domain_id)
        .join(Level, Level.id == Competency.level_id)
        .where(Competency.version_id == version.id)
    )
    if level_code is not None:
        query = query.where(Level.code == level_code)

    rows = (await db.execute(query)).all()

    nodes: dict[str, Node] = {}
    identifiers: dict[uuid.UUID, str] = {}
    for (
        identifier,
        code,
        label,
        position,
        domain_code,
        domain_label,
        domain_position,
        lvl_code,
    ) in rows:
        nodes[code] = Node(
            code,
            label,
            domain_code,
            domain_label,
            lvl_code,
            (domain_position, position),
        )
        identifiers[identifier] = code

    if not identifiers:
        return CompetencyGraph(nodes, {})

    prerequisites = await _edges(db, version.id, identifiers)
    return CompetencyGraph(nodes, prerequisites)


async def _edges(
    db: AsyncSession,
    version_id: uuid.UUID,
    identifiers: dict[uuid.UUID, str],
) -> dict[str, list[str]]:
    """Direct-prerequisite edges between the given identifiers, by code.

    An edge whose other end was not loaded as a node is silently dropped: it
    reaches outside whatever scope the caller asked `load` for, and a scoped
    caller (the assessment) must not see it. An unscoped caller sees every
    competency of the version as a node, so nothing is ever dropped for it.
    """
    rows = (
        await db.execute(
            select(
                CompetencyPrerequisite.competency_id,
                CompetencyPrerequisite.prerequisite_id,
            ).where(
                CompetencyPrerequisite.version_id == version_id,
                CompetencyPrerequisite.competency_id.in_(list(identifiers)),
            )
        )
    ).all()

    prerequisites: dict[str, list[str]] = {}
    for competency_id, prerequisite_id in rows:
        code = identifiers.get(competency_id)
        required = identifiers.get(prerequisite_id)
        if code is not None and required is not None:
            prerequisites.setdefault(code, []).append(required)
    return prerequisites
