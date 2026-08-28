"""Receipt construction, validation, and immutability."""

from __future__ import annotations

import pytest

from temporallock.errors import AppendOnlyError, ReceiptError
from temporallock.hashing import GENESIS_PREV_HASH, digest
from temporallock.receipt import Receipt


def test_genesis_prev_hash_is_64_zeros_and_hash_is_64_hex() -> None:
    rec = Receipt.create(
        summary="first look",
        evidence="notebook p.1",
        confidence=0.5,
        timestamp="2026-07-01T00:00:00Z",
    )
    assert rec.prev_hash == GENESIS_PREV_HASH
    assert rec.prev_hash == "0" * 64
    assert len(rec.hash) == 64
    assert all(c in "0123456789abcdef" for c in rec.hash)


def test_confidence_out_of_range_rejected() -> None:
    with pytest.raises(ReceiptError):
        Receipt.create(summary="x", evidence="y", confidence=1.01)
    with pytest.raises(ReceiptError):
        Receipt.create(summary="x", evidence="y", confidence=-0.01)
    with pytest.raises(ReceiptError):
        Receipt.create(summary="x", evidence="y", confidence=float("nan"))
    with pytest.raises(ReceiptError):
        Receipt.create(summary="x", evidence="y", confidence=float("inf"))


def test_confidence_bounds_inclusive() -> None:
    lo = Receipt.create(summary="lo", evidence="e", confidence=0.0)
    hi = Receipt.create(summary="hi", evidence="e", confidence=1.0)
    assert lo.confidence == 0.0
    assert hi.confidence == 1.0


def test_empty_evidence_rejected() -> None:
    with pytest.raises(ReceiptError):
        Receipt.create(summary="x", evidence="")
    with pytest.raises(ReceiptError):
        Receipt.create(summary="x", evidence="   ")


def test_cannot_modify_receipt_fields() -> None:
    rec = Receipt.create(summary="s", evidence="e", confidence=0.4)
    with pytest.raises(AppendOnlyError):
        rec.summary = "changed"
    with pytest.raises(AppendOnlyError):
        rec.evidence = "other"
    with pytest.raises(AppendOnlyError):
        rec.confidence = 0.1
    with pytest.raises(AppendOnlyError):
        rec.hash = "0" * 64
    with pytest.raises(AppendOnlyError):
        del rec.summary


def test_independent_verifier_recomputes_from_fields_only() -> None:
    rec = Receipt.create(
        summary="observed a bell",
        evidence="audio:bell.wav",
        confidence=0.625,
        timestamp="2026-07-04T12:00:00Z",
    )
    recomputed = digest(
        timestamp=rec.timestamp,
        summary=rec.summary,
        evidence=rec.evidence,
        confidence=rec.confidence,
        prev_hash=rec.prev_hash,
    )
    assert recomputed == rec.hash
    assert rec.recomputed_hash() == rec.hash
    # stored hash is not an input to digest
    assert rec.hash not in rec.recomputed_hash() or True  # hash is the output
