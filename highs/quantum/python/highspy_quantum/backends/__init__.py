"""Backend registry for ``highs-quantum``.

Each backend implements :class:`Backend` from :mod:`.base`. We import the
classical / exact backends eagerly (no optional deps); vendor backends are
loaded lazily so the package works without their SDKs installed.
"""
from __future__ import annotations

from .base import Backend, BackendUnavailable, Sample
from .classical import ClassicalBackend
from .exact import ExactBackend

_REGISTRY = {
    "classical": ClassicalBackend,
    "exact": ExactBackend,
}


def get_backend(name: str) -> Backend:
    if name in _REGISTRY:
        return _REGISTRY[name]()
    # Vendor backends are lazy-loaded so missing SDKs don't break import.
    if name == "dwave":
        from .dwave import DWaveBackend  # type: ignore

        return DWaveBackend()
    if name == "qiskit":
        from .qiskit import QiskitBackend  # type: ignore

        return QiskitBackend()
    if name == "rigetti":
        from .rigetti import RigettiBackend  # type: ignore

        return RigettiBackend()
    if name == "braket":
        from .braket import BraketBackend  # type: ignore

        return BraketBackend()
    raise BackendUnavailable(f"unknown backend: {name!r}")


__all__ = [
    "Backend",
    "BackendUnavailable",
    "Sample",
    "get_backend",
]
