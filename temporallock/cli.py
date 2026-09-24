"""Command-line interface for TemporalLock.

Human text is the default. Pass ``--json`` on verify, lattice, click,
gate, doctor, import, and export for the machine payload.

    temporallock
    temporallock ui [--host 127.0.0.1] [--port 8766]
    temporallock version
    temporallock gate FILE [--chain FILE.jsonl] [--json]
    temporallock genesis --chain FILE.jsonl --summary "..." --evidence "..."
    temporallock append  --chain FILE.jsonl --summary "..." --evidence "..." [--confidence 0.7] [--timestamp ISO]
    temporallock timeslate --chain FILE.jsonl --summary "..." --evidence "..."
    temporallock lattice FILE.jsonl [--json]
    temporallock click [--timestamp ISO] [--json [FILE]]
    temporallock verify FILE.jsonl [--json]
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
import re
import sys
from pathlib import Path
from typing import Sequence

from temporallock import __version__
from temporallock.chain import Chain
from temporallock.errors import AppendOnlyError, ChainError, LatticeError, ReceiptError, TemporalLockError
from temporallock.timeslate import ROLE, STATICCLOCK_HOST, staticclock_click_digest

ROOT_HELP = """\
usage: temporallock <command> [options]

Record observation receipts on a local chain. Each receipt stays.

commands:
  ui                 Open the local app at http://127.0.0.1:8766
  doctor             Check this install
  genesis            Write the first receipt
  append             Add a receipt to an existing chain
  show               Print the receipts in a chain
  verify             Check that receipt links are intact

advanced:
  gate               Hash a file and record a receipt for it
  timeslate          Write a receipt bound to a StaticClock click
  lattice            Check receipt links and timeslate binds
  click              Print a local StaticClock click digest
  import             Import a JSON document
  export             Export a JSON document
  version            Print the package version

examples:
  temporallock
  temporallock ui
  temporallock doctor
  temporallock genesis --chain notes.jsonl --summary "sky was overcast" --evidence "photo:./sky.jpg"
  temporallock verify notes.jsonl
  temporallock verify notes.jsonl --json

Add --json on verify, lattice, click, gate, doctor, import, and export
for machine output. `temporallock click --json FILE` also mixes that
JSON object into the click.

Author: Aziel Eliab
"""

WELCOME = """\
TemporalLock records observation receipts on a local chain. Each receipt stays.

Open the app:
  temporallock ui

Or write the first receipt:
  temporallock genesis --chain notes.jsonl --summary "sky was overcast" --evidence "photo:./sky.jpg"

Check this install:
  temporallock doctor

