"""SQLAlchemy models exported for application and Alembic metadata discovery."""

from app.models.catalog import Activity, ActivityCompetency, H5PPackage
from app.models.identity import Child, Parent
from app.models.referential import (
    Competency,
    CompetencyPrerequisite,
    Domain,
    Level,
    ReferentialVersion,
    Subject,
)

__all__ = [
    "Activity",
    "ActivityCompetency",
    "Child",
    "Competency",
    "CompetencyPrerequisite",
    "Domain",
    "H5PPackage",
    "Level",
    "Parent",
    "ReferentialVersion",
    "Subject",
]
