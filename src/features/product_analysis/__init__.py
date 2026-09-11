"""
Python package shim — makes src.features.product_analysis importable.

The actual Python source lives in src/features/product-analysis/ (hyphenated,
following Next.js feature directory conventions). Python cannot resolve a
hyphenated directory name as a package identifier.

This shim sets __path__ to redirect all sub-package resolution to the real
source directory, making imports like:

    from src.features.product_analysis.domain.product_request import ...

work correctly without renaming the feature directory or requiring PYTHONPATH.

No logic lives here. All logic is in src/features/product-analysis/.
"""
import os as _os

__path__ = [
    _os.path.join(
        _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))),
        "product-analysis",
    )
]
