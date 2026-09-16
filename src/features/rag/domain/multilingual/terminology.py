"""
Phase 2 — Protected Legal & Botanical Terminology Registry.

Defines terms that MUST be preserved during query normalization and response translation.
"""

from __future__ import annotations

from typing import Set

PROTECTED_TERMS: Set[str] = {
    # Botanical / Ingredient names
    "ashwagandha",
    "withania somnifera",
    "pippali",
    "piper longum",
    "brahmi",
    "bacopa monnieri",
    "tulsi",
    "ocimum sanctum",
    "turmeric",
    "curcuma longa",
    "shatavari",
    "asparagus racemosus",
    "guduchi",
    "tinospora cordifolia",
    "amla",
    "triphala",
    "haritaki",
    "bibhitaki",
    "arjuna",
    "giloy",
    "mulethi",
    
    # Legal & Regulatory Concepts
    "patent",
    "patentability",
    "novelty",
    "inventive step",
    "industrial applicability",
    "prior art",
    "traditional knowledge",
    "tkdl",
    "biodiversity",
    "abs",
    "access and benefit sharing",
    "ayurveda-aahara",
    "ayurveda aahara",
    "fssai",
    "drugs and cosmetics",
    "drugs and magic remedies",
    "trips",
    "pct",
    "cbd",
    "nagoya protocol",
    "wipo",
    "section 3(p)",
    "section 3(d)",
    "section 3(e)",
    "schedule e",
    "schedule b",
}
