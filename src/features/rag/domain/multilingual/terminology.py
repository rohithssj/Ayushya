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
    "neem",
    "azadirachta indica",
    "black pepper",
    "piper nigrum",
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
    
    # Core IP & Legal Concepts
    "patent",
    "trademark",
    "geographical indication",
    "gi",
    "copyright",
    "design",
    "trade secret",
    "traditional knowledge",
    "tk",
    "tkdl",
    "abs",
    "access and benefit sharing",
    "nagoya protocol",
    "convention on biological diversity",
    "cbd",
    "trips",
    "pct",
    "madrid system",
    "hague system",
    "budapest treaty",
    
    # Statutes & Regulatory Acts
    "biological diversity act",
    "biological diversity rules",
    "drugs and cosmetics act",
    "drugs and cosmetics rules",
    "drugs and magic remedies act",
    "fssai",
    "ayurveda-aahara",
    "ayurvedic medicine",
    "ayurvedic formulation",
    "national biodiversity authority",
    "nba",
    "pic",
    "mat",
    
    # Section references
    "section 3(p)",
    "section 3(d)",
    "section 3(e)",
    "schedule e",
    "schedule b",
}

