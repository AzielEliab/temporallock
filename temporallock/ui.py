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
from temporallock.timeslate import AZOS_HOST, HONEST_SCOPE, ROLE, STATICCLOCK_HOST

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8766
LOOPBACK = frozenset({"127.0.0.1", "localhost", "::1"})
MAX_BODY = 1 * 1024 * 1024

PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<title>TemporalLock</title>
<style>
  :root {
    color-scheme: light;
    --bg: #f7f4ee;
    --panel: #fffdf8;
    --ink: #1a1814;
    --muted: #4a453c;
    --line: #e3d9c4;
    --gold: #c9a227;
    --field: #ffffff;
    --bad: #8d1d1d;
    --pass: #0d5c32;
    --on-gold: #1a1408;
  }
  @media (prefers-color-scheme: dark) {
    :root {
      color-scheme: dark;
      --bg: #12110e;
      --panel: #1c1a16;
      --ink: #f4efe6;
      --muted: #d2c8b8;
      --line: #3d362c;
      --gold: #c9a227;
      --field: #14120f;
      --bad: #ffb4ab;
      --pass: #9ee6b8;
      --on-gold: #1a1408;
    }
  }
  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; }
  body {
    background: var(--bg);
    color: var(--ink);
    font-family: system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    line-height: 1.5;
    min-height: 100vh;
  }
  .wrap {
    width: min(40rem, 100%);
    margin: 0 auto;
    padding: 1.25rem 1rem 3rem;
  }
  .top {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    gap: 1rem;
    margin-bottom: 1.75rem;
  }
  .brand { margin: 0; font-weight: 650; letter-spacing: 0.01em; }
  .author { margin: 0; color: var(--muted); font-size: 0.92rem; }
  h1 { font-size: 1.75rem; font-weight: 650; letter-spacing: -0.02em; margin: 0 0 0.4rem; }
  .lede { margin: 0 0 1.5rem; max-width: 38rem; }
  label { display: block; font-weight: 600; margin: 0 0 0.85rem; }
  .hint { display: block; font-weight: 450; color: var(--muted); margin-top: 0.15rem; }
  input[type="text"], input[type="number"], textarea {
    width: 100%;
    margin-top: 0.35rem;
    padding: 0.65rem 0.75rem;
    border: 1px solid var(--line);
    border-radius: 8px;
    background: var(--field);
    color: var(--ink);
    font: inherit;
  }
  textarea { min-height: 6.5rem; resize: vertical; }
  button, .advanced > summary, .about > summary {
    font: inherit;
    min-height: 44px;
  }
  button {
    border-radius: 8px;
    padding: 0.65rem 1rem;
    cursor: pointer;
  }
  button.primary {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    border: 1px solid var(--gold);
    background: var(--gold);
    color: var(--on-gold);
    font-weight: 650;
    margin: 0.25rem 0 1.25rem;
  }
  button.ghost {
    background: transparent;
    color: var(--ink);
    border: 1px solid var(--line);
  }
  :focus-visible {
    outline: 2px solid var(--gold);
    outline-offset: 2px;
  }
  .banner {
    margin: 0 0 1.5rem;
    padding: 0.85rem 1rem;
    border-radius: 10px;
    border: 1px solid var(--line);
    background: var(--panel);
  }
  .banner.ok { color: var(--pass); border-color: var(--pass); }
  .banner.bad { color: var(--bad); border-color: var(--bad); }
  h2 { font-size: 1.05rem; font-weight: 650; margin: 0 0 0.75rem; }
  ol { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 0.65rem; }
  .receipt {
    border: 1px solid var(--line);
    border-radius: 10px;
    background: var(--panel);
    padding: 0.85rem 1rem;
  }
  .receipt p { margin: 0.35rem 0 0; }
  .when { color: var(--muted); font-size: 0.85rem; font-weight: 500; }
  .hash {
    font-family: ui-monospace, "SFMono-Regular", Menlo, Consolas, monospace;
    font-size: 0.78rem;
    overflow-wrap: anywhere;
    color: var(--muted);
  }
  .empty { color: var(--muted); margin: 0; }
  .err { color: var(--bad); margin: 0.75rem 0 0; }
  .advanced { margin-top: 2rem; }
  .advanced > summary, .about > summary {
    cursor: pointer;
    list-style: none;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem;
    padding: 0.7rem 0.9rem;
    border: 1px solid var(--line);
    border-radius: 10px;
    background: var(--panel);
    font-weight: 650;
  }
  .advanced > summary::-webkit-details-marker,
  .about > summary::-webkit-details-marker { display: none; }
  .advanced > summary::after { content: "Show"; color: var(--muted); font-weight: 500; }
  .advanced[open] > summary::after { content: "Hide"; }
  .advanced-body, .about-body {
    margin-top: 0.75rem;
    padding: 0.2rem 0.15rem 0.4rem;
  }
  .row { display: flex; flex-direction: column; gap: 0.5rem; margin: 0.25rem 0 1rem; }
  .file input { display: block; margin-top: 0.35rem; max-width: 100%; font: inherit; }
  .about { margin-top: 0.75rem; }
  .about-body p { margin: 0.4rem 0 0; overflow-wrap: anywhere; }
  footer { margin-top: 2rem; color: var(--muted); font-size: 0.88rem; }
  @media (min-width: 720px) {
    .wrap { padding: 2rem 1.5rem 4rem; }
    button.primary { width: auto; min-width: 14rem; }
    .row { flex-direction: row; flex-wrap: wrap; }
    .row button { width: auto; }
  }
