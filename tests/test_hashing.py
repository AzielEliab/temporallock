"""Canonical encoding stability."""

from __future__ import annotations

from temporallock.hashing import canonical_bytes, digest
from temporallock.receipt import Receipt


def test_canonical_encoding_stable_same_fields_same_hash() -> None:
    kwargs = dict(
        timestamp="2026-07-01T00:00:00Z",
        summary="same",
        evidence="uri:example",
        confidence=0.7,
        prev_hash="0" * 64,
    )
    a = canonical_bytes(**kwargs)
    b = canonical_bytes(**kwargs)
    assert a == b
    assert digest(**kwargs) == digest(**kwargs)
    rec1 = Receipt.create(
        summary=kwargs["summary"],
        evidence=kwargs["evidence"],
        confidence=kwargs["confidence"],
        timestamp=kwargs["timestamp"],
        prev_hash=kwargs["prev_hash"],
    )
    rec2 = Receipt.create(
        summary=kwargs["summary"],
        evidence=kwargs["evidence"],
        confidence=kwargs["confidence"],
        timestamp=kwargs["timestamp"],
        prev_hash=kwargs["prev_hash"],
    )
    assert rec1.hash == rec2.hash


def test_canonical_confidence_six_decimal_places() -> None:
    raw = canonical_bytes(
        timestamp="2026-07-01T00:00:00Z",
        summary="s",
        evidence="e",
        confidence=0.7,
        prev_hash="0" * 64,
    )
    text = raw.decode("utf-8")
    assert "0.700000" in text
    assert '"0.700000"' not in text  # JSON number, not a string
    # sorted keys, no extra whitespace
    assert text.startswith("{")
    assert ": " not in text
    assert ", " not in text


def test_canonical_excludes_hash_field() -> None:
    raw = canonical_bytes(
        timestamp="2026-07-01T00:00:00Z",
        summary="s",
        evidence="e",
        confidence=1.0,
        prev_hash="0" * 64,
    ).decode("utf-8")
    assert "hash" not in raw or '"hash"' not in raw
