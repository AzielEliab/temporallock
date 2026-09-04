"""Local UI: loopback only, GET / contains TemporalLock. Port 8766."""

from __future__ import annotations

import json
import threading
import urllib.request

import pytest

from temporallock.cli import _build_parser
from temporallock.ui import DEFAULT_HOST, DEFAULT_PORT, LOOPBACK, make_server


def test_cli_ui_defaults() -> None:
    args = _build_parser().parse_args(["ui"])
    assert args.host == "127.0.0.1"
    assert args.host == DEFAULT_HOST
    assert args.port == 8766
    assert args.port == DEFAULT_PORT


def test_ui_rejects_non_loopback() -> None:
    with pytest.raises(ValueError, match="loopback"):
        make_server("0.0.0.0", 9)
    assert "127.0.0.1" in LOOPBACK


def test_ui_get_root_200_contains_temporallock() -> None:
    httpd = make_server("127.0.0.1", 0)
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=5) as resp:
            assert resp.status == 200
            html = resp.read()
        assert b"TemporalLock" in html
        assert b"receipts" in html.lower()
        assert b"timeslate" in html.lower()
        assert b"StaticClock" in html
        assert b"127.0.0.1" in html
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=5) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        assert payload["ok"] is True
        assert payload["bind_host"] == "127.0.0.1"
        assert payload["author"] == "Aziel Eliab"
        assert payload["role"] == "immutable timeslate lattice"
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/api/genesis",
            data=json.dumps({"summary": "desk", "evidence": "log", "confidence": 1.0, "click_index": 0}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            minted = json.loads(resp.read().decode("utf-8"))
        assert minted["receipts"]
        assert minted["receipts"][0]["timeslate_hash"]
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/api/lattice",
            data=b"{}",
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            lat = json.loads(resp.read().decode("utf-8"))
        assert lat["lattice"]["ok"] is True
        assert lat["lattice"]["cross_hash"] is True
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=2)
