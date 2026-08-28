"""Chain linking, verify, append-only, corrections."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from temporallock.chain import Chain
from temporallock.errors import AppendOnlyError, ChainError, ReceiptError
from temporallock.hashing import GENESIS_PREV_HASH
from temporallock.receipt import Receipt


def _genesis(path: Path) -> Chain:
    return Chain.genesis(
        path,
        summary="g",
        evidence="e0",
        confidence=1.0,
        timestamp="2026-07-01T00:00:00Z",
    )


def test_second_receipt_prev_hash_equals_first_hash(tmp_path: Path) -> None:
    chain = _genesis(tmp_path / "c.jsonl")
    first = chain[0]
    second = chain.append("next", evidence="e1", confidence=0.5, timestamp="2026-07-01T00:01:00Z")
    assert second.prev_hash == first.hash
    assert first.prev_hash == GENESIS_PREV_HASH
    assert chain.verify().ok


def test_tampering_summary_without_rehash_fails_verify(tmp_path: Path) -> None:
    path = tmp_path / "c.jsonl"
    chain = _genesis(path)
    chain.append("two", evidence="e1", timestamp="2026-07-01T00:01:00Z")
    lines = path.read_text(encoding="utf-8").splitlines()
    obj = json.loads(lines[0])
    obj["summary"] = "TAMPERED"
    lines[0] = json.dumps(obj, separators=(",", ":"))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    loaded = Chain.load(path)
    result = loaded.verify()
    assert not result.ok
    assert result.errors


def test_tampering_middle_prev_hash_fails_verify(tmp_path: Path) -> None:
    path = tmp_path / "c.jsonl"
    chain = _genesis(path)
    chain.append("two", evidence="e1", timestamp="2026-07-01T00:01:00Z")
    chain.append("three", evidence="e2", timestamp="2026-07-01T00:02:00Z")
    lines = path.read_text(encoding="utf-8").splitlines()
    obj = json.loads(lines[1])
    obj["prev_hash"] = "ab" * 32
    lines[1] = json.dumps(obj, separators=(",", ":"))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    loaded = Chain.load(path)
    result = loaded.verify()
    assert not result.ok
    assert any("prev_hash" in e or "hash" in e for e in result.errors)


def test_cannot_modify_or_delete_chain(tmp_path: Path) -> None:
    chain = _genesis(tmp_path / "c.jsonl")
    chain.append("two", evidence="e1")
    with pytest.raises(AppendOnlyError):
        chain.pop()
    with pytest.raises(AppendOnlyError):
        chain.clear()
    with pytest.raises(AppendOnlyError):
        chain.remove(chain[0])
    with pytest.raises(AppendOnlyError):
        chain.insert(0, chain[0])
    with pytest.raises(AppendOnlyError):
        chain[0] = chain[0]
    with pytest.raises(AppendOnlyError):
        del chain[0]
    with pytest.raises(AppendOnlyError):
        chain.reverse()


def test_correction_is_new_receipt_old_still_verifies(tmp_path: Path) -> None:
    path = tmp_path / "c.jsonl"
    chain = _genesis(path)
    original = chain[0]
    original_hash = original.hash
    original_summary = original.summary
    chain.append(
        summary=f"re: {original.hash} the count was 3 not 2",
        evidence="recount of the same notebook page",
        confidence=0.8,
    )
    assert original.hash == original_hash
    assert original.summary == original_summary
    assert len(chain) == 2
    assert chain[1].prev_hash == original.hash
    assert "re:" in chain[1].summary
    assert chain.verify().ok
    reloaded = Chain.load(path)
    assert reloaded.verify().ok
    assert reloaded[0].hash == original_hash


def test_genesis_on_existing_file_raises(tmp_path: Path) -> None:
    path = tmp_path / "c.jsonl"
    _genesis(path)
    with pytest.raises(ChainError):
        Chain.genesis(path, summary="again", evidence="nope")


def test_append_require_existing_on_empty_raises(tmp_path: Path) -> None:
    chain = Chain((), path=tmp_path / "missing.jsonl")
    with pytest.raises(ChainError):
        chain.append("s", evidence="e", require_existing=True)
