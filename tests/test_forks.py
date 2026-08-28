"""Forks are allowed and detectable. No winner is chosen."""

from __future__ import annotations

from pathlib import Path

from temporallock.chain import Chain, detect_forks
from temporallock.receipt import Receipt


def test_two_children_of_same_prev_hash_detected_as_fork(tmp_path: Path) -> None:
    parent = Receipt.create(
        summary="parent",
        evidence="root evidence",
        confidence=1.0,
        timestamp="2026-07-01T00:00:00Z",
    )
    left = Receipt.create(
        summary="left branch",
        evidence="left evidence",
        confidence=0.6,
        timestamp="2026-07-01T00:01:00Z",
        prev_hash=parent.hash,
    )
    right = Receipt.create(
        summary="right branch",
        evidence="right evidence",
        confidence=0.4,
        timestamp="2026-07-01T00:02:00Z",
        prev_hash=parent.hash,
    )
    assert left.hash != right.hash
    assert left.prev_hash == right.prev_hash == parent.hash

    forks = detect_forks([parent, left, right])
    assert len(forks) == 1
    assert forks[0].prev_hash == parent.hash
    assert set(forks[0].child_hashes) == {left.hash, right.hash}

    # Both chains still internally verifiable if stored separately.
    p_left = tmp_path / "left.jsonl"
    p_right = tmp_path / "right.jsonl"
    chain_left = Chain.genesis(
        p_left,
        summary=parent.summary,
        evidence=parent.evidence,
        confidence=parent.confidence,
        timestamp=parent.timestamp,
    )
    # genesis hash must match parent (same fields)
    assert chain_left[0].hash == parent.hash
    chain_left.append(
        summary=left.summary,
        evidence=left.evidence,
        confidence=left.confidence,
        timestamp=left.timestamp,
    )
    assert chain_left[-1].hash == left.hash
    assert chain_left.verify().ok

    chain_right = Chain.genesis(
        p_right,
        summary=parent.summary,
        evidence=parent.evidence,
        confidence=parent.confidence,
        timestamp=parent.timestamp,
    )
    chain_right.append(
        summary=right.summary,
        evidence=right.evidence,
        confidence=right.confidence,
        timestamp=right.timestamp,
    )
    assert chain_right[-1].hash == right.hash
    assert chain_right.verify().ok

    # Combined view still reports the fork and does not pick a winner.
    combined = detect_forks(list(chain_left) + [chain_right[-1]])
    assert len(combined) == 1
    assert set(combined[0].child_hashes) == {left.hash, right.hash}


def test_linear_chain_has_no_forks(tmp_path: Path) -> None:
    chain = Chain.genesis(tmp_path / "c.jsonl", summary="a", evidence="e")
    chain.append("b", evidence="e2")
    chain.append("c", evidence="e3")
    assert chain.forks() == []
    assert chain.verify().ok
