"""Self-check for TemporalLock. No network, no telemetry.

    temporallock doctor
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Callable

from temporallock import __version__

AUTHOR = "Aziel Eliab"
Check = tuple[str, bool, str]


def _ok(name: str, detail: str = "") -> Check:
    return name, True, detail


def _fail(name: str, detail: str) -> Check:
    return name, False, detail


def _check_version() -> Check:
    if __version__:
        return _ok("version", str(__version__))
    return _fail("version", "missing")


def _check_identity() -> Check:
    try:
        mod = __import__(__name__.split(".")[0])
        author = str(getattr(mod, "__author__", AUTHOR))
    except Exception as exc:  # noqa: BLE001
        return _fail("identity", str(exc))
    blob = author + " " + AUTHOR
    forbidden = ("Col" + "lin H" + "orton", "Ja" + "ck Al" + "tman", "GodLock" + ".AZ", "Reve" + "aler")
    if any(x in blob for x in forbidden):
        return _fail("identity", "forbidden identity label")
    if "Aziel Eliab" not in blob:
        return _fail("identity", author)
    return _ok("identity", AUTHOR)



def _check_json_roundtrip() -> Check:
    from temporallock.jsonio import export_json, import_json

    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "in.json"
        out = Path(tmp) / "out.json"
        src.write_text(json.dumps({"product": "temporallock", "author": AUTHOR, "ok": True}, indent=2), encoding="utf-8")
        rec = import_json(src)
        if not rec.get("ok"):
            return _fail("import", str(rec))
        rec2 = export_json(out)
        if not rec2.get("ok") or not out.exists():
            return _fail("export", str(rec2))
        doc = json.loads(out.read_text(encoding="utf-8"))
        if doc.get("author") != AUTHOR:
            return _fail("export author", str(doc.get("author")))
        return _ok("json import/export", "roundtrip")


def _check_core_hash_stable() -> Check:
    from temporallock.hashing import digest

    known = digest(
        timestamp="2026-07-01T00:00:00Z",
        summary="same",
        evidence="uri:example",
        confidence=0.7,
        prev_hash="0" * 64,
    )
    again = digest(
        timestamp="2026-07-01T00:00:00Z",
        summary="same",
        evidence="uri:example",
        confidence=0.7,
        prev_hash="0" * 64,
    )
    if known != again or len(known) != 64:
        return _fail("v0.1.0 core hash", known)
    return _ok("v0.1.0 core hash", "stable")


def _check_lattice() -> Check:
    from temporallock.chain import Chain
    from temporallock.errors import LatticeError

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "lattice.jsonl"
        chain = Chain.genesis(
            path,
            summary="g",
            evidence="e0",
            timestamp="2026-07-01T00:00:00Z",
            click_index=0,
        )
        chain.append(
            "next",
            evidence="e1",
            timestamp="2026-07-01T00:01:00Z",
            click_index=1,
        )
        result = chain.lattice()
        if not result.ok or not result.cross_hash or result.bound != 2:
            return _fail("lattice", str(result.errors))
        try:
            chain.append(
                "rollback",
                evidence="e2",
                timestamp="2026-07-01T00:02:00Z",
                click_index=0,
            )
            return _fail("no-rollback", "decreasing click_index was accepted")
        except LatticeError:
            pass
        return _ok("timeslate lattice", f"bound={result.bound} staticclock cross-hash")


def _check_staticclock_click() -> Check:
    from temporallock.timeslate import staticclock_click_digest

    a = staticclock_click_digest({"kind": "gear-click", "timestamp": "2026-07-01T00:00:00Z", "click_index": 0})
    b = staticclock_click_digest({"kind": "gear-click", "timestamp": "2026-07-01T00:00:00Z", "click_index": 0})
    if a != b or len(a) != 64:
        return _fail("staticclock click", a)
    return _ok("staticclock click", "local digest")


CHECKS: tuple[Callable[[], Check], ...] = (
    _check_version,
    _check_identity,
    _check_json_roundtrip,
    _check_core_hash_stable,
    _check_lattice,
    _check_staticclock_click,
)


def run_doctor(*, as_json: bool = False) -> int:
    results = []
    failed = 0
    for fn in CHECKS:
        name, ok, detail = fn()
        results.append({"name": name, "ok": ok, "detail": detail})
        if not ok:
            failed += 1
        mark = "ok" if ok else "FAIL"
        if not as_json:
            print(f"[{mark}] {name}" + (f" — {detail}" if detail else ""))
    payload = {
        "ok": failed == 0,
        "failed": failed,
        "checks": results,
        "version": __version__,
        "author": AUTHOR,
        "role": "immutable timeslate lattice",
        "network": False,
        "telemetry": False,
    }
    if as_json:
        print(json.dumps(payload, indent=2))
    else:
        print("doctor", "passed" if failed == 0 else "failed")
    return 0 if failed == 0 else 1
