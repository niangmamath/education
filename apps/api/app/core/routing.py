"""
StudentConnect API Routing

Main router for all API endpoints.
"""

from fastapi import APIRouter

# Create the main API router
api_router = APIRouter()


# Import and include sub-routers
# These will be added as modules are implemented

# Example structure for future imports:
# from app.api.v1 import auth, families, students, competencies, assessments, gaps
# from app.api.v1 import contents, remediation, analytics, notifications, storage

# For now, we'll add placeholder routers to show the structure

# Auth router (placeholder)
# api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# Families router (placeholder)
# api_router.include_router(families.router, prefix="/families", tags=["families"])

# Students router (placeholder)
# api_router.include_router(students.router, prefix="/students", tags=["students"])

# Competencies router (placeholder)
# api_router.include_router(competencies.router, prefix="/competencies", tags=["competencies"])

# Assessments router (placeholder)
# api_router.include_router(assessments.router, prefix="/assessments", tags=["assessments"])

# Gaps router (placeholder)
# api_router.include_router(gaps.router, prefix="/gaps", tags=["gaps"])

# Contents router (placeholder)
# api_router.include_router(contents.router, prefix="/contents", tags=["contents"])

# Remediation router (placeholder)
# api_router.include_router(remediation.router, prefix="/remediation", tags=["remediation"])

# Analytics router (placeholder)
# api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])

# Notifications router (placeholder)
# api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])

# Storage router (placeholder)
# api_router.include_router(storage.router, prefix="/storage", tags=["storage"])
