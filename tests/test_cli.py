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

    rc = main(["verify", str(path), "--json"])
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
    rc = main(["verify", str(path), "--json"])
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


def test_help_lists_ui_and_version() -> None:
    from temporallock.cli import _build_parser

    text = _build_parser().format_help()
    assert "ui" in text
    assert "version" in text
    assert "gate" in text
    assert "lattice" in text
    assert "timeslate" in text
    assert "click" in text
    assert "127.0.0.1:8766" in text or "temporallock ui" in text


def test_cli_gate_hashes_and_accepts(tmp_path: Path, capsys) -> None:
    target = tmp_path / "note.txt"
    target.write_text("observed sky\n", encoding="utf-8")
    rc = main(["gate", str(target)])
    out = capsys.readouterr().out
    assert rc == 0
    assert "accepted" in out
    assert "file_sha256=" in out
    chain = Path(str(target) + ".receipts.jsonl")
    assert chain.is_file()

    rc = main(["gate", str(target), "--json"])
    payload = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert payload["ok"] is True
    assert payload["accepted"] is True
    assert payload["length"] == 2
    assert payload["file_sha256"]
    assert payload["action"] == "appended"


def test_cli_lattice_and_timeslate(tmp_path: Path, capsys) -> None:
    path = tmp_path / "notes.jsonl"
    rc = main(
        [
            "timeslate",
            "--chain",
            str(path),
            "--summary",
            "hook",
            "--evidence",
            "azos:prefab",
            "--timestamp",
            "2026-07-12T14:30:00Z",
            "--click-index",
            "0",
        ]
    )
    assert rc == 0
    out = capsys.readouterr().out
    assert "genesis" in out
    assert "timeslate" in out
    rc = main(["lattice", str(path), "--json"])
    payload = __import__("json").loads(capsys.readouterr().out)
    assert rc == 0
    assert payload["ok"] is True
    assert payload["cross_hash"] is True
    assert payload["bound"] == 1


def test_cli_click(capsys) -> None:
    rc = main(["click", "--json", "--timestamp", "2026-07-12T14:30:00Z", "--click-index", "0"])
    assert rc == 0
    payload = __import__("json").loads(capsys.readouterr().out)
    assert payload["staticclock_click"]
    assert len(payload["staticclock_click"]) == 64
    assert payload["author"] == "Aziel Eliab"


def test_cli_doctor(capsys) -> None:
    rc = main(["doctor", "--json"])
    payload = __import__("json").loads(capsys.readouterr().out)
    assert rc == 0
    assert payload["ok"] is True
    assert payload["author"] == "Aziel Eliab"
    assert payload["role"] == "immutable timeslate lattice"


def test_cli_gate_missing_file(tmp_path: Path, capsys) -> None:
    rc = main(["gate", str(tmp_path / "nope.bin")])
    assert rc != 0
    err = capsys.readouterr().err
    assert "not found" in err.lower()
    assert "next:" in err.lower()


def test_cli_welcome_and_help(capsys) -> None:
    assert main([]) == 0
    welcome = capsys.readouterr().out
    assert "temporallock ui" in welcome
    assert "Aziel Eliab" in welcome
    assert "arguments are required" not in welcome.lower()

    assert main(["--help"]) == 0
    help_text = capsys.readouterr().out
    assert "commands:" in help_text
    assert "advanced:" in help_text
    assert "examples:" in help_text
    assert "changelog" not in help_text.lower()


def test_cli_unknown_command(capsys) -> None:
    assert main(["bogus"]) == 2
    err = capsys.readouterr().err
    assert 'Unknown command "bogus"' in err
    assert "temporallock --help" in err


def test_cli_missing_genesis_args(capsys) -> None:
    assert main(["genesis"]) == 2
    err = capsys.readouterr().err
    assert "--chain" in err
    assert "Try:" in err


def test_cli_verify_human_default(tmp_path: Path, capsys) -> None:
    path = tmp_path / "notes.jsonl"
    assert main(["genesis", "--chain", str(path), "--summary", "s", "--evidence", "e"]) == 0
    capsys.readouterr()
    assert main(["verify", str(path)]) == 0
    out = capsys.readouterr().out
    assert "Chain intact" in out
    assert not out.lstrip().startswith("{")


def test_cli_click_human_default(capsys) -> None:
    assert main(["click", "--timestamp", "2026-07-12T14:30:00Z", "--click-index", "0"]) == 0
    out = capsys.readouterr().out
    assert "staticclock_click=" in out
    assert "Aziel Eliab" in out
    assert not out.lstrip().startswith("{")
