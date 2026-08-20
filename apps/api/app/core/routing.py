"""
StudentConnect API Routing

Main router for all API endpoints.
"""

from fastapi import APIRouter

from app.api.v1 import (
    assessment,
    assignments,
    attempts,
    auth,
    catalog,
    children,
    diagnostic,
    fiches,
    internal,
    progress,
    public,
    referential,
    xapi,
)

# Create the main API router
api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(children.router, prefix="/auth", tags=["auth"])
api_router.include_router(
    referential.router, prefix="/referential", tags=["referential"]
)
api_router.include_router(catalog.router, prefix="/catalog", tags=["catalog"])
api_router.include_router(assignments.router, tags=["assignments"])
api_router.include_router(attempts.router, tags=["attempts"])
api_router.include_router(assessment.router, tags=["assessment"])
api_router.include_router(fiches.router, tags=["fiches"])
api_router.include_router(xapi.router, tags=["xapi"])
api_router.include_router(progress.router, tags=["progress"])
api_router.include_router(diagnostic.router, tags=["diagnostic"])
api_router.include_router(internal.router, tags=["internal"])
api_router.include_router(public.router, tags=["public"])


# Sub-routers added as their step implements them:
# from app.api.v1 import families, students, competencies, assessments, gaps
# from app.api.v1 import contents, remediation, analytics, notifications, storage

# api_router.include_router(families.router, prefix="/families", tags=["families"])
# api_router.include_router(students.router, prefix="/students", tags=["students"])
# api_router.include_router(
#     competencies.router, prefix="/competencies", tags=["competencies"]
# )
# api_router.include_router(
#     assessments.router, prefix="/assessments", tags=["assessments"]
# )
# api_router.include_router(gaps.router, prefix="/gaps", tags=["gaps"])
# api_router.include_router(contents.router, prefix="/contents", tags=["contents"])
# api_router.include_router(
#     remediation.router, prefix="/remediation", tags=["remediation"]
# )
# api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
# api_router.include_router(
#     notifications.router, prefix="/notifications", tags=["notifications"]
# )
# api_router.include_router(storage.router, prefix="/storage", tags=["storage"])
