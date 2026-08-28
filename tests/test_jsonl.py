"""JSONL is append-only: earlier lines are never rewritten."""

from __future__ import annotations

from pathlib import Path

from temporallock.chain import Chain


def test_jsonl_append_does_not_rewrite_earlier_lines(tmp_path: Path) -> None:
    path = tmp_path / "c.jsonl"
    chain = Chain.genesis(
        path,
        summary="first line must stay",
        evidence="body-0",
        confidence=0.5,
        timestamp="2026-07-01T00:00:00Z",
    )
    before = path.read_bytes()
    first_line = before.split(b"\n")[0]
    assert first_line  # non-empty

    chain.append(
        summary="second",
        evidence="body-1",
        confidence=0.6,
        timestamp="2026-07-01T00:01:00Z",
    )
    after = path.read_bytes()
    assert after.startswith(first_line + b"\n")
    # first line bytes identical, not just parsed equal
    assert after.split(b"\n")[0] == first_line
    assert after != before
    assert after.count(b"\n") >= 2


def test_jsonl_roundtrip_load(tmp_path: Path) -> None:
    path = tmp_path / "c.jsonl"
    chain = Chain.genesis(path, summary="a", evidence="e", confidence=0.25)
    chain.append("b", evidence="e2", confidence=0.5)
    loaded = Chain.load(path)
    assert len(loaded) == 2
    assert loaded[0].hash == chain[0].hash
    assert loaded[1].hash == chain[1].hash
    assert loaded.verify().ok
