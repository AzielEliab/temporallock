"""Localhost UI for TemporalLock. Binds 127.0.0.1. Chain lives in a process tmp dir."""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from temporallock import __version__
from temporallock.chain import Chain
from temporallock.errors import TemporalLockError

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8766
LOOPBACK = frozenset({"127.0.0.1", "localhost", "::1"})
MAX_BODY = 1 * 1024 * 1024

PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>TemporalLock</title>
<style>
  :root {
    --bg: #0f1419; --panel: #171e27; --ink: #e8edf2; --muted: #8b97a6;
    --line: #2a3544; --gold: #d4bc6a; --focus: #7aa2d4; --bad: #d4534b;
    --pass: #3dba7a;
  }
  * { box-sizing: border-box; }
  html, body {
    margin: 0; padding: 0; background: var(--bg); color: var(--ink);
    font-family: system-ui, "Segoe UI", sans-serif; line-height: 1.45;
  }
  body { max-width: 46rem; margin: 0 auto; padding: 2.1rem 1.2rem 4rem; }
  .tag {
    font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 0.72rem;
    letter-spacing: 0.14em; text-transform: uppercase; color: var(--muted);
  }
  h1 { font-size: 2rem; font-weight: 650; letter-spacing: 0.04em; margin: 0.35rem 0 0.25rem; }
  .motto { color: var(--gold); font-style: italic; margin: 0 0 0.85rem; font-size: 1.05rem; }
  .lede { color: var(--muted); margin: 0 0 1.5rem; max-width: 40rem; }
  fieldset {
    border: 1px solid var(--line); border-radius: 10px; background: var(--panel);
    padding: 1.1rem 1.15rem 1.2rem; margin: 0 0 1rem;
  }
  legend {
    font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 0.72rem;
    letter-spacing: 0.12em; text-transform: uppercase; color: var(--muted); padding: 0 0.4rem;
  }
  label { display: block; font-size: 0.92rem; margin: 0.85rem 0 0.3rem; }
  label .kicker {
    display: block; font-family: ui-monospace, Menlo, Consolas, monospace;
    font-size: 0.68rem; letter-spacing: 0.12em; text-transform: uppercase;
    color: var(--muted); margin-bottom: 0.12rem;
  }
  textarea, input[type="text"], input[type="number"] {
    width: 100%; padding: 0.55rem 0.65rem; border: 1px solid var(--line);
    border-radius: 6px; background: #10161d; color: var(--ink); font: inherit;
  }
  textarea:focus, input:focus { outline: 2px solid var(--focus); outline-offset: 1px; }
  .actions { display: flex; gap: 0.65rem; flex-wrap: wrap; margin: 0 0 1.6rem; }
  button {
    font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 0.85rem;
    letter-spacing: 0.04em; padding: 0.65rem 1rem; border-radius: 8px;
    border: 1px solid var(--ink); background: var(--ink); color: var(--bg);
    cursor: pointer; font-weight: 650;
  }
  button.ghost { background: transparent; color: var(--ink); }
  h2 {
    font-size: 1.05rem; letter-spacing: 0.08em; text-transform: uppercase;
    color: var(--muted); font-weight: 600; margin: 0 0 0.7rem;
  }
  .banner {
    margin: 0 0 1rem; padding: 0.9rem 1rem; border-radius: 10px;
    border: 1px solid var(--line); background: var(--panel); color: var(--muted);
  }
  .banner.ok { color: var(--pass); border-color: var(--pass); }
  .banner.bad { color: var(--bad); border-color: var(--bad); }
  ol { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 0.65rem; }
  .receipt {
    border: 1px solid var(--line); border-radius: 10px; background: var(--panel);
    padding: 0.85rem 1rem;
  }
  .hash { font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 0.75rem; word-break: break-all; color: var(--muted); }
  .err { color: var(--bad); }
  footer { margin-top: 2rem; color: var(--muted); font-size: 0.88rem; }
  .foot-note { font-style: italic; }
