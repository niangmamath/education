"""
StudentConnect API Routing

Main router for all API endpoints.
"""

from fastapi import APIRouter

from app.api.v1 import auth, children

# Create the main API router
api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(children.router, prefix="/auth", tags=["auth"])


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
