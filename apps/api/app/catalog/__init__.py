"""The catalogue of activities, and the vetted packages some of them play.

Registration and verification are commands rather than routes: a package is
inspected, stored and recorded by someone with access to the server, and there
is no editor, per ADR-006 and ADR-012. See `docs/backend/catalogue-activites.md`.
"""

from app.catalog.checks import CheckReport, check_catalogue
from app.catalog.h5p import (
    ALLOWED_LIBRARIES,
    PackageFacts,
    PackageRefused,
    inspect_package,
)
from app.catalog.registration import (
    RegistrationRefused,
    RegistrationReport,
    register_package,
)

__all__ = [
    "ALLOWED_LIBRARIES",
    "CheckReport",
    "PackageFacts",
    "PackageRefused",
    "RegistrationRefused",
    "RegistrationReport",
    "check_catalogue",
    "inspect_package",
    "register_package",
]
