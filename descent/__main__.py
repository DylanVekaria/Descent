"""Entry point for ``python -m descent``."""
from __future__ import annotations

from . import main


def run() -> None:
    """Execute the game using the compatibility shim."""
    main()


if __name__ == "__main__":
    run()
