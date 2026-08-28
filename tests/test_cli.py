"""CLI: version, genesis, append, verify, show."""

from __future__ import annotations

import json
from pathlib import Path

from temporallock import __version__
from temporallock.cli import main
from temporallock.chain import Chain


def test_cli_version(capsys) -> None:
    assert main(["version"]) == 0
    assert capsys.readouterr().out.strip() == f"temporallock {__version__}"


def test_cli_genesis_append_verify(tmp_path: Path, capsys) -> None:
    path = tmp_path / "notes.jsonl"
    rc = main(
        [
            "genesis",
            "--chain",
            str(path),
            "--summary",
            "sky overcast",
            "--evidence",
            "photo:sky.jpg",
            "--confidence",
            "0.9",
            "--timestamp",
            "2026-07-12T14:30:00Z",
        ]
    )
    assert rc == 0
    out = capsys.readouterr().out
    assert "genesis" in out
    assert path.is_file()

    rc = main(
        [
            "append",
            "--chain",
            str(path),
            "--summary",
            "rain began",
            "--evidence",
            "https://example.invalid/log",
            "--confidence",
            "0.7",
            "--timestamp",
            "2026-07-12T14:46:00Z",
        ]
    )
    assert rc == 0
    out = capsys.readouterr().out
    assert "appended" in out

    rc = main(["verify", str(path)])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["length"] == 2
    assert payload["first_hash"]
    assert payload["last_hash"]
    assert payload["errors"] == []

    chain = Chain.load(path)
    assert chain[1].prev_hash == chain[0].hash


def test_cli_append_requires_existing_chain(tmp_path: Path, capsys) -> None:
    path = tmp_path / "missing.jsonl"
    rc = main(
        [
            "append",
            "--chain",
            str(path),
            "--summary",
            "nope",
            "--evidence",
            "e",
        ]
    )
    assert rc != 0
    err = capsys.readouterr().err
    assert "genesis" in err.lower() or "not exist" in err.lower()
    assert not path.exists()


def test_cli_verify_detects_break(tmp_path: Path, capsys) -> None:
    path = tmp_path / "notes.jsonl"
    assert main(["genesis", "--chain", str(path), "--summary", "s", "--evidence", "e"]) == 0
    capsys.readouterr()
    text = path.read_text(encoding="utf-8")
    obj = json.loads(text)
    obj["summary"] = "broken"
    path.write_text(json.dumps(obj) + "\n", encoding="utf-8")
    rc = main(["verify", str(path)])
    assert rc != 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is False
    assert payload["errors"]


def test_cli_show(tmp_path: Path, capsys) -> None:
    path = tmp_path / "notes.jsonl"
    assert main(["genesis", "--chain", str(path), "--summary", "hello", "--evidence", "e"]) == 0
    capsys.readouterr()
    rc = main(["show", str(path)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "hello" in out
    assert "n=1" in out


def test_cli_genesis_refuses_existing(tmp_path: Path, capsys) -> None:
    path = tmp_path / "notes.jsonl"
    assert main(["genesis", "--chain", str(path), "--summary", "s", "--evidence", "e"]) == 0
    capsys.readouterr()
    rc = main(["genesis", "--chain", str(path), "--summary", "s2", "--evidence", "e2"])
    assert rc != 0
    capsys.readouterr()