</style>
</head>
<body>
  <div class="wrap">
    <header class="top">
      <p class="brand">TemporalLock</p>
      <p class="author">Aziel Eliab</p>
    </header>
    <main>
      <h1>Record a receipt</h1>
      <p class="lede">Write what you observed. TemporalLock keeps it on a chain on this computer.</p>
      <form id="receipt-form" autocomplete="off">
        <label for="summary">Summary
          <span class="hint">A short note of what you saw.</span>
          <input id="summary" type="text" name="summary">
        </label>
        <label for="evidence">Evidence
          <span class="hint">A path, link, or the note that supports it.</span>
          <textarea id="evidence" name="evidence" rows="4"></textarea>
        </label>
        <button type="submit" class="primary" id="write">Write first receipt</button>
      </form>
      <p id="banner" class="banner" role="status">No receipts yet. Write the first one above.</p>
      <h2>Receipts</h2>
      <ol id="list"></ol>
      <p class="empty" id="empty">Nothing recorded in this session yet.</p>
      <p class="err" id="err" hidden></p>
      <details class="advanced" id="advanced">
        <summary>Advanced</summary>
        <div class="advanced-body">
          <label for="confidence">Confidence
            <span class="hint">A number from 0 to 1. Default 0.7.</span>
            <input id="confidence" type="number" min="0" max="1" step="0.01" value="0.7">
          </label>
          <label for="click-index">Click index
            <span class="hint">Leave blank for the next StaticClock click. It cannot move backward.</span>
            <input id="click-index" type="number" min="0" step="1">
          </label>
          <div class="row">
            <button type="button" class="ghost" id="verify">Check links</button>
            <button type="button" class="ghost" id="lattice">Check timeslate binds</button>
            <button type="button" class="ghost" id="export">Export JSON</button>
          </div>
          <label class="file" for="import-json">Import JSON
            <input type="file" id="import-json" accept="application/json,.json,.jsonl">
          </label>
          <details class="about">
            <summary>About</summary>
            <div class="about-body">
              <p>A timeslate is a receipt linked to a StaticClock gear-click. Receipts, not truth claims. Forks stay side by side. A correction is a new receipt.</p>
              <p>This page listens on 127.0.0.1. The receipts in this session are removed when you stop the app. Version __VERSION__.</p>
              <p>StaticClock: __STATICCLOCK__</p>
              <p>AZ-OS: __AZOS__</p>
              <p>Author: Aziel Eliab</p>
            </div>
          </details>
        </div>
      </details>
    </main>
    <footer>Aziel Eliab · 127.0.0.1</footer>
  </div>
