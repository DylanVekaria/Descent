"""Compatibility shim for running Descent as a module."""
from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path

_pkg_dir = Path(__file__).resolve().parent
_src_pkg = _pkg_dir.parent / "src" / "descent"

# Ensure Python can discover the real package that lives under src/.
if _src_pkg.exists():
    # Prepend the src directory (the package parent) so imports discover it first.
    src_parent = str(_src_pkg.parent)
    if src_parent not in sys.path:
        sys.path.insert(0, src_parent)

# Mirror the src-based package on our package path so that submodule lookups resolve.
__path__ = [str(_pkg_dir)]
if _src_pkg.exists():
    __path__.append(str(_src_pkg))

# Import the actual public interface from the implementation package.
_impl = import_module("descent.main")
main = _impl.main
__all__ = ["main"]
