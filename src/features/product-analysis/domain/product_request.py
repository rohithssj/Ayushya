"""
Product Analysis — ProductAnalysisRequest domain model and input validation.

Validates user-submitted product formulation data before it enters the
retrieval/reasoning pipeline. No legal conclusions are made here.

Rules enforced:
- Required fields must be non-empty strings
- Field lengths are capped to prevent prompt injection / oversized queries
- Ingredients must be a list of IngredientRecord with a non-empty name
- Quantity/unit values are validated but not legally interpreted
- Jurisdiction and classification must come from the supported sets
- traditional_knowledge_ref is optional (supported in model for future UI)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SUPPORTED_JURISDICTIONS: frozenset = frozenset({"india", "international"})

SUPPORTED_CLASSIFICATIONS: frozenset = frozenset(
    {
        "no_preference",
        "no preference — let ayushya assess",
        "ayurveda-aahar",
        "ayurveda-aahara",
        "ayurvedic drug / medicine",
        "classical ayurvedic formulation",
        "proprietary ayurvedic formulation",
        "phytopharmaceutical",
        "ayurvedic cosmetic",
        "proprietary asu medicine",
        "classical formulation",
        "nutraceutical",
        "other / not sure",
        "other",
    }
)

SUPPORTED_PRODUCT_FORMS: frozenset = frozenset(
    {
        "tablet",
        "capsule",
        "syrup / churna",
        "oil / taila",
        "cosmetic cream",
        "powder",
        "decoction",
        "paste",
        "other",
    }
)

SUPPORTED_UNITS: frozenset = frozenset({"mg", "g", "ml", "%", "mcg", "iu", "other"})

MAX_PRODUCT_NAME_LEN = 200
MAX_DESCRIPTION_LEN = 2000
MAX_INGREDIENT_NAME_LEN = 200
MAX_INGREDIENT_QUANTITY_LEN = 50
MAX_TK_REF_LEN = 1000
MAX_INGREDIENTS = 30


# ---------------------------------------------------------------------------
# Domain models
# ---------------------------------------------------------------------------


@dataclass
class IngredientRecord:
    """A single ingredient in the product formulation."""

    name: str
    quantity: str
    unit: str


@dataclass
class ProductAnalysisRequest:
    """
    Validated product formulation analysis request.

    Required Fields:
      jurisdiction               — 'India' or 'International'
      product_name               — product name (required)
      product_form               — dosage form (tablet, capsule, etc.)
      ingredients                — list of IngredientRecord (required, non-empty)
      intended_use               — intended use / purpose (required)

    Optional Classification Facts:
      user_selected_classification — optional hypothesis (default: "no_preference")
      product_claims             — optional product health/marketing claims
      disease_claim_flag         — optional boolean (true if disease claim made)
      disease_claim_text         — optional exact disease claim text
      is_classical_basis         — 'yes' | 'no' | 'unknown'
      classical_reference        — optional reference text/source
      manufacturing_processing   — optional processing details
      description                — optional description/notes (backed by intended_use)
      traditional_knowledge_ref  — optional TK reference
    """

    jurisdiction: str
    product_name: str
    product_form: str
    ingredients: List[IngredientRecord]
    intended_use: str
    user_selected_classification: str = "no_preference"
    product_claims: str = ""
    disease_claim_flag: bool = False
    disease_claim_text: str = ""
    is_classical_basis: str = "unknown"
    classical_reference: Optional[str] = None
    manufacturing_processing: str = ""
    description: str = ""
    traditional_knowledge_ref: Optional[str] = None


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


class ProductRequestValidationError(ValueError):
    """Raised when a product analysis request fails validation."""


def _strip_safe(value: object) -> str:
    """Return str-stripped value; empty string if falsy."""
    return str(value).strip() if value else ""


def validate_product_request(raw: dict) -> ProductAnalysisRequest:
    """
    Validate and construct a ProductAnalysisRequest from raw input.

    Raises ProductRequestValidationError with a descriptive message on any
    validation failure.
    """
    errors: List[str] = []

    # ── Jurisdiction ──────────────────────────────────────────────────────
    jur_raw = _strip_safe(raw.get("jurisdiction") or raw.get("target_jurisdiction"))
    if not jur_raw:
        errors.append("'jurisdiction' is required.")
    elif jur_raw.lower() not in SUPPORTED_JURISDICTIONS:
        errors.append(
            f"'jurisdiction' must be one of: {sorted(SUPPORTED_JURISDICTIONS)}. Got: '{jur_raw}'."
        )

    # ── Product name ──────────────────────────────────────────────────────
    product_name = _strip_safe(raw.get("productName") or raw.get("product_name"))
    if not product_name:
        errors.append("'productName' is required.")
    elif len(product_name) > MAX_PRODUCT_NAME_LEN:
        errors.append(
            f"'productName' must not exceed {MAX_PRODUCT_NAME_LEN} characters."
        )

    # ── Product form ──────────────────────────────────────────────────────
    form_raw = _strip_safe(raw.get("form") or raw.get("product_form"))
    product_form = form_raw if form_raw else "Tablet"

    # ── Intended Use & Description ────────────────────────────────────────
    intended_use = _strip_safe(raw.get("intendedUse") or raw.get("intended_use"))
    description = _strip_safe(raw.get("description"))

    if not intended_use and not description:
        errors.append("'intended_use' (or 'description') is required.")
    elif not intended_use:
        intended_use = description
    elif not description:
        description = intended_use

    if len(intended_use) > MAX_DESCRIPTION_LEN:
        errors.append(f"'intended_use' must not exceed {MAX_DESCRIPTION_LEN} characters.")
    if len(description) > MAX_DESCRIPTION_LEN:
        errors.append(f"'description' must not exceed {MAX_DESCRIPTION_LEN} characters.")

    # ── Classification ────────────────────────────────────────────────────
    cls_raw = _strip_safe(raw.get("category") or raw.get("user_selected_classification") or raw.get("proposed_classification"))
    if not cls_raw:
        cls_raw = "other"
    elif cls_raw.lower() not in SUPPORTED_CLASSIFICATIONS:
        cls_raw = "other"

    # ── Ingredients ───────────────────────────────────────────────────────
    raw_ingredients = raw.get("ingredients")
    ingredients: List[IngredientRecord] = []
    if raw_ingredients is not None:
        if not isinstance(raw_ingredients, list):
            errors.append("'ingredients' must be a list.")
        elif len(raw_ingredients) > MAX_INGREDIENTS:
            errors.append(f"'ingredients' must not exceed {MAX_INGREDIENTS} entries.")
        else:
            for idx, ing in enumerate(raw_ingredients):
                if not isinstance(ing, dict):
                    errors.append(f"Ingredient at index {idx} must be an object.")
                    continue
                name = _strip_safe(ing.get("name"))
                if not name:
                    errors.append(f"Ingredient at index {idx} requires a non-empty 'name'.")
                    continue
                if len(name) > MAX_INGREDIENT_NAME_LEN:
                    errors.append(
                        f"Ingredient '{name[:50]}...' name exceeds {MAX_INGREDIENT_NAME_LEN} characters."
                    )
                    continue
                quantity = _strip_safe(ing.get("quantity") or "")
                if len(quantity) > MAX_INGREDIENT_QUANTITY_LEN:
                    errors.append(
                        f"Ingredient '{name}' quantity value is too long."
                    )
                    continue
                unit = _strip_safe(ing.get("unit") or "mg")
                if len(unit) > 20:
                    unit = "other"
                ingredients.append(IngredientRecord(name=name, quantity=quantity, unit=unit))


    # ── Optional classification signals ──────────────────────────────────
    product_claims = _strip_safe(raw.get("productClaims") or raw.get("product_claims"))
    disease_claim_flag = bool(raw.get("diseaseClaimFlag") or raw.get("disease_claim_flag"))
    disease_claim_text = _strip_safe(raw.get("diseaseClaimText") or raw.get("disease_claim_text"))
    
    is_classical_raw = _strip_safe(raw.get("isClassicalBasis") or raw.get("is_classical_basis")).lower()
    is_classical_basis = is_classical_raw if is_classical_raw in ("yes", "no") else "unknown"
    
    classical_reference = _strip_safe(raw.get("classicalReference") or raw.get("classical_reference") or raw.get("traditional_knowledge_ref")) or None
    manufacturing_processing = _strip_safe(raw.get("manufacturingProcessing") or raw.get("manufacturing_processing"))

    # ── Raise if any errors ───────────────────────────────────────────────
    if errors:
        raise ProductRequestValidationError(
            "Product analysis request validation failed: " + "; ".join(errors)
        )

    jurisdiction_normalised = (
        "International" if "international" in jur_raw.lower() else "India"
    )

    return ProductAnalysisRequest(
        jurisdiction=jurisdiction_normalised,
        product_name=product_name,
        product_form=product_form,
        ingredients=ingredients,
        intended_use=intended_use,
        user_selected_classification=cls_raw,
        product_claims=product_claims,
        disease_claim_flag=disease_claim_flag,
        disease_claim_text=disease_claim_text,
        is_classical_basis=is_classical_basis,
        classical_reference=classical_reference,
        manufacturing_processing=manufacturing_processing,
        description=description,
        traditional_knowledge_ref=classical_reference,
    )

