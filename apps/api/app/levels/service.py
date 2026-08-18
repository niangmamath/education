"""Les classes de l'élémentaire, telles que le référentiel en vigueur les déclare.

Les niveaux ne sont pas écrits en dur ici, et c'est délibéré : ils appartiennent
à l'édition du référentiel, qui est la seule chose autorisée à dire de quoi
l'élémentaire est fait. Une plateforme qui figerait « CI, CP, CE1, CE2, CM1,
CM2 » dans son code refuserait de servir un pays qui découpe autrement — et
mentirait dès la première édition publiée qui ne lui ressemble pas.

Deux questions seulement sont posées ici, et elles portent tout le reste.

**« Que doit tenir un élève de cette classe ? »** — les compétences sont
cumulatives : un CE2 doit celles du CI, du CP, du CE1 et du CE2. Sans cela, le
diagnostic ne pourrait pas descendre, et descendre est précisément ce que cette
plateforme fait de plus utile.

**« Quelle est la classe suivante ? »** — pour le passage, décidé par le parent.
Le CM2 n'a pas de suivant dans l'élémentaire : la suite est le collège, que cette
plateforme ne couvre pas et sur lequel elle ne prétend rien.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.referential import (
    VERSION_STATUS_PUBLISHED,
    Level,
    ReferentialVersion,
)

UNKNOWN_LEVEL_MESSAGE = "Cette classe n’existe pas dans le programme en vigueur"


async def levels_in_force(db: AsyncSession) -> list[tuple[str, str]]:
    """Les classes de l'édition en vigueur, du plus petit niveau au plus grand.

    Vide quand aucune édition n'est publiée, ce qui est un état réel et non une
    erreur : la plateforme sait alors qu'elle ne sait pas, et les appelants le
    disent plutôt que d'inventer une liste.
    """
    version = await db.scalar(
        select(ReferentialVersion)
        .where(ReferentialVersion.status == VERSION_STATUS_PUBLISHED)
        .limit(1)
    )
    if version is None:
        return []

    rows = await db.scalars(
        select(Level).where(Level.version_id == version.id).order_by(Level.position)
    )
    return [(row.code, row.label) for row in rows.all()]


async def is_acceptable(db: AsyncSession, level_code: str) -> bool:
    """La classe déclarée est-elle recevable ?

    Quand une édition du référentiel est en vigueur, la classe doit s'y trouver :
    un profil portant `ce7` ne recevrait aucun examen et personne ne saurait
    pourquoi.

    Quand **aucune** édition n'est publiée, la déclaration est acceptée telle
    quelle. Ce n'est pas un relâchement par commodité : la classe est une
    déclaration du parent, et une plateforme sans programme importé n'a aucune
    base pour la contredire. Refuser reviendrait à empêcher une famille d'exister
    tant qu'un opérateur n'a pas fait son travail — une panne bien plus grave que
    la classe fantaisiste qu'on laisse passer, laquelle se corrige d'ailleurs
    d'un appel à la route qui déclare la classe.
    """
    known = await levels_in_force(db)
    if not known:
        return True
    return any(code == level_code for code, _ in known)


async def levels_up_to(db: AsyncSession, level_code: str | None) -> list[str]:
    """Les classes qu'un élève de cette classe doit tenir, la sienne comprise.

    La règle du cumul, écrite une fois pour toute la plateforme. Une classe
    inconnue ou non déclarée ne donne **rien** plutôt que tout : proposer le
    programme entier à un enfant dont on ignore la classe serait pire que de ne
    rien proposer, et la seule chose honnête à faire est de demander sa classe.
    """
    if level_code is None:
        return []

    ordered = [code for code, _ in await levels_in_force(db)]
    if level_code not in ordered:
        return []
    return ordered[: ordered.index(level_code) + 1]


async def next_level(db: AsyncSession, level_code: str | None) -> str | None:
    """La classe suivante, ou rien s'il n'y en a pas.

    Rien signifie « la dernière classe de l'élémentaire » aussi bien que « classe
    inconnue ». Les appelants n'ont pas à distinguer : dans les deux cas, il n'y
    a pas de passage à proposer.
    """
    if level_code is None:
        return None

    ordered = [code for code, _ in await levels_in_force(db)]
    if level_code not in ordered:
        return None

    position = ordered.index(level_code)
    if position + 1 >= len(ordered):
        return None
    return ordered[position + 1]


async def label_of(db: AsyncSession, level_code: str | None) -> str | None:
    """Le nom lisible d'une classe — « Cours élémentaire première année ».

    Un parent ne lit pas `ce1`, et un code affiché tel quel dans une interface
    est une fuite d'implémentation.
    """
    if level_code is None:
        return None
    for code, label in await levels_in_force(db):
        if code == level_code:
            return label
    return None
