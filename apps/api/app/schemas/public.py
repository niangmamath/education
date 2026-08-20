"""What the public stats route hands a visitor: counts, never names."""

from __future__ import annotations

from pydantic import BaseModel


class PublicStats(BaseModel):
    families: int
    children: int
    activities_completed: int
    competencies_covered: int
    competencies_total: int