<script>
(function () {
  const $ = (id) => document.getElementById(id);
  let last = null;
  let mode = "ready";

  function fail(msg) {
    $("err").hidden = false;
    $("err").textContent = msg;
  }
  function explain(msg) {
    const text = String(msg || "Something went wrong.");
    if (/evidence/i.test(text)) return text + " Next: add a note or a path in Evidence, then try again.";
    if (/genesis/i.test(text)) return text + " Next: write the first receipt before adding another.";
    if (/confidence/i.test(text)) return text + " Next: set Confidence between 0 and 1 under Advanced.";
    if (/click_index|rollback/i.test(text)) return text + " Next: use a click index that stays the same or moves forward.";
    return text + " Next: check the fields and try again.";
  }
  function fields() {
    const idx = $("click-index").value;
    const body = {
      summary: $("summary").value,
      evidence: $("evidence").value,
      confidence: Number($("confidence").value),
    };
    if (idx !== "") body.click_index = Number(idx);
    return body;
  }
  function noun(n) { return n === 1 ? "receipt" : "receipts"; }
  function statusText(data) {
    const n = (data.receipts || []).length;
    const v = data.verify || {};
    const lat = data.lattice || {};
    if (mode === "verify") {
      if (!n) return "No receipts yet. Write the first one, then check links.";
      return v.ok
        ? ("Links check out. " + n + " " + noun(n) + " on this chain.")
        : ("These receipts do not link. " + ((v.errors || []).join(" ") || "Read the list below."));
    }
    if (mode === "lattice") {
      if (!n) return "No receipts yet. Write the first one, then check the timeslate binds.";
      return lat.ok
        ? ("Timeslate binds check out. " + (lat.bound || 0) + " bound.")
        : ("Timeslate binds need a look. " + ((lat.errors || []).join(" ") || "Read the list below."));
    }
    if (mode === "wrote" && n === 1) return "First receipt saved. Add another when you have a new observation.";
    if (mode === "wrote") return "Receipt added. Earlier receipts stay as they were.";
    if (mode === "imported") return "Imported " + n + " " + noun(n) + ".";
    if (!n) return "No receipts yet. Write the first one above.";
    return n + " " + noun(n) + " in this session.";
  }
  function draw(data) {
    last = data;
    $("err").hidden = true;
    $("err").textContent = "";
    const n = (data.receipts || []).length;
    const banner = $("banner");
    const v = data.verify || {};
    const lat = data.lattice || {};
    let tone = "";
    if (mode === "verify") tone = v.ok ? "ok" : "bad";
    else if (mode === "lattice") tone = lat.ok ? "ok" : "bad";
    else if (n) tone = "ok";
    banner.className = "banner" + (tone ? " " + tone : "");
    banner.textContent = statusText(data);
    $("write").textContent = n ? "Add receipt" : "Write first receipt";
    $("empty").hidden = n > 0;
    const ol = $("list");
    ol.replaceChildren();
    (data.receipts || []).forEach((rec) => {
      const li = document.createElement("li");
      li.className = "receipt";
      const when = document.createElement("div");
      when.className = "when";
      when.textContent = rec.timestamp || "";
      const summary = document.createElement("p");
      summary.textContent = rec.summary || "";
      const evidence = document.createElement("p");
      evidence.textContent = rec.evidence || "";
      const hash = document.createElement("p");
      hash.className = "hash";
      hash.textContent = rec.hash || "";
      li.append(when, summary, evidence, hash);
      ol.appendChild(li);
    });
    if (mode === "wrote") {
      $("summary").value = "";
      $("evidence").value = "";
      $("summary").focus();
    }
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
  $("receipt-form").addEventListener("submit", async (ev) => {
    ev.preventDefault();
    if (!$("evidence").value.trim()) {
      fail("Evidence is required. Next: add a note or a path, then try again.");
      return;
    }
    const conf = Number($("confidence").value);
    if (!Number.isFinite(conf) || conf < 0 || conf > 1) {
      fail("Confidence needs to be a number from 0 to 1. Next: set it under Advanced, then try again.");
      return;
    }
    const n = last && last.receipts ? last.receipts.length : 0;
    mode = "wrote";
    try {
      draw(await post(n ? "/api/append" : "/api/genesis", fields()));
    } catch (e) {
      mode = "ready";
      fail(explain(e.message || e));
    }
  });
  $("verify").onclick = async () => {
    mode = "verify";
    try { draw(await post("/api/verify", {})); } catch (e) { fail(explain(e.message || e)); }
  };
  $("lattice").onclick = async () => {
    mode = "lattice";
    try { draw(await post("/api/lattice", {})); } catch (e) { fail(explain(e.message || e)); }
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
      try {
        receipts = text.split(/\n/).filter(Boolean).map((line) => JSON.parse(line));
      } catch (err) {
        fail("That file is not JSON. Next: choose a JSON or JSONL file of receipts.");
        return;
      }
    }
    if (!receipts || !receipts.length) {
      fail("That file has no receipts. Next: choose a JSON file that contains a receipts array.");
      return;
    }
    mode = "imported";
    try { draw(await post("/api/import", { receipts: receipts })); }
    catch (err) { fail(explain(err.message || err)); }
  };
  $("export").onclick = () => {
    const receipts = (last && last.receipts) || [];
    if (!receipts.length) {
      fail("Nothing to export yet. Next: write a receipt, then export again.");
      return;
    }
    const blob = new Blob([JSON.stringify(receipts, null, 2)], {type: "application/json"});
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
""".replace("__VERSION__", __version__).replace("__STATICCLOCK__", STATICCLOCK_HOST).replace("__AZOS__", AZOS_HOST)


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
    lattice = chain.lattice()
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
        "lattice": {
            "ok": lattice.ok,
            "bound": lattice.bound,
            "cross_hash": lattice.cross_hash,
            "last_timeslate_hash": lattice.last_timeslate_hash,
            "last_click_index": lattice.last_click_index,
            "errors": list(lattice.errors),
        },
        "role": ROLE,
        "staticclock": STATICCLOCK_HOST,
        "azos": AZOS_HOST,
        "note": HONEST_SCOPE,
    }


def _empty(message: str) -> dict[str, Any]:
    return {
        "message": message,
        "receipts": [],
        "verify": {"ok": True, "length": 0, "first_hash": None, "last_hash": None, "errors": []},
        "lattice": {"ok": True, "bound": 0, "cross_hash": False, "last_timeslate_hash": None, "last_click_index": None, "errors": []},
        "role": ROLE,
        "staticclock": STATICCLOCK_HOST,
        "azos": AZOS_HOST,
        "note": HONEST_SCOPE,
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

    def _wants_json(self) -> bool:
        accept = (self.headers.get("Accept") or "").lower()
        if "application/json" not in accept:
            return False
        html_at = accept.find("text/html")
        json_at = accept.find("application/json")
        return html_at == -1 or json_at < html_at

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            if self._wants_json():
                host, port = self.server.server_address[:2]
                shown = f"[{host}]" if ":" in str(host) else str(host)
                self._json(200, {
                    "ok": True,
                    "name": "TemporalLock",
                    "author": "Aziel Eliab",
                    "version": __version__,
                    "role": ROLE,
                    "bind_host": host,
                    "open": f"http://{shown}:{port}/",
                })
                return
            self._send(200, PAGE.encode("utf-8"), "text/html; charset=utf-8")
            return
        if path == "/health":
            self._json(200, {
                "ok": True,
                "bind_host": DEFAULT_HOST,
                "name": "TemporalLock",
                "author": "Aziel Eliab",
                "version": __version__,
                "role": ROLE,
                "staticclock": STATICCLOCK_HOST,
                "azos": AZOS_HOST,
            })
            return
        if path == "/api/chain":
            chain = self._load()
            if chain is None:
                self._json(200, _empty("No timeslates yet. Genesis writes the first lattice node."))
                return
            self._json(200, _payload(chain, "Current timeslates on the local lattice."))
            return
        self._json(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        try:
            if path == "/api/verify":
                chain = self._load()
                if chain is None:
                    self._json(200, _empty("No timeslates to verify."))
                    return
                result = chain.verify()
                msg = "Chain intact." if result.ok else "Broken links or hashes in these receipts."
                self._json(200, _payload(chain, msg))
                return
            if path == "/api/lattice":
                chain = self._load()
                if chain is None:
                    self._json(200, _empty("No timeslates to walk."))
                    return
                result = chain.lattice()
                msg = (
                    "Lattice intact · StaticClock cross-hash · no rollbacks."
                    if result.ok
                    else "Lattice errors: " + "; ".join(result.errors)
                )
                self._json(200, _payload(chain, msg))
                return
            body = self._read_json()
            summary = str(body.get("summary") or "")
            evidence = str(body.get("evidence") or "")
            confidence = float(body.get("confidence") if body.get("confidence") is not None else 0.7)
            click_index = body.get("click_index")
            if click_index is not None and click_index != "":
                click_index = int(click_index)
            else:
                click_index = None
            dest = self._chain_path()
            if path == "/api/genesis":
                chain = Chain.genesis(
                    dest,
                    summary=summary,
                    evidence=evidence,
                    confidence=confidence,
                    staticclock_click=body.get("staticclock_click") or None,
                    click_index=click_index,
                )
                self._json(200, _payload(chain, "Genesis timeslate written. Receipts, not truth claims."))
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
                self._json(200, _payload(chain, "Imported timeslates. Receipts, not truth claims."))
                return
            if path == "/api/append":
                if not dest.is_file() or dest.stat().st_size == 0:
                    self._json(400, {"error": "chain does not exist; use genesis for the first timeslate"})
                    return
                chain = Chain.load(dest)
                chain.append(
                    summary=summary,
                    evidence=evidence,
                    confidence=confidence,
                    require_existing=True,
                    staticclock_click=body.get("staticclock_click") or None,
                    click_index=click_index,
                )
                self._json(200, _payload(chain, "Timeslate appended. StaticClock click locked forward."))
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
    shown = f"[{host}]" if ":" in host else host
    sys.stdout.write(f"Open http://{shown}:{port}/\n")
    sys.stdout.flush()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        sys.stdout.write("\nstopped\n")
    finally:
        httpd.server_close()
