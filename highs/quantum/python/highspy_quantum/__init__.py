"""Quantum-assisted MIP heuristics for HiGHS.

Exposes the in-process API for embedding the same pipeline used by the
``highs-quantum`` CLI and by the C++ subprocess invocation.
"""
from .model import MipSubproblem, build_bqm_from_subproblem
from .protocol import PROTOCOL_VERSION, decode_input, encode_result

__all__ = [
    "MipSubproblem",
    "build_bqm_from_subproblem",
    "PROTOCOL_VERSION",
    "decode_input",
    "encode_result",
]
