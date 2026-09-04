"""Timeslate lattice: StaticClock cross-hash, no rollbacks, core hash stable."""

from __future__ import annotations

from pathlib import Path

import pytest

from temporallock.chain import Chain
from temporallock.errors import LatticeError
from temporallock.hashing import digest
from temporallock.receipt import Receipt
from temporallock.timeslate import (
    STATICCLOCK_HOST,
    bind_timeslate,
    staticclock_click_digest,
    timeslate_digest,
    verify_lattice,
)


def test_core_hash_ignores_timeslate_extras() -> None:
    rec = Receipt.create(
        summary="same",
        evidence="uri:example",
        confidence=0.7,
        timestamp="2026-07-01T00:00:00Z",
    )
    bound = bind_timeslate(rec, prev=None, click_index=0)
    assert bound.hash == rec.hash
    assert bound.hash == digest(
        timestamp="2026-07-01T00:00:00Z",
        summary="same",
        evidence="uri:example",
        confidence=0.7,
        prev_hash="0" * 64,
    )
    assert bound.timeslate_hash
    assert bound.staticclock_click
    assert len(bound.timeslate_hash) == 64


def test_staticclock_click_digest_stable_and_forces_product() -> None:
    a = staticclock_click_digest({"kind": "gear-click", "timestamp": "2026-07-01T00:00:00Z", "click_index": 0})
    b = staticclock_click_digest({"kind": "gear-click", "timestamp": "2026-07-01T00:00:00Z", "click_index": 0})
    assert a == b
    assert len(a) == 64
    other = staticclock_click_digest({"kind": "gear-click", "timestamp": "2026-07-01T00:00:01Z", "click_index": 0})
    assert other != a


def test_genesis_append_lattice_ok(tmp_path: Path) -> None:
    chain = Chain.genesis(
        tmp_path / "c.jsonl",
        summary="g",
        evidence="e0",
        timestamp="2026-07-01T00:00:00Z",
        click_index=0,
    )
    second = chain.append("next", evidence="e1", timestamp="2026-07-01T00:01:00Z", click_index=1)
    assert chain[0].timeslate_hash
    assert second.prev_timeslate_hash == chain[0].timeslate_hash
    result = chain.lattice()
    assert result.ok
    assert result.cross_hash
    assert result.bound == 2
    assert result.last_click_index == 1
    assert result.staticclock == STATICCLOCK_HOST
    assert chain.verify().ok


def test_rollback_click_index_refused(tmp_path: Path) -> None:
    chain = Chain.genesis(
        tmp_path / "c.jsonl",
        summary="g",
        evidence="e0",
        timestamp="2026-07-01T00:00:00Z",
        click_index=3,
    )
    with pytest.raises(LatticeError, match="rollback"):
        chain.append("back", evidence="e1", click_index=2)


def test_same_click_index_is_allowed_fork(tmp_path: Path) -> None:
    chain = Chain.genesis(
        tmp_path / "c.jsonl",
        summary="g",
        evidence="e0",
        timestamp="2026-07-01T00:00:00Z",
        click_index=1,
    )
    rec = chain.append("same click", evidence="e1", click_index=1)
    assert rec.click_index == 1
    assert chain.lattice().ok


def test_legacy_receipt_only_chain_still_verifies(tmp_path: Path) -> None:
    rec = Receipt.create(
        summary="legacy",
        evidence="e",
        timestamp="2026-07-01T00:00:00Z",
    )
    path = tmp_path / "legacy.jsonl"
    path.write_text(
        '{"confidence":1.0,"evidence":"e","hash":"%s","prev_hash":"%s","summary":"legacy","timestamp":"2026-07-01T00:00:00Z"}\n'
        % (rec.hash, rec.prev_hash),
        encoding="utf-8",
    )
    loaded = Chain.load(path)
    assert loaded.verify().ok
    lattice = loaded.lattice()
    assert lattice.ok
    assert lattice.cross_hash is False
    assert lattice.bound == 0


def test_timeslate_digest_recompute() -> None:
    rec = Receipt.create(summary="s", evidence="e", timestamp="2026-07-01T00:00:00Z")
    bound = bind_timeslate(rec, prev=None, click_index=0)
    assert timeslate_digest(
        bound.hash,
        bound.staticclock_click,
        bound.prev_timeslate_hash,
        bound.click_index,
    ) == bound.timeslate_hash


def test_tampered_timeslate_fails_lattice(tmp_path: Path) -> None:
    path = tmp_path / "c.jsonl"
    chain = Chain.genesis(path, summary="g", evidence="e0", timestamp="2026-07-01T00:00:00Z")
    text = path.read_text(encoding="utf-8")
    obj = __import__("json").loads(text)
    obj["timeslate_hash"] = "ab" * 32
    path.write_text(__import__("json").dumps(obj) + "\n", encoding="utf-8")
    loaded = Chain.load(path)
    result = loaded.lattice()
    assert not result.ok
    assert any("timeslate_hash" in e for e in result.errors)
    # core receipt hash still matches
    assert loaded.verify().ok


def test_verify_lattice_helper_empty() -> None:
    result = verify_lattice([])
    assert result.ok
    assert result.bound == 0
