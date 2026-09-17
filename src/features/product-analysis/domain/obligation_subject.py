"""
Legal Obligation Subject Domain Module.

Defines the legal entity/subject to whom a statutory or treaty obligation attaches.
Prevents State/Party obligations (e.g., Nagoya Protocol Art. 13 National Focal Points)
from being converted into product-user compliance tasks.
"""

from __future__ import annotations
import re
from enum import Enum
from typing import Optional


class ObligationSubject(str, Enum):
    STATE = "state"
    NATIONAL_AUTHORITY = "national_authority"
    APPLICANT = "applicant"
    MANUFACTURER = "manufacturer"
    RESOURCE_USER = "resource_user"
    COMMUNITY = "community"
    UNKNOWN = "unknown"


def classify_obligation_subject(text: str) -> ObligationSubject:
    """
    Deterministically classifies the subject of a legal obligation based on statutory/treaty text.
    """
    lower_text = text.lower()

    # State / Party / Contracting Party obligations
    state_patterns = [
        r"\beach contracting party shall\b",
        r"\beach party shall\b",
        r"\bthe state shall\b",
        r"\bparties shall\b",
        r"\bthe central government shall\b",
        r"\bmember states shall\b",
    ]
    for pat in state_patterns:
        if re.search(pat, lower_text):
            return ObligationSubject.STATE

    # National Authority obligations
    authority_patterns = [
        r"\bthe national biodiversity authority shall\b",
        r"\bthe authority shall\b",
        r"\bthe state biodiversity board shall\b",
        r"\bthe controller shall\b",
        r"\bthe licensing authority shall\b",
        r"\bthe competent authority shall\b",
    ]
    for pat in authority_patterns:
        if re.search(pat, lower_text):
            return ObligationSubject.NATIONAL_AUTHORITY

    # Manufacturer / Applicant / User obligations
    user_patterns = [
        r"\bno person shall\b",
        r"\bany person who\b",
        r"\bthe applicant shall\b",
        r"\bthe manufacturer shall\b",
        r"\bevery licensee shall\b",
        r"\bwhoever intends to\b",
        r"\buser of genetic resources\b",
    ]
    for pat in user_patterns:
        if re.search(pat, lower_text):
            return ObligationSubject.MANUFACTURER

    return ObligationSubject.UNKNOWN


def is_product_user_obligation(subject: ObligationSubject) -> bool:
    """
    Returns True ONLY if the obligation applies to a product applicant/manufacturer/user.
    State or National Authority obligations return False.
    """
    return subject in (
        ObligationSubject.APPLICANT,
        ObligationSubject.MANUFACTURER,
        ObligationSubject.RESOURCE_USER,
    )
