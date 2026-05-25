"""Module entry point so the C++ side can invoke us with ``python -m highspy_quantum``."""
from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
