"""Roles and knowledge detail levels (BUSINESS_PROJECT section 4, BACKEND-ARCHITECTURE section 6).

They live in the shared kernel because several modules store them (identity, audit, qa, pathways,
knowledge) and modules must not import each other.
"""

from enum import StrEnum


class Role(StrEnum):
    """The 7 account roles. Guest has no account, so it is not stored in the database."""

    ADMIN = "ADMIN"
    RECEPTIONIST = "RECEPTIONIST"  # ERD: LE_TAN
    DOCTOR = "DOCTOR"  # ERD: BAC_SI
    TECHNICIAN = "TECHNICIAN"  # ERD: KTV (technician / rehab nurse)
    CURATOR = "CURATOR"
    PATIENT = "PATIENT"  # ERD: BENH_NHAN
    CAREGIVER = "CAREGIVER"  # ERD: NGUOI_NHA (relative)


class DetailLevel(StrEnum):
    """Answer detail level (BUSINESS_PROJECT section 4.1)."""

    BASIC = "BASIC"
    DEEP = "DEEP"
