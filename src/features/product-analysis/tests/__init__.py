# Product Analysis — Tests Package
#
# sys.path fixup: when unittest discover is run from this directory
# (without -t specifying the project root), absolute imports such as
#   from src.features.product_analysis.domain.xxx import ...
# require the project root (D:\Ayushya) to be on sys.path.
# We compute it relative to this file so no PYTHONPATH env var is needed.
import sys as _sys, os as _os

_ROOT = _os.path.dirname(  # src/
    _os.path.dirname(       # features/
        _os.path.dirname(   # product-analysis/
            _os.path.dirname(  # tests/
                _os.path.abspath(__file__)
            )
        )
    )
)
if _ROOT not in _sys.path:
    _sys.path.insert(0, _ROOT)
