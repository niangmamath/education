"""Assigning catalogue activities to children, and following what becomes of them.

The rules live in `service.py` because the Parent space and the Élève space act
on the same rows from opposite sides. See `docs/backend/affectations.md`.
"""

from app.assignments.service import (
    assign_activity,
    cancel_assignment,
    complete_assignment,
    list_for_child,
    list_for_parent,
    start_assignment,
)

__all__ = [
    "assign_activity",
    "cancel_assignment",
    "complete_assignment",
    "list_for_child",
    "list_for_parent",
    "start_assignment",
]