</style>
</head>
<body>
  <header>
    <div class="tag">TemporalLock · __VERSION__ · loopback · receipts</div>
    <h1>TemporalLock</h1>
    <p class="motto">Receipts, not truth claims.</p>
    <p class="lede">
      Genesis, append, and verify a local observation chain in a temporary directory
      owned by this process. A receipt records that something was observed. It is not
      a verdict, not a score of truth, and not an official history. Bound to 127.0.0.1 only.
    </p>
  </header>

  <form id="receipt-form" autocomplete="off">
    <fieldset>
      <legend>New receipt</legend>
      <label for="summary"><span class="kicker">Summary</span> Brief note of what was observed.</label>
      <input id="summary" type="text" placeholder="sky was overcast">
      <label for="evidence"><span class="kicker">Evidence</span> Supporting body and/or URI. Required.</label>
      <textarea id="evidence" rows="3" placeholder="photo:./sky.jpg"></textarea>
      <label for="confidence"><span class="kicker">Confidence</span> Observer-assigned float in [0, 1].</label>
      <input id="confidence" type="number" min="0" max="1" step="0.01" value="0.7">
    </fieldset>
    <div class="actions">
      <button type="button" id="genesis">Genesis</button>
      <button type="button" id="append">Append</button>
      <button type="button" class="ghost" id="verify">Verify</button>
      <label class="ghost">Import JSON <input type="file" id="import-json" accept="application/json,.json,.jsonl"></label>
      <button type="button" class="ghost" id="export">Export JSON receipts</button>
    </div>
  </form>

  <div id="banner" class="banner">No receipts yet. Genesis writes the first receipt.</div>
  <h2>Receipts</h2>
  <ol id="list"></ol>
  <p class="err" id="err" hidden></p>

  <footer>
    <p>Apache-2.0 · Aziel Eliab · July 2026 · Bound to 127.0.0.1 · <code>temporallock ui</code></p>
    <p class="foot-note">Receipts, not truth claims. Forks welcome and always allowed.</p>
  </footer>
