"""Command-line interface for TemporalLock.

    temporallock ui [--host 127.0.0.1] [--port 8766]
    temporallock version
    temporallock gate FILE [--chain FILE.jsonl]
    temporallock genesis --chain FILE.jsonl --summary "..." --evidence "..."
    temporallock append  --chain FILE.jsonl --summary "..." --evidence "..." [--confidence 0.7] [--timestamp ISO]
    temporallock verify FILE.jsonl
    temporallock show FILE.jsonl

Receipts, not truth claims. Forks always allowed.
``gate FILE`` hashes the file and appends a receipt before treating it
as accepted (genesis if the chain is new, else append, then verify).
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
from temporallock.errors import AppendOnlyError, ChainError, ReceiptError, TemporalLockError


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="temporallock",
        description=(
            "TemporalLock — append-only observation receipts "
            "(Aziel Eliab, July 2026). Receipts, not truth claims. "
            "Local UI: `temporallock ui` at http://127.0.0.1:8766."
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

    p_app = sub.add_parser("append", help="Append a receipt to an existing chain.")
    p_app.add_argument("--chain", required=True, help="JSONL chain path (must already exist).")
    p_app.add_argument("--summary", required=True, help="Brief summary of what was observed.")
    p_app.add_argument("--evidence", required=True, help="Supporting evidence (body and/or URI/path).")
    p_app.add_argument("--confidence", type=float, default=0.7, help="Observer confidence in [0.0, 1.0] (default 0.7).")
    p_app.add_argument("--timestamp", default=None, help="UTC ISO-8601 timestamp (default: now).")

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
        )
        action = "appended"
    result = chain.verify()
    payload = {
        "ok": result.ok,
        "accepted": bool(result.ok),
        "action": action,
        "file": str(path),
        "file_sha256": digest,
        "receipt": rec.hash,
        "chain": str(chain_path),
        "length": result.length,
        "errors": result.errors,
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
            )
            rec = chain[-1]
            print(f"genesis {rec.hash}")
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
            )
            print(f"appended {rec.hash}")
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
    except (ReceiptError, ChainError, AppendOnlyError, TemporalLockError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except OSError as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
