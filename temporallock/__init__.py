"""TemporalLock: immutable timeslate lattice hash-chained against StaticClock.

July 2026 whitepaper (v0.1.0 receipts) plus v0.2.0 lattice extras.
Author: Aziel Eliab.

Receipts, not truth claims. Forks are welcome and always allowed.
No consensus, no mining, no tokens, no truth scores.
AZ-OS integrity log — not a kernel, not a remote shell.
"""

from __future__ import annotations

from temporallock.chain import Chain, Fork, VerifyResult, detect_forks
from temporallock.errors import (
    AppendOnlyError,
    ChainError,
    LatticeError,
    ReceiptError,
    TemporalLockError,
)
from temporallock.hashing import GENESIS_PREV_HASH, canonical_bytes, digest
from temporallock.receipt import Receipt
from temporallock.timeslate import (
    AZOS_HOST,
    HONEST_SCOPE,
    ROLE,
    STATICCLOCK_HOST,
    LatticeResult,
    bind_timeslate,
    staticclock_click_digest,
    timeslate_digest,
    verify_lattice,
)

__version__ = "0.2.0"
__author__ = "Aziel Eliab"
__all__ = [
    "AZOS_HOST",
    "AppendOnlyError",
    "Chain",
    "ChainError",
    "Fork",
    "GENESIS_PREV_HASH",
    "HONEST_SCOPE",
    "LatticeError",
    "LatticeResult",
    "ROLE",
    "Receipt",
    "ReceiptError",
    "STATICCLOCK_HOST",
    "TemporalLockError",
    "VerifyResult",
    "bind_timeslate",
    "canonical_bytes",
    "detect_forks",
    "digest",
    "staticclock_click_digest",
    "timeslate_digest",
    "verify_lattice",
    "__version__",
]
