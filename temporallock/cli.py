"""Command-line interface for TemporalLock.

    temporallock ui [--host 127.0.0.1] [--port 8766]
    temporallock version
    temporallock gate FILE [--chain FILE.jsonl]
    temporallock genesis --chain FILE.jsonl --summary "..." --evidence "..."
    temporallock append  --chain FILE.jsonl --summary "..." --evidence "..." [--confidence 0.7] [--timestamp ISO]
    temporallock timeslate --chain FILE.jsonl --summary "..." --evidence "..."
    temporallock lattice FILE.jsonl
    temporallock click [--timestamp ISO]
    temporallock verify FILE.jsonl
    temporallock show FILE.jsonl

Immutable timeslate lattice, hash-chained against StaticClock.
Receipts, not truth claims. Forks always allowed. No rollbacks.
``gate FILE`` hashes the file and appends a timeslate before treating it
as accepted (genesis if the chain is new, else append, then lattice).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Sequence

from temporallock import __version__
from temporallock.chain import Chain
from temporallock.errors import AppendOnlyError, ChainError, LatticeError, ReceiptError, TemporalLockError
from temporallock.timeslate import HONEST_SCOPE, ROLE, STATICCLOCK_HOST, staticclock_click_digest


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="temporallock",
        description=(
            "TemporalLock — immutable timeslate lattice hash-chained against "
            "StaticClock (Aziel Eliab). AZ-OS integrity log. Receipts, not "
            "truth claims. Local UI: `temporallock ui` at http://127.0.0.1:8766."
        ),
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("version", help="Print package version.")

    p_ui = sub.add_parser("ui", help="Run the localhost UI (127.0.0.1:8766).")
    p_ui.add_argument("--host", default="127.0.0.1", help="Bind host (default 127.0.0.1).")
    p_ui.add_argument("--port", type=int, default=8766, help="Bind port (default 8766).")

    p_gen = sub.add_parser("genesis", help="Write the first receipt (prev_hash = 64 zeros).")
    p_gen.add_argument("--chain", required=True, help="JSONL chain path (must not already exist).")
    p_gen.add_argument("--summary", required=True, help="Brief summary of what was observed.")
    p_gen.add_argument("--evidence", required=True, help="Supporting evidence (body and/or URI/path).")
    p_gen.add_argument("--confidence", type=float, default=1.0, help="Observer confidence in [0.0, 1.0] (default 1.0).")
    p_gen.add_argument("--timestamp", default=None, help="UTC ISO-8601 timestamp (default: now).")
    p_gen.add_argument("--click", default=None, help="StaticClock gear-click hex (64). Default: derived locally.")
    p_gen.add_argument("--click-index", type=int, default=None, dest="click_index", help="Monotonic StaticClock click index.")

    p_app = sub.add_parser("append", help="Append a timeslate to an existing lattice.")
    p_app.add_argument("--chain", required=True, help="JSONL chain path (must already exist).")
    p_app.add_argument("--summary", required=True, help="Brief summary of what was observed.")
    p_app.add_argument("--evidence", required=True, help="Supporting evidence (body and/or URI/path).")
    p_app.add_argument("--confidence", type=float, default=0.7, help="Observer confidence in [0.0, 1.0] (default 0.7).")
    p_app.add_argument("--timestamp", default=None, help="UTC ISO-8601 timestamp (default: now).")
    p_app.add_argument("--click", default=None, help="StaticClock gear-click hex (64). Default: derived locally.")
    p_app.add_argument("--click-index", type=int, default=None, dest="click_index", help="Monotonic StaticClock click index (must not decrease).")

    p_ver = sub.add_parser("verify", help="Walk the chain; exit 0 if intact, nonzero if broken.")
    p_ver.add_argument("file", help="JSONL chain path.")

    p_show = sub.add_parser("show", help="Print receipts in a chain.")
    p_show.add_argument("file", help="JSONL chain path.")

    p_gate = sub.add_parser(
        "gate",
        help="Hash FILE, append a receipt, verify; treat the file as accepted only if the chain is intact.",
    )
    p_gate.add_argument("file", help="File to hash and accept.")
    p_gate.add_argument(
        "--chain",
        default=None,
        help="JSONL chain path (default: FILE.receipts.jsonl beside the file).",
    )
    p_gate.add_argument("--summary", default=None, help="Optional summary (default: gate accept <name>).")
    p_gate.add_argument("--confidence", type=float, default=1.0, help="Observer confidence in [0.0, 1.0].")
    p_gate.add_argument("--timestamp", default=None, help="UTC ISO-8601 timestamp (default: now).")
    p_gate.add_argument("--json", action="store_true", dest="as_json", help="Print the verify payload as JSON.")
    p_gate.add_argument("--click", default=None, help="StaticClock gear-click hex (64).")
    p_gate.add_argument("--click-index", type=int, default=None, dest="click_index", help="Monotonic StaticClock click index.")

    p_tl = sub.add_parser("timeslate", help="Genesis or append a timeslate bound to a StaticClock click.")
    p_tl.add_argument("--chain", required=True, help="JSONL lattice path.")
    p_tl.add_argument("--summary", required=True, help="Brief summary of what was observed.")
    p_tl.add_argument("--evidence", required=True, help="Supporting evidence (body and/or URI/path).")
    p_tl.add_argument("--confidence", type=float, default=0.7, help="Observer confidence in [0.0, 1.0].")
    p_tl.add_argument("--timestamp", default=None, help="UTC ISO-8601 timestamp (default: now).")
    p_tl.add_argument("--click", default=None, help="StaticClock gear-click hex (64). Default: derived locally.")
    p_tl.add_argument("--click-index", type=int, default=None, dest="click_index", help="Monotonic StaticClock click index.")

    p_lat = sub.add_parser("lattice", help="Verify receipt links + StaticClock timeslate binds. No rollbacks.")
    p_lat.add_argument("file", help="JSONL lattice path.")

    p_click = sub.add_parser("click", help="Derive a local StaticClock click digest. No network.")
    p_click.add_argument("--timestamp", default=None, help="UTC ISO-8601 timestamp (default: now).")
    p_click.add_argument("--click-index", type=int, default=0, dest="click_index", help="Click index (default 0).")
    p_click.add_argument("--json", default=None, dest="click_json", help="Optional JSON file of a StaticClock advisory/action.")

    p_doc = sub.add_parser("doctor", help="Self-check. No network, no telemetry.")
    p_doc.add_argument("--json", action="store_true", dest="as_json", help="Print doctor results as JSON.")

    p_imp = sub.add_parser("import", help="Import a JSON document.")
    p_imp.add_argument("path")

    p_exp = sub.add_parser("export", help="Export a JSON document.")
    p_exp.add_argument("path")

    return parser



def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _cmd_gate(args: argparse.Namespace) -> int:
    path = Path(args.file)
    if not path.is_file():
        print(f"not found: {path}", file=sys.stderr)
        return 2
    digest = _sha256_file(path)
    evidence = f"sha256:{digest} path:{path.name}"
    summary = args.summary or f"gate accept {path.name}"
    chain_path = Path(args.chain) if args.chain else Path(str(path) + ".receipts.jsonl")
    if not chain_path.is_file() or chain_path.stat().st_size == 0:
        chain = Chain.genesis(
            chain_path,
            summary=summary,
            evidence=evidence,
            confidence=args.confidence,
            timestamp=args.timestamp,
            staticclock_click=args.click,
            click_index=args.click_index,
        )
        rec = chain[-1]
        action = "genesis"
    else:
        chain = Chain.load(chain_path)
        rec = chain.append(
            summary=summary,
            evidence=evidence,
            confidence=args.confidence,
            timestamp=args.timestamp,
            require_existing=True,
            staticclock_click=args.click,
            click_index=args.click_index,
        )
        action = "appended"
    result = chain.lattice()
    payload = {
        "ok": result.ok,
        "accepted": bool(result.ok),
        "action": action,
        "file": str(path),
        "file_sha256": digest,
        "receipt": rec.hash,
        "timeslate_hash": rec.timeslate_hash,
        "click_index": rec.click_index,
        "staticclock_click": rec.staticclock_click,
        "chain": str(chain_path),
        "length": result.length,
        "bound": result.bound,
        "errors": result.errors,
        "role": ROLE,
    }
    if args.as_json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"{action} {rec.hash}")
        print(f"file_sha256={digest}")
        print(f"chain={chain_path}")
        if result.ok:
            print("accepted")
        else:
            print("chain broken; file not accepted", file=sys.stderr)
    return 0 if result.ok else 1


def _print_receipt_brief(receipt, index: int | None = None) -> None:
    prefix = f"[{index}] " if index is not None else ""
    print(f"{prefix}{receipt.timestamp}  conf={receipt.confidence:.6f}  hash={receipt.hash}")
    print(f"    prev={receipt.prev_hash}")
    print(f"    summary: {receipt.summary}")
    print(f"    evidence: {receipt.evidence}")
    if receipt.timeslate_hash:
        print(f"    click_index={receipt.click_index}  click={receipt.staticclock_click}")
        print(f"    timeslate={receipt.timeslate_hash}")
        print(f"    prev_timeslate={receipt.prev_timeslate_hash}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    try:
        if args.cmd == "version":
            print(f"temporallock {__version__}")
            return 0

        if args.cmd == "ui":
            from temporallock.ui import serve

            serve(host=args.host, port=args.port)
            return 0

        if args.cmd == "genesis":
            path = Path(args.chain)
            chain = Chain.genesis(
                path,
                summary=args.summary,
                evidence=args.evidence,
                confidence=args.confidence,
                timestamp=args.timestamp,
                staticclock_click=args.click,
                click_index=args.click_index,
            )
            rec = chain[-1]
            print(f"genesis {rec.hash}")
            if rec.timeslate_hash:
                print(f"timeslate {rec.timeslate_hash} click_index={rec.click_index}")
            return 0

        if args.cmd == "append":
            path = Path(args.chain)
            if not path.is_file() or path.stat().st_size == 0:
                print("chain does not exist; use genesis for the first receipt", file=sys.stderr)
                return 2
            chain = Chain.load(path)
            rec = chain.append(
                summary=args.summary,
                evidence=args.evidence,
                confidence=args.confidence,
                timestamp=args.timestamp,
                require_existing=True,
                staticclock_click=args.click,
                click_index=args.click_index,
            )
            print(f"appended {rec.hash}")
            if rec.timeslate_hash:
                print(f"timeslate {rec.timeslate_hash} click_index={rec.click_index}")
            return 0

        if args.cmd == "timeslate":
            path = Path(args.chain)
            kwargs = dict(
                summary=args.summary,
                evidence=args.evidence,
                confidence=args.confidence,
                timestamp=args.timestamp,
                staticclock_click=args.click,
                click_index=args.click_index,
            )
            if not path.is_file() or path.stat().st_size == 0:
                chain = Chain.genesis(path, **kwargs)
                rec = chain[-1]
                print(f"genesis {rec.hash}")
            else:
                chain = Chain.load(path)
                rec = chain.append(require_existing=True, **kwargs)
                print(f"appended {rec.hash}")
            print(f"timeslate {rec.timeslate_hash} click_index={rec.click_index}")
            print(f"staticclock_click {rec.staticclock_click}")
            return 0

        if args.cmd == "lattice":
            path = Path(args.file)
            if not path.is_file():
                print(f"not found: {path}", file=sys.stderr)
                return 2
            chain = Chain.load(path)
            result = chain.lattice()
            payload = {
                "ok": result.ok,
                "length": result.length,
                "bound": result.bound,
                "cross_hash": result.cross_hash,
                "first_hash": result.first_hash,
                "last_hash": result.last_hash,
                "last_timeslate_hash": result.last_timeslate_hash,
                "last_click_index": result.last_click_index,
                "errors": result.errors,
                "receipt_ok": result.receipt_ok,
                "role": result.role,
                "staticclock": result.staticclock,
                "note": result.note,
            }
            print(json.dumps(payload, indent=2))
            return 0 if result.ok else 1

        if args.cmd == "click":
            from temporallock.receipt import utc_now

            ts = args.timestamp or utc_now()
            payload = {"kind": "gear-click", "timestamp": ts, "click_index": args.click_index}
            if args.click_json:
                extra = json.loads(Path(args.click_json).read_text(encoding="utf-8"))
                if isinstance(extra, dict):
                    payload.update(extra)
                    payload["kind"] = extra.get("kind") or "gear-click"
                    payload["timestamp"] = extra.get("timestamp") or ts
            digest_hex = staticclock_click_digest(payload)
            print(json.dumps({
                "staticclock_click": digest_hex,
                "click_index": args.click_index,
                "payload": payload,
                "product": "staticclock",
                "host": STATICCLOCK_HOST,
                "note": "Local digest only. TemporalLock does not call StaticClock.",
                "author": "Aziel Eliab",
            }, indent=2))
            return 0

        if args.cmd == "verify":
            path = Path(args.file)
            if not path.is_file():
                print(f"not found: {path}", file=sys.stderr)
                return 2
            chain = Chain.load(path)
            result = chain.verify()
            payload = {
                "ok": result.ok,
                "length": result.length,
                "first_hash": result.first_hash,
                "last_hash": result.last_hash,
                "errors": result.errors,
            }
            print(json.dumps(payload, indent=2))
            return 0 if result.ok else 1

        if args.cmd == "show":
            path = Path(args.file)
            if not path.is_file():
                print(f"not found: {path}", file=sys.stderr)
                return 2
            chain = Chain.load(path)
            print(f"temporallock chain  n={len(chain)}  path={path}")
            for i, rec in enumerate(chain):
                _print_receipt_brief(rec, i)
            forks = chain.forks()
            if forks:
                print(f"forks: {len(forks)} (allowed; no winner chosen)")
                for f in forks:
                    print(f"  prev={f.prev_hash}")
                    for h in f.child_hashes:
                        print(f"    child={h}")
            return 0

        if args.cmd == "gate":
            return _cmd_gate(args)

        if args.cmd == "doctor":
            from temporallock.doctor import run_doctor

            return run_doctor(as_json=getattr(args, "as_json", False))

        if args.cmd == "import":
            from temporallock.jsonio import import_json

            rec = import_json(args.path)
            sys.stdout.write(json.dumps(rec, indent=2, ensure_ascii=False) + "\n")
            return 0

        if args.cmd == "export":
            from temporallock.jsonio import export_json

            rec = export_json(args.path)
            sys.stdout.write(json.dumps(rec, indent=2, ensure_ascii=False) + "\n")
            return 0

        parser.error(f"unknown command {args.cmd}")
        return 2
    except (ReceiptError, ChainError, AppendOnlyError, LatticeError, TemporalLockError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except OSError as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