Author: Aziel Eliab
"""

_TRY = {
    "genesis": 'temporallock genesis --chain notes.jsonl --summary "sky was overcast" --evidence "photo:./sky.jpg"',
    "append": 'temporallock append --chain notes.jsonl --summary "rain began" --evidence "log:./rain.txt"',
    "verify": "temporallock verify notes.jsonl",
    "show": "temporallock show notes.jsonl",
    "gate": "temporallock gate notes.txt",
    "timeslate": 'temporallock timeslate --chain notes.jsonl --summary "hook fired" --evidence "azos:prefab"',
    "lattice": "temporallock lattice notes.jsonl",
    "click": "temporallock click",
    "import": "temporallock import notes.json",
    "export": "temporallock export out.json",
    "ui": "temporallock ui",
    "doctor": "temporallock doctor",
    "version": "temporallock version",
}


class HumanParser(argparse.ArgumentParser):
    """Git-style root help, and plain misuse messages with a next step."""

    def __init__(self, *args, root: bool = False, **kwargs):
        self.root = root
        super().__init__(*args, **kwargs)

    def format_help(self) -> str:
        if self.root:
            return ROOT_HELP
        return super().format_help()

    def error(self, message: str) -> None:
        cmd = ""
        parts = self.prog.split()
        if len(parts) >= 2:
            cmd = parts[-1]
        self.exit(2, _friendly_misuse(message, cmd) + "\n")


def _friendly_misuse(message: str, cmd: str) -> str:
    low = message.lower()
    if "invalid choice" in low:
        match = re.search(r"invalid choice: '([^']*)'", message)
        name = match.group(1) if match else "that"
        return f'Unknown command "{name}". Try: temporallock ui   or   temporallock --help'
    example = _TRY.get(cmd, "temporallock --help")
    if "required" in low:
        tail = message.split(":", 1)[-1].strip() if ":" in message else "a command"
        if not cmd or tail == "cmd":
            return "Choose a command. Try: temporallock ui   or   temporallock --help"
        return f"Missing {tail}.\nTry: {example}"
    if message[:1].islower():
        message = message[0].upper() + message[1:]
    return f"{message}.\nTry: {example}"


def _next_step(exc: BaseException) -> str:
    text = str(exc).lower()
    if "already exists" in text or "use append" in text:
        return 'Next: temporallock append --chain <file> --summary "..." --evidence "..."'
    if "does not exist" in text or "use genesis" in text:
        return 'Next: temporallock genesis --chain <file> --summary "..." --evidence "..."'
    if "evidence" in text:
        return "Next: pass --evidence with a note or a path, then run the command again."
    if "confidence" in text:
        return "Next: pass --confidence as a number from 0 to 1."
    if "rollback" in text or "click_index" in text:
        return "Next: use a click index that stays the same or moves forward, or omit --click-index."
    if "timestamp" in text:
        return "Next: pass --timestamp as UTC ISO-8601, such as 2026-07-12T14:30:00Z."
    return "Next: temporallock --help"


def _fail(reason: str, nxt: str) -> int:
    print(reason, file=sys.stderr)
    print(nxt, file=sys.stderr)
    return 2


def _emit(payload: dict, lines: Sequence[str], as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, indent=2))
        return
    for line in lines:
        print(line)


def _exit_code(code: object) -> int:
    if code is None or code == 0:
        return 0
    if isinstance(code, int):
        return code
    return 2


def _build_parser() -> HumanParser:
    parser = HumanParser(
        prog="temporallock",
        root=True,
        description="Record observation receipts on a local chain.",
    )
    sub = parser.add_subparsers(dest="cmd", required=False, parser_class=HumanParser)

    sub.add_parser("version", help="Print the package version.")

    p_ui = sub.add_parser("ui", help="Open the local app at http://127.0.0.1:8766.")
    p_ui.add_argument("--host", default="127.0.0.1", help="Bind host (default 127.0.0.1).")
    p_ui.add_argument("--port", type=int, default=8766, help="Bind port (default 8766).")

    p_gen = sub.add_parser("genesis", help="Write the first receipt.")
    p_gen.add_argument("--chain", required=True, help="JSONL chain path (must not already exist).")
    p_gen.add_argument("--summary", required=True, help="Brief summary of what was observed.")
    p_gen.add_argument("--evidence", required=True, help="Supporting evidence (body and/or URI/path).")
    p_gen.add_argument("--confidence", type=float, default=1.0, help="Observer confidence in [0.0, 1.0] (default 1.0).")
    p_gen.add_argument("--timestamp", default=None, help="UTC ISO-8601 timestamp (default: now).")
    p_gen.add_argument("--click", default=None, help="StaticClock gear-click hex (64). Default: derived locally.")
    p_gen.add_argument("--click-index", type=int, default=None, dest="click_index", help="Monotonic StaticClock click index.")

    p_app = sub.add_parser("append", help="Add a receipt to an existing chain.")
    p_app.add_argument("--chain", required=True, help="JSONL chain path (must already exist).")
    p_app.add_argument("--summary", required=True, help="Brief summary of what was observed.")
    p_app.add_argument("--evidence", required=True, help="Supporting evidence (body and/or URI/path).")
    p_app.add_argument("--confidence", type=float, default=0.7, help="Observer confidence in [0.0, 1.0] (default 0.7).")
    p_app.add_argument("--timestamp", default=None, help="UTC ISO-8601 timestamp (default: now).")
    p_app.add_argument("--click", default=None, help="StaticClock gear-click hex (64). Default: derived locally.")
    p_app.add_argument("--click-index", type=int, default=None, dest="click_index", help="Monotonic StaticClock click index (must not decrease).")

    p_ver = sub.add_parser("verify", help="Check that receipt links are intact.")
    p_ver.add_argument("file", help="JSONL chain path.")
    p_ver.add_argument("--json", action="store_true", dest="as_json", help="Print the verify payload as JSON.")

    p_show = sub.add_parser("show", help="Print the receipts in a chain.")
    p_show.add_argument("file", help="JSONL chain path.")

    p_gate = sub.add_parser(
        "gate",
        help="Hash FILE, append a receipt, and accept the file when the chain is intact.",
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

    p_tl = sub.add_parser("timeslate", help="Write a receipt bound to a StaticClock click.")
    p_tl.add_argument("--chain", required=True, help="JSONL lattice path.")
    p_tl.add_argument("--summary", required=True, help="Brief summary of what was observed.")
    p_tl.add_argument("--evidence", required=True, help="Supporting evidence (body and/or URI/path).")
    p_tl.add_argument("--confidence", type=float, default=0.7, help="Observer confidence in [0.0, 1.0].")
    p_tl.add_argument("--timestamp", default=None, help="UTC ISO-8601 timestamp (default: now).")
    p_tl.add_argument("--click", default=None, help="StaticClock gear-click hex (64). Default: derived locally.")
    p_tl.add_argument("--click-index", type=int, default=None, dest="click_index", help="Monotonic StaticClock click index.")

    p_lat = sub.add_parser("lattice", help="Check receipt links and timeslate binds.")
    p_lat.add_argument("file", help="JSONL lattice path.")
    p_lat.add_argument("--json", action="store_true", dest="as_json", help="Print the lattice payload as JSON.")

    p_click = sub.add_parser("click", help="Print a local StaticClock click digest.")
    p_click.add_argument("--timestamp", default=None, help="UTC ISO-8601 timestamp (default: now).")
    p_click.add_argument("--click-index", type=int, default=0, dest="click_index", help="Click index (default 0).")
    p_click.add_argument(
        "--json",
        nargs="?",
        const="",
        default=None,
        dest="click_json",
        help="Print the click object as JSON. Optional FILE mixes that JSON object into the click.",
    )

    p_doc = sub.add_parser("doctor", help="Check this install. No network.")
    p_doc.add_argument("--json", action="store_true", dest="as_json", help="Print doctor results as JSON.")

    p_imp = sub.add_parser("import", help="Import a JSON document.")
    p_imp.add_argument("path")
    p_imp.add_argument("--json", action="store_true", dest="as_json", help="Print the import result as JSON.")

    p_exp = sub.add_parser("export", help="Export a JSON document.")
    p_exp.add_argument("path")
    p_exp.add_argument("--json", action="store_true", dest="as_json", help="Print the export result as JSON.")

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
        return _fail(f"not found: {path}", f"Next: check the path, then run temporallock gate {path}")
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
            print(f"Next: temporallock show {chain_path}")
        else:
            print("chain broken; file not accepted", file=sys.stderr)
            print(f"Next: temporallock lattice {chain_path}", file=sys.stderr)
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


def _not_found(path: Path, command: str) -> int:
    return _fail(f"not found: {path}", f"Next: check the path, then run temporallock {command} {path}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    try:
        args = parser.parse_args(list(argv) if argv is not None else None)
    except SystemExit as exc:
        return _exit_code(exc.code)

    try:
        if args.cmd is None:
            print(WELCOME, end="")
            return 0

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
            print(f"Next: temporallock show {path}")
            return 0

        if args.cmd == "append":
            path = Path(args.chain)
            if not path.is_file() or path.stat().st_size == 0:
                return _fail(
                    "chain does not exist; use genesis for the first receipt",
                    f'Next: temporallock genesis --chain {path} --summary "..." --evidence "..."',
                )
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
            print(f"Next: temporallock show {path}")
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
            print(f"Next: temporallock show {path}")
            return 0

        if args.cmd == "lattice":
            path = Path(args.file)
            if not path.is_file():
                return _not_found(path, "lattice")
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
            if result.ok:
                lines = [
                    "Lattice intact",
                    f"Receipts: {result.length}",
                    f"Timeslates bound: {result.bound}",
                    "StaticClock cross-hash: yes" if result.cross_hash else "StaticClock cross-hash: no",
                ]
            else:
                lines = ["Lattice has errors", f"Receipts: {result.length}"]
                lines.extend(f"- {err}" for err in result.errors)
                lines.append(f"Next: temporallock show {path}")
            _emit(payload, lines, args.as_json)
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
            body = {
                "staticclock_click": digest_hex,
                "click_index": args.click_index,
                "payload": payload,
                "product": "staticclock",
                "host": STATICCLOCK_HOST,
                "note": "Local digest only. TemporalLock does not call StaticClock.",
                "author": "Aziel Eliab",
            }
            _emit(
                body,
                [
                    "Local StaticClock click",
                    f"staticclock_click={digest_hex}",
                    f"click_index={args.click_index}",
                    "Computed on this computer.",
                    "Author: Aziel Eliab",
                ],
                args.click_json is not None,
            )
            return 0

        if args.cmd == "verify":
            path = Path(args.file)
            if not path.is_file():
                return _not_found(path, "verify")
            chain = Chain.load(path)
            result = chain.verify()
            payload = {
                "ok": result.ok,
                "length": result.length,
                "first_hash": result.first_hash,
                "last_hash": result.last_hash,
                "errors": result.errors,
            }
            if result.ok:
                lines = [
                    "Chain intact",
                    f"Receipts: {result.length}",
                ]
                if result.last_hash:
                    lines.append(f"Last hash: {result.last_hash}")
            else:
                lines = ["Chain has broken links", f"Receipts: {result.length}"]
                lines.extend(f"- {err}" for err in result.errors)
                lines.append(f"Next: temporallock show {path}")
            _emit(payload, lines, args.as_json)
            return 0 if result.ok else 1

        if args.cmd == "show":
            path = Path(args.file)
            if not path.is_file():
                return _not_found(path, "show")
            chain = Chain.load(path)
            print(f"temporallock chain  n={len(chain)}  path={path}")
            for i, rec in enumerate(chain):
                _print_receipt_brief(rec, i)
            forks = chain.forks()
            if forks:
                print(f"forks: {len(forks)} (kept side by side)")
                for fork in forks:
                    print(f"  prev={fork.prev_hash}")
                    for child in fork.child_hashes:
                        print(f"    child={child}")
            return 0

        if args.cmd == "gate":
            return _cmd_gate(args)

        if args.cmd == "doctor":
            from temporallock.doctor import run_doctor

            return run_doctor(as_json=getattr(args, "as_json", False))

        if args.cmd == "import":
            from temporallock.jsonio import import_json

            rec = import_json(args.path)
            _emit(
                rec,
                [f"Imported {rec['imported']}", f"Stored {rec['stored']}"],
                args.as_json,
            )
            return 0

        if args.cmd == "export":
            from temporallock.jsonio import export_json

            rec = export_json(args.path)
            _emit(rec, [f"Exported {rec['exported']}"], args.as_json)
            return 0

        return _fail(
            f'Unknown command "{args.cmd}".',
            "Next: temporallock ui   or   temporallock --help",
        )
    except (ReceiptError, ChainError, AppendOnlyError, LatticeError, TemporalLockError) as exc:
        return _fail(str(exc), _next_step(exc))
    except json.JSONDecodeError as exc:
        return _fail(
            f"That file is not JSON ({exc.msg}).",
            "Next: pass a JSON object file, then run the command again.",
        )
    except ValueError as exc:
        return _fail(str(exc), "Next: check the value, then run the command again.")
    except OSError as exc:
        reason = exc.strerror or str(exc)
        return _fail(f"Could not use that path. {reason}.", "Next: check the path, then run the command again.")


if __name__ == "__main__":
    raise SystemExit(main())
