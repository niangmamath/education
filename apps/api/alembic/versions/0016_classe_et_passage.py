"""La classe de l'élève, et son passage dans la classe supérieure.

Trois changements, et chacun répond à une chose que le propriétaire a demandée.

**`auth_children.level_code`** porte la classe où l'élève se trouve aujourd'hui.
Elle est demandée à l'inscription, parce que c'est elle qui décide de l'examen
d'entrée à donner : il y en a un par classe, du CI au CM2.

La colonne est **nullable**, et pas par facilité. Un profil ouvert avant que la
plateforme ne demande la classe existe ; lui en attribuer une d'office
affirmerait sur un enfant réel quelque chose que personne n'a dit. Une classe
absente veut dire « pas encore déclarée », et l'interface la réclame.

**`auth_child_promotions`** garde chaque passage comme un fait, avec sa date et
le parent qui l'a décidé. Rien ne s'y met à jour : le dossier d'un élève le suit
toute sa scolarité, et savoir qu'une lacune a été observée alors qu'il était en
CE1 n'a pas le même poids qu'une lacune observée trois ans plus tard. Un parent
qui se trompe de bouton fait un passage de plus ; il ne réécrit pas le précédent,
exactement comme une observation n'écrase jamais l'historique.

**`catalog_activities.level_code`** dit quelle classe un examen interroge. Pour
le reste du catalogue c'est une indication : une fiche vise une compétence, et
une compétence porte déjà son niveau.

Aucune de ces colonnes n'est une clé étrangère vers `ref_levels`, et c'est le
raisonnement d'ADR-013 : un niveau appartient à une édition du référentiel, alors
que la classe d'un enfant et le catalogue lui survivent tous les deux.

Revision ID: 0016_classe_et_passage
Revises: 0015_h5p_allowed_libraries
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0016_classe_et_passage"
down_revision: str | None = "0015_h5p_allowed_libraries"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "auth_children", sa.Column("level_code", sa.String(length=50), nullable=True)
    )
    op.add_column(
        "catalog_activities",
        sa.Column("level_code", sa.String(length=50), nullable=True),
    )

    op.create_table(
        "auth_child_promotions",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False
        ),
        sa.Column(
            "child_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("auth_children.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "decided_by_parent_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("auth_parents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("from_level_code", sa.String(length=50), nullable=True),
        sa.Column("to_level_code", sa.String(length=50), nullable=False),
        sa.Column(
            "decided_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "from_level_code IS NULL OR from_level_code <> to_level_code",
            name="ck_auth_child_promotions_moves",
        ),
    )
    op.create_index(
        "ix_auth_child_promotions_child",
        "auth_child_promotions",
        ["child_id", "decided_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_auth_child_promotions_child", table_name="auth_child_promotions")
    op.drop_table("auth_child_promotions")
    op.drop_column("catalog_activities", "level_code")
    op.drop_column("auth_children", "level_code")
