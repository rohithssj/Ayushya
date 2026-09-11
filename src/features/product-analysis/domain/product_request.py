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
        "ayurveda-aahar",
        "proprietary asu medicine",
        "classical formulation",
        "phytopharmaceutical",
        "ayurvedic cosmetic",
        "nutraceutical",
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

    Fields:
      jurisdiction               — 'India' or 'International'
      product_name               — product name (required)
      product_form               — dosage form (tablet, capsule, etc.)
      user_selected_classification — the user's stated target classification
                                    (treated as preliminary, not legally verified)
      description                — product description + processing method
      ingredients                — list of IngredientRecord
      traditional_knowledge_ref  — optional: classical reference / textual basis
                                   (not in current UI, supported for future use)
    """

    jurisdiction: str                        # normalised to lowercase
    product_name: str
    product_form: str
    user_selected_classification: str
    description: str
    ingredients: List[IngredientRecord]
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

    Does NOT fabricate or infer legal conclusions from the supplied data.
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
    product_form = form_raw if form_raw else "tablet"

    # ── Classification ────────────────────────────────────────────────────
    cls_raw = _strip_safe(raw.get("category") or raw.get("user_selected_classification"))
    if not cls_raw:
        # Default to 'other' if not provided — not an error
        cls_raw = "other"
    if cls_raw.lower() not in SUPPORTED_CLASSIFICATIONS:
        # Accept unknown classification as 'other' — do not block
        cls_raw = "other"

    # ── Description ───────────────────────────────────────────────────────
    description = _strip_safe(raw.get("description"))
    if not description:
        errors.append("'description' is required.")
    elif len(description) > MAX_DESCRIPTION_LEN:
        errors.append(
            f"'description' must not exceed {MAX_DESCRIPTION_LEN} characters."
        )

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

    # ── Traditional knowledge reference (optional) ─────────────────────────
    tk_ref_raw = _strip_safe(raw.get("traditional_knowledge_ref") or "")
    traditional_knowledge_ref: Optional[str] = None
    if tk_ref_raw:
        if len(tk_ref_raw) > MAX_TK_REF_LEN:
            errors.append(
                f"'traditional_knowledge_ref' must not exceed {MAX_TK_REF_LEN} characters."
            )
        else:
            traditional_knowledge_ref = tk_ref_raw

    # ── Raise if any errors ───────────────────────────────────────────────
    if errors:
        raise ProductRequestValidationError(
            "Product analysis request validation failed: " + "; ".join(errors)
        )

    # Normalise jurisdiction to Title Case for internal use and RAG chunk metadata matching
    jurisdiction_normalised = (
        "International" if "international" in jur_raw.lower() else "India"
    )

    return ProductAnalysisRequest(
        jurisdiction=jurisdiction_normalised,
        product_name=product_name,
        product_form=product_form,
        user_selected_classification=cls_raw,
        description=description,
        ingredients=ingredients,
        traditional_knowledge_ref=traditional_knowledge_ref,
    )