<script>
(function () {
  const $ = (id) => document.getElementById(id);
  let last = null;
  function fail(msg) { $("err").hidden = false; $("err").textContent = msg; }
  function fields() {
    return {
      summary: $("summary").value,
      evidence: $("evidence").value,
      confidence: Number($("confidence").value),
    };
  }
  function draw(data) {
    last = data;
    $("err").hidden = true;
    const banner = $("banner");
    const v = data.verify || {};
    banner.className = "banner " + (v.ok ? "ok" : (data.receipts && data.receipts.length ? "bad" : ""));
    banner.textContent = data.message || (v.ok
      ? ("Chain intact · " + v.length + " receipts · last " + (v.last_hash || "").slice(0, 12))
      : ("Verify errors: " + ((v.errors || []).join("; ") || "none")));
    const ol = $("list");
    ol.innerHTML = "";
    (data.receipts || []).forEach((rec, i) => {
      const li = document.createElement("li");
      li.className = "receipt";
      li.innerHTML = "<strong>" + (i) + " · " + (rec.timestamp || "") + "</strong>"
        + "<p>" + (rec.summary || "") + "</p>"
        + "<p>" + (rec.evidence || "") + " · conf " + rec.confidence + "</p>"
        + "<p class='hash'>hash " + rec.hash + "</p>"
        + "<p class='hash'>prev " + rec.prev_hash + "</p>";
      ol.appendChild(li);
    });
  }
  async function post(url, body) {
    const res = await fetch(url, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(body || {}),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || ("HTTP " + res.status));
    return data;
  }
  async function refresh() {
    const res = await fetch("/api/chain");
    draw(await res.json());
  }
  $("genesis").onclick = async () => {
    try { draw(await post("/api/genesis", fields())); } catch (e) { fail(String(e.message || e)); }
  };
  $("append").onclick = async () => {
    try { draw(await post("/api/append", fields())); } catch (e) { fail(String(e.message || e)); }
  };
  $("verify").onclick = async () => {
    try { draw(await post("/api/verify", {})); } catch (e) { fail(String(e.message || e)); }
  };
  $("import-json").onchange = async () => {
    const f = $("import-json").files && $("import-json").files[0];
    if (!f) return;
    const text = await f.text();
    let receipts;
    try {
      const parsed = JSON.parse(text);
      receipts = Array.isArray(parsed) ? parsed : (parsed.receipts || []);
    } catch (e) {
      receipts = text.split(/\n/).filter(Boolean).map((line) => JSON.parse(line));
    }
    try { draw(await post("/api/import", { receipts: receipts })); } catch (err) { fail(String(err.message || err)); }
  };
  $("export").onclick = () => {
    if (!last) return;
    const blob = new Blob([JSON.stringify(last.receipts || [], null, 2)], {type: "application/json"});
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "temporallock-receipts.json";
    a.click();
    URL.revokeObjectURL(a.href);
  };
  refresh().catch(() => {});
})();
</script>
</body>
</html>
""".replace("__VERSION__", __version__)


class TemporalServer(ThreadingHTTPServer):
    chain_dir: str
    chain_path: Path

    def server_close(self) -> None:
        super().server_close()
        chain_dir = getattr(self, "chain_dir", None)
        if chain_dir:
            shutil.rmtree(chain_dir, ignore_errors=True)


def _payload(chain: Chain, message: str) -> dict[str, Any]:
    verify = chain.verify()
    return {
        "message": message,
        "receipts": [rec.to_dict() for rec in chain],
        "verify": {
            "ok": verify.ok,
            "length": verify.length,
            "first_hash": verify.first_hash,
            "last_hash": verify.last_hash,
            "errors": list(verify.errors),
        },
        "note": "Receipts, not truth claims.",
    }


def _empty(message: str) -> dict[str, Any]:
    return {
        "message": message,
        "receipts": [],
        "verify": {"ok": True, "length": 0, "first_hash": None, "last_hash": None, "errors": []},
        "note": "Receipts, not truth claims.",
    }


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args: object) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _chain_path(self) -> Path:
        return self.server.chain_path  # type: ignore[attr-defined]

    def _load(self) -> Chain | None:
        path = self._chain_path()
        if not path.is_file() or path.stat().st_size == 0:
            return None
        return Chain.load(path)

    def _send(self, code: int, body: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code: int, obj: Any) -> None:
        self._send(code, json.dumps(obj).encode("utf-8"), "application/json; charset=utf-8")

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length") or 0)
        if length > MAX_BODY:
            raise ValueError("payload too large")
        raw = self.rfile.read(length) if length else b"{}"
        data = json.loads(raw.decode("utf-8") or "{}")
        if not isinstance(data, dict):
            raise ValueError("expected a JSON object")
        return data

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            self._send(200, PAGE.encode("utf-8"), "text/html; charset=utf-8")
            return
        if path == "/health":
            self._json(200, {"ok": True, "bind_host": DEFAULT_HOST, "name": "TemporalLock"})
            return
        if path == "/api/chain":
            chain = self._load()
            if chain is None:
                self._json(200, _empty("No receipts yet. Genesis writes the first receipt."))
                return
            self._json(200, _payload(chain, "Current receipts on the local chain."))
            return
        self._json(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        try:
            if path == "/api/verify":
                chain = self._load()
                if chain is None:
                    self._json(200, _empty("No receipts to verify."))
                    return
                result = chain.verify()
                msg = "Chain intact." if result.ok else "Broken links or hashes in these receipts."
                self._json(200, _payload(chain, msg))
                return
            body = self._read_json()
            summary = str(body.get("summary") or "")
            evidence = str(body.get("evidence") or "")
            confidence = float(body.get("confidence") if body.get("confidence") is not None else 0.7)
            dest = self._chain_path()
            if path == "/api/genesis":
                chain = Chain.genesis(dest, summary=summary, evidence=evidence, confidence=confidence)
                self._json(200, _payload(chain, "Genesis receipt written. Receipts, not truth claims."))
                return
            if path == "/api/import":
                receipts = body.get("receipts")
                if not isinstance(receipts, list) or not receipts:
                    self._json(400, {"error": "receipts array required"})
                    return
                dest = self._chain_path()
                dest.write_text(
                    "\n".join(json.dumps(r, sort_keys=True, separators=(",", ":"), ensure_ascii=False) for r in receipts if isinstance(r, dict)) + "\n",
                    encoding="utf-8",
                )
                chain = Chain.load(dest)
                self._json(200, _payload(chain, "Imported receipts. Receipts, not truth claims."))
                return
            if path == "/api/append":
                if not dest.is_file() or dest.stat().st_size == 0:
                    self._json(400, {"error": "chain does not exist; use genesis for the first receipt"})
                    return
                chain = Chain.load(dest)
                chain.append(
                    summary=summary,
                    evidence=evidence,
                    confidence=confidence,
                    require_existing=True,
                )
                self._json(200, _payload(chain, "Receipt appended. Receipts, not truth claims."))
                return
        except TemporalLockError as exc:
            self._json(400, {"error": str(exc)})
            return
        except Exception as exc:  # noqa: BLE001
            self._json(400, {"error": str(exc)})
            return
        self._json(404, {"error": "not found"})


def make_server(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> TemporalServer:
    if host not in LOOPBACK:
        raise ValueError("TemporalLock UI binds loopback only (127.0.0.1)")
    tmp = tempfile.mkdtemp(prefix="temporallock-ui-")
    httpd = TemporalServer((host, port), Handler)
    httpd.chain_dir = tmp
    httpd.chain_path = Path(tmp) / "chain.jsonl"
    return httpd


def serve(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
    httpd = make_server(host, port)
    sys.stdout.write(f"TemporalLock UI  http://{host}:{port}/\n")
    sys.stdout.write("Local only. Receipts, not truth claims. Chain lives in a process tmp dir.\n")
    sys.stdout.flush()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        sys.stdout.write("\nstopped\n")
    finally:
        httpd.server_close()
