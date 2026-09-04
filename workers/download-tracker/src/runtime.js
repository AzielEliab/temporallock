/**
 * TemporalLock hosted runtime (port of canon/receipt/chain).
 * Stateless: client sends the chain JSON in the body. Receipts not truth claims.
 * /v1 never touches DOWNLOADS KV.
 */
const PRODUCT = "temporallock";
const VERSION = "0.2.0";
const MOTTO = "Receipts, not truth claims.";
const ROLE = "immutable timeslate lattice";
const AUTHOR = "Aziel Eliab";
const STATICCLOCK_HOST = "https://staticclock-download-tracker.vibelock.workers.dev";
const AZOS_HOST = "https://azos-download-tracker.vibelock.workers.dev";
const HOST = "https://temporallock-download-tracker.vibelock.workers.dev";
const SKILL = `---
name: TemporalLock
description: Use when minting or verifying an immutable timeslate lattice hash-chained against StaticClock. AZ-OS integrity log. Receipts, not truth claims. Hosted API is stateless. Hosted /v1 via this Worker or aziel-runtime. Author Aziel Eliab.
---

# TemporalLock

Immutable timeslate lattice. Hash-chained against StaticClock. Receipts, not truth claims.

Author: **Aziel Eliab**.

Use when minting or verifying append-only timeslates bound to a StaticClock gear-click. No rollbacks. AZ-OS prefab hooks may write this integrity log. Hosted API is stateless and does not run AZ-OS.

Always send \`User-Agent: Mozilla/5.0\`. Cloudflare Workers may 403 an empty agent.

## Endpoints (this Worker)

Host: \`https://temporallock-download-tracker.vibelock.workers.dev\`

| Method | Path | What |
|--------|------|------|
| GET | \`/v1/health\` | Liveness. Does not increment downloads. |
| GET | \`/v1/skill\` | This markdown. Does not increment downloads. |
| GET | \`/v1/example\` | Sample timeslate payload. Does not increment downloads. |
| POST | \`/v1/genesis\` | First timeslate. Body includes summary + evidence. Optional click. |
| POST | \`/v1/append\` | Append a timeslate. Client sends the chain. Decreasing click_index is refused. |
| POST | \`/v1/timeslate\` | Genesis or append a StaticClock-bound timeslate. |
| POST | \`/v1/verify\` | Verify receipt hashes and prev links. Not stored. |
| POST | \`/v1/lattice\` | Verify receipt links + timeslate binds + no StaticClock rollback. |
| POST | \`/v1/click\` | Local SHA-256 of a StaticClock-shaped gear-click. No network. |
| POST | \`/v1/gate\` | File-gate preview (hash + timeslate). |

OpenAPI: \`https://temporallock-download-tracker.vibelock.workers.dev/openapi.json\`

Catalog OpenAPI: \`https://aziel-runtime.vibelock.workers.dev/openapi.json\`

MCP: \`POST https://aziel-runtime.vibelock.workers.dev/mcp\`

Catalog aliases under \`/p/temporallock/…\`.

StaticClock (gear-click timeline): \`https://staticclock-download-tracker.vibelock.workers.dev/\`

AZ-OS (prefab OS hooks; integrity precedes execution): \`https://azos-download-tracker.vibelock.workers.dev/\`

## How to call (Mozilla/5.0)

\`\`\`bash
curl -s -A 'Mozilla/5.0' https://temporallock-download-tracker.vibelock.workers.dev/v1/health
curl -s -A 'Mozilla/5.0' -X POST https://temporallock-download-tracker.vibelock.workers.dev/v1/genesis \\
  -H 'content-type: application/json' \\
  -d '{"summary":"desk closed","evidence":"log row"}'
curl -s -A 'Mozilla/5.0' -X POST https://temporallock-download-tracker.vibelock.workers.dev/v1/lattice \\
  -H 'content-type: application/json' \\
  -d '{"chain":[]}'
curl -s -A 'Mozilla/5.0' https://temporallock-download-tracker.vibelock.workers.dev/v1/skill
\`\`\`

Grok: import the catalog OpenAPI as a custom tool. ChatGPT: GPT Actions. Venice: HTTP tools.

## Local (after one-click install)

\`\`\`bash
curl -fsSL https://temporallock-download-tracker.vibelock.workers.dev/install.sh | bash
temporallock ui
temporallock doctor
\`\`\`

Then open http://127.0.0.1:8766 (this computer only).

## Honest banner

THIS IS: an immutable timeslate lattice hash-chained against the StaticClock gear-click timeline, used as the AZ-OS integrity log. THIS IS NOT: a kernel, scheduler, truth score, court, or remote shell. The Worker does not store chains and does not run AZ-OS. Author Aziel Eliab.

DOI: https://doi.org/10.5281/zenodo.21431405  
Record: https://zenodo.org/records/21431405

Apache-2.0 (or the repo LICENSE). Forks are welcome and always allowed.

## Catalog + local UI

Author: **Aziel Eliab**. Honest scope: Timeslate lattice × StaticClock. AZ-OS integrity, not a kernel.

- Catalog product: https://aziel-runtime.vibelock.workers.dev/p/temporallock/
- Catalog OpenAPI: https://aziel-runtime.vibelock.workers.dev/openapi.json
- Catalog MCP: \`POST https://aziel-runtime.vibelock.workers.dev/mcp\`
- This Worker skill: \`GET https://temporallock-download-tracker.vibelock.workers.dev/v1/skill\`
- This Worker OpenAPI: https://temporallock-download-tracker.vibelock.workers.dev/openapi.json
- Sample payload: \`GET https://temporallock-download-tracker.vibelock.workers.dev/v1/example\`

Local UI: **Import JSON file** (\`type=file\`) and **Export JSON**. Then \`temporallock doctor\`.

Grok: import catalog or Worker OpenAPI as a custom tool. ChatGPT: GPT Actions. Venice: HTTP tools.

Counted download (gzip HTTP 200, no 302): https://temporallock-download-tracker.vibelock.workers.dev/download?asset=temporallock-0.2.0.tar.gz
GitHub: https://github.com/AzielEliab/temporallock
`;
const GENESIS_PREV_HASH = "0".repeat(64);
const CONFIDENCE_DECIMALS = 6;
const CONF_PLACEHOLDER = "__TL_CONFIDENCE__";

function corsHeaders() {
  return {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
  };
}

function json(body, status = 200) {
  return new Response(JSON.stringify(body, null, 2), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8", ...corsHeaders() },
  });
}

class ReceiptError extends Error {
  constructor(msg) { super(msg); this.name = "ReceiptError"; }
}
class ChainError extends Error {
  constructor(msg) { super(msg); this.name = "ChainError"; }
}

function formatConfidence(confidence) {
  return Number(confidence).toFixed(CONFIDENCE_DECIMALS);
}

function canonicalBytes(timestamp, summary, evidence, confidence, prev_hash) {
  const payload = {
    confidence: CONF_PLACEHOLDER,
    evidence,
    prev_hash,
    summary,
    timestamp,
  };
  const keys = Object.keys(payload).sort();
  let raw = "{" + keys.map((k) => JSON.stringify(k) + ":" + JSON.stringify(payload[k])).join(",") + "}";
  raw = raw.replace(`"${CONF_PLACEHOLDER}"`, formatConfidence(confidence));
  return new TextEncoder().encode(raw);
}

async function digest(timestamp, summary, evidence, confidence, prev_hash) {
  const bytes = canonicalBytes(timestamp, summary, evidence, confidence, prev_hash);
  const buf = await crypto.subtle.digest("SHA-256", bytes);
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

function requireHex64(name, value) {
  if (typeof value !== "string") throw new ReceiptError(`${name} must be a string`);
  const text = value.trim().toLowerCase();
  if (text.length !== 64 || /[^0-9a-f]/.test(text)) {
    throw new ReceiptError(`${name} must be 64 lowercase hex characters`);
  }
  return text;
}

function validateClickIndex(value) {
  const n = Number(value);
  if (!Number.isInteger(n) || n < 0) throw new ReceiptError("click_index must be an integer >= 0");
  return n;
}

function sortedJsonBytes(payload) {
  const keys = Object.keys(payload).sort();
  const raw = "{" + keys.map((k) => JSON.stringify(k) + ":" + JSON.stringify(payload[k])).join(",") + "}";
  return new TextEncoder().encode(raw);
}

async function sha256HexBytes(bytes) {
  const buf = await crypto.subtle.digest("SHA-256", bytes);
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

async function timeslateDigest(receiptHash, staticclockClick, prevTimeslateHash, clickIndex) {
  const payload = {
    click_index: validateClickIndex(clickIndex),
    prev_timeslate_hash: requireHex64("prev_timeslate_hash", prevTimeslateHash),
    receipt_hash: requireHex64("receipt_hash", receiptHash),
    staticclock_click: requireHex64("staticclock_click", staticclockClick),
  };
  return sha256HexBytes(sortedJsonBytes(payload));
}

async function staticclockClickDigest(payload) {
  const body = { ...(payload && typeof payload === "object" ? payload : {}) };
  body.product = "staticclock";
  if (body.kind == null) body.kind = "gear-click";
  return sha256HexBytes(sortedJsonBytes(body));
}

async function defaultGearClick(timestamp, clickIndex) {
  return staticclockClickDigest({ kind: "gear-click", timestamp, click_index: validateClickIndex(clickIndex) });
}

function prevTimeslateLink(prev) {
  if (!prev) return GENESIS_PREV_HASH;
  if (prev.timeslate_hash) return prev.timeslate_hash;
  return prev.hash;
}

function minClickIndex(prev) {
  if (!prev) return 0;
  if (prev.timeslate_hash || prev.staticclock_click) return prev.click_index || 0;
  return 0;
}

class LatticeError extends Error {
  constructor(msg) { super(msg); this.name = "LatticeError"; }
}

async function bindTimeslate(rec, prev, body) {
  const floor = minClickIndex(prev);
  let index;
  if (body.click_index == null || body.click_index === "") {
    index = prev ? floor + 1 : 0;
  } else {
    index = validateClickIndex(body.click_index);
  }
  if (index < floor) {
    throw new LatticeError(`StaticClock rollback refused: click_index ${index} < previous ${floor}`);
  }
  let click;
  if (body.staticclock_click) {
    click = requireHex64("staticclock_click", String(body.staticclock_click));
  } else if (body.click_payload && typeof body.click_payload === "object") {
    click = await staticclockClickDigest(body.click_payload);
  } else {
    click = await defaultGearClick(rec.timestamp, index);
  }
  const prevTl = prevTimeslateLink(prev);
  const tlHash = await timeslateDigest(rec.hash, click, prevTl, index);
  return {
    ...rec,
    staticclock_click: click,
    click_index: index,
    prev_timeslate_hash: prevTl,
    timeslate_hash: tlHash,
  };
}

function utcNow() {
  return new Date().toISOString().replace(/\.\d{3}Z$/, "Z");
}

function requireStr(name, value) {
  if (typeof value !== "string") throw new ReceiptError(`${name} must be a string`);
  return value;
}

function validateEvidence(evidence) {
  evidence = requireStr("evidence", evidence);
  if (evidence.trim() === "") throw new ReceiptError("empty evidence is invalid");
  return evidence;
}

function validateConfidence(confidence) {
  const value = Number(confidence);
  if (!Number.isFinite(value) || value < 0 || value > 1) {
    throw new ReceiptError("confidence must be a float in [0.0, 1.0] inclusive");
  }
  return value;
}

function validateSummary(summary) {
  return requireStr("summary", summary);
}

function validateTimestamp(timestamp) {
  const ts = requireStr("timestamp", timestamp);
  if (ts.trim() === "") throw new ReceiptError("timestamp must be a non-empty UTC ISO-8601 string");
  return ts;
}

async function createReceipt({ summary, evidence, confidence = 1.0, timestamp = null, prev_hash = GENESIS_PREV_HASH }) {
  const ts = timestamp == null ? utcNow() : timestamp;
  const conf = validateConfidence(confidence);
  const recHash = await digest(
    validateTimestamp(ts),
    validateSummary(summary),
    validateEvidence(evidence),
    conf,
    requireStr("prev_hash", prev_hash),
  );
  return {
    timestamp: ts,
    summary,
    evidence,
    confidence: conf,
    prev_hash,
    hash: recHash,
    staticclock_click: "",
    click_index: 0,
    prev_timeslate_hash: "",
    timeslate_hash: "",
  };
}

function receiptFromDict(data) {
  const missing = ["timestamp", "summary", "evidence", "confidence", "prev_hash", "hash"].filter((k) => !(k in data));
  if (missing.length) throw new ReceiptError(`receipt missing fields: ${missing}`);
  const rec = {
    timestamp: validateTimestamp(data.timestamp),
    summary: validateSummary(data.summary),
    evidence: validateEvidence(data.evidence),
    confidence: validateConfidence(data.confidence),
    prev_hash: requireStr("prev_hash", data.prev_hash),
    hash: requireStr("hash", data.hash),
    staticclock_click: data.staticclock_click ? String(data.staticclock_click) : "",
    click_index: data.click_index == null ? 0 : Number(data.click_index),
    prev_timeslate_hash: data.prev_timeslate_hash ? String(data.prev_timeslate_hash) : "",
    timeslate_hash: data.timeslate_hash ? String(data.timeslate_hash) : "",
  };
  return rec;
}

async function recomputedHash(rec) {
  return digest(rec.timestamp, rec.summary, rec.evidence, rec.confidence, rec.prev_hash);
}

function parseChain(body) {
  if (body == null) return [];
  let raw = body;
  if (typeof body === "string") {
    const text = body.trim();
    if (!text) return [];
    if (text.startsWith("[")) raw = JSON.parse(text);
    else {
      const rows = [];
      for (const line of text.split("\n")) {
        const t = line.trim();
        if (!t) continue;
        rows.push(JSON.parse(t));
      }
      return rows.map(receiptFromDict);
    }
  }
  if (Array.isArray(raw)) return raw.map(receiptFromDict);
  if (raw && typeof raw === "object") {
    if (Array.isArray(raw.chain)) return raw.chain.map(receiptFromDict);
    if (Array.isArray(raw.receipts)) return raw.receipts.map(receiptFromDict);
  }
  return [];
}

async function verify(receipts) {
  const errors = [];
  const n = receipts.length;
  const first = n ? receipts[0].hash : null;
  const last = n ? receipts[n - 1].hash : null;
  for (let i = 0; i < n; i++) {
    const rec = receipts[i];
    const expected = await recomputedHash(rec);
    if (rec.hash !== expected) {
      errors.push(`index ${i}: stored hash ${rec.hash} != recomputed ${expected}`);
    }
    if (i === 0) continue;
    const prev = receipts[i - 1];
    if (rec.prev_hash !== prev.hash) {
      errors.push(`index ${i}: prev_hash ${rec.prev_hash} != previous.hash ${prev.hash}`);
    }
  }
  return { ok: errors.length === 0, length: n, first_hash: first, last_hash: last, errors };
}

async function verifyLattice(receipts, receiptErrors) {
  const errors = Array.isArray(receiptErrors) ? [...receiptErrors] : [];
  const n = receipts.length;
  let bound = 0;
  let lastTl = null;
  let lastClick = null;
  for (let i = 0; i < n; i++) {
    const rec = receipts[i];
    if (!rec.timeslate_hash) {
      if (i > 0 && receipts[i - 1].timeslate_hash) {
        errors.push(`index ${i}: missing timeslate after lattice bind`);
      }
      continue;
    }
    bound += 1;
    let expected;
    try {
      expected = await timeslateDigest(rec.hash, rec.staticclock_click, rec.prev_timeslate_hash, rec.click_index);
    } catch (err) {
      errors.push(`index ${i}: ${err.message || err}`);
      continue;
    }
    if (rec.timeslate_hash !== expected) {
      errors.push(`index ${i}: stored timeslate_hash ${rec.timeslate_hash} != recomputed ${expected}`);
    }
    if (i === 0) {
      if (rec.prev_timeslate_hash !== GENESIS_PREV_HASH) {
        errors.push(`index 0: prev_timeslate_hash ${rec.prev_timeslate_hash} != genesis zeros`);
      }
    } else {
      const prev = receipts[i - 1];
      const expectedPrev = prevTimeslateLink(prev);
      if (rec.prev_timeslate_hash !== expectedPrev) {
        errors.push(`index ${i}: prev_timeslate_hash ${rec.prev_timeslate_hash} != previous timeslate ${expectedPrev}`);
      }
      const floor = minClickIndex(prev);
      if (rec.click_index < floor) {
        errors.push(`index ${i}: StaticClock rollback: click_index ${rec.click_index} < ${floor}`);
      }
    }
    lastTl = rec.timeslate_hash;
    lastClick = rec.click_index;
  }
  return {
    ok: errors.length === 0,
    length: n,
    bound,
    cross_hash: bound > 0,
    first_hash: n ? receipts[0].hash : null,
    last_hash: n ? receipts[n - 1].hash : null,
    last_timeslate_hash: lastTl,
    last_click_index: lastClick,
    errors,
    receipt_ok: !(receiptErrors && receiptErrors.length),
    role: ROLE,
    staticclock: STATICCLOCK_HOST,
    azos: AZOS_HOST,
    note: "Timeslate lattice integrity only. Receipts, not truth claims. AZ-OS prefab hooks may write here; this log does not execute software.",
  };
}

async function genesis(body) {
  const summary = body.summary;
  const evidence = body.evidence;
  if (summary == null) throw new ReceiptError("summary is required");
  if (evidence == null) throw new ReceiptError("evidence is required");
  const existing = parseChain(body.chain != null ? body.chain : body.receipts);
  if (existing.length) throw new ChainError("chain already exists; use append");
  let rec = await createReceipt({
    summary: String(summary),
    evidence: String(evidence),
    confidence: body.confidence == null ? 1.0 : body.confidence,
    timestamp: body.timestamp || null,
    prev_hash: GENESIS_PREV_HASH,
  });
  rec = await bindTimeslate(rec, null, body);
  return { product: PRODUCT, version: VERSION, motto: MOTTO, role: ROLE, author: AUTHOR, action: "genesis", receipt: rec, chain: [rec] };
}

async function append(body) {
  const receipts = parseChain(body.chain != null ? body : body.chain);
  // parseChain on full body also looks at body.chain / body.receipts
  const chain = parseChain(body);
  if (!chain.length) throw new ChainError("chain does not exist or is empty; use genesis");
  let rec = await createReceipt({
    summary: String(body.summary),
    evidence: String(body.evidence),
    confidence: body.confidence == null ? 0.7 : body.confidence,
    timestamp: body.timestamp || null,
    prev_hash: chain[chain.length - 1].hash,
  });
  rec = await bindTimeslate(rec, chain[chain.length - 1], body);
  return { product: PRODUCT, version: VERSION, motto: MOTTO, role: ROLE, author: AUTHOR, action: "appended", receipt: rec, chain: [...chain, rec] };
}

async function timeslate(body) {
  const chain = parseChain(body);
  if (!chain.length) return genesis(body);
  return append(body);
}

async function sha256Text(text) {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text == null ? "" : String(text)));
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

async function gate(body) {
  const content = body.content != null ? String(body.content) : (body.file_text != null ? String(body.file_text) : "");
  const fileName = body.file || body.name || "payload";
  const digestHex = body.sha256 || body.file_sha256 || await sha256Text(content);
  const evidence = `sha256:${digestHex} path:${fileName}`;
  const summary = body.summary || `gate accept ${fileName}`;
  let chain = parseChain(body);
  let rec;
  let action;
  if (!chain.length) {
    rec = await createReceipt({
      summary,
      evidence,
      confidence: body.confidence == null ? 1.0 : body.confidence,
      timestamp: body.timestamp || null,
      prev_hash: GENESIS_PREV_HASH,
    });
    rec = await bindTimeslate(rec, null, body);
    chain = [rec];
    action = "genesis";
  } else {
    rec = await createReceipt({
      summary,
      evidence,
      confidence: body.confidence == null ? 1.0 : body.confidence,
      timestamp: body.timestamp || null,
      prev_hash: chain[chain.length - 1].hash,
    });
    rec = await bindTimeslate(rec, chain[chain.length - 1], body);
    chain = [...chain, rec];
    action = "appended";
  }
  const result = await verifyLattice(chain, (await verify(chain)).errors);
  return {
    product: PRODUCT,
    version: VERSION,
    motto: MOTTO,
    role: ROLE,
    author: AUTHOR,
    ok: result.ok,
    accepted: Boolean(result.ok),
    action,
    file: fileName,
    file_sha256: digestHex,
    receipt: rec.hash,
    timeslate_hash: rec.timeslate_hash,
    click_index: rec.click_index,
    staticclock_click: rec.staticclock_click,
    length: result.length,
    bound: result.bound,
    errors: result.errors,
    chain,
  };
}

function openapiSpec() {
  const chainSchema = {
    oneOf: [
      { type: "array", items: { type: "object" } },
      { type: "string" },
    ],
  };
  return {
    openapi: "3.1.0",
    info: {
      title: "TemporalLock runtime",
      version: VERSION,
      description: "Immutable timeslate lattice hash-chained against StaticClock. AZ-OS integrity log. Client sends the chain JSON (stateless). " + MOTTO + " Author " + AUTHOR + ".",
    },
    servers: [{ url: HOST }],
    paths: {
      
      "/v1/skill": {
        get: {
          operationId: "temporallock_skill",
          summary: "Return skill markdown. Does not increment download KV.",
          responses: { "200": { description: "markdown" } },
        },
      },
"/v1/health": {
        get: { operationId: "health", summary: "Liveness", responses: { "200": { description: "ok", content: { "application/json": { schema: { type: "object" } } } } } },
      },
      "/v1/genesis": {
        post: {
          operationId: "genesis",
          summary: "Mint the first receipt (prev_hash = 64 zeros).",
          requestBody: { required: true, content: { "application/json": { schema: { type: "object", required: ["summary", "evidence"], properties: { summary: { type: "string" }, evidence: { type: "string" }, confidence: { type: "number" }, timestamp: { type: "string" }, staticclock_click: { type: "string" }, click_index: { type: "integer" } } } } } },
          responses: { "200": { description: "genesis", content: { "application/json": { schema: { type: "object" } } } } },
        },
      },
      "/v1/append": {
        post: {
          operationId: "append",
          summary: "Append a timeslate. Client sends the existing chain JSON. Decreasing click_index is refused.",
          requestBody: { required: true, content: { "application/json": { schema: { type: "object", required: ["summary", "evidence"], properties: { chain: chainSchema, receipts: chainSchema, summary: { type: "string" }, evidence: { type: "string" }, confidence: { type: "number" }, timestamp: { type: "string" }, staticclock_click: { type: "string" }, click_index: { type: "integer" } } } } } },
          responses: { "200": { description: "append", content: { "application/json": { schema: { type: "object" } } } } },
        },
      },
      "/v1/verify": {
        post: {
          operationId: "verify",
          summary: "Walk hashes and links. Receipts, not truth claims.",
          requestBody: { required: true, content: { "application/json": { schema: { type: "object", properties: { chain: chainSchema, receipts: chainSchema } } } } },
          responses: { "200": { description: "verify", content: { "application/json": { schema: { type: "object" } } } } },
        },
      },
      "/v1/timeslate": {
        post: {
          operationId: "timeslate",
          summary: "Genesis or append a StaticClock-bound timeslate.",
          requestBody: { required: true, content: { "application/json": { schema: { type: "object", required: ["summary", "evidence"], properties: { chain: chainSchema, summary: { type: "string" }, evidence: { type: "string" }, staticclock_click: { type: "string" }, click_index: { type: "integer" } } } } } },
          responses: { "200": { description: "timeslate", content: { "application/json": { schema: { type: "object" } } } } },
        },
      },
      "/v1/lattice": {
        post: {
          operationId: "lattice",
          summary: "Verify receipt links plus StaticClock timeslate binds. No rollbacks.",
          requestBody: { required: true, content: { "application/json": { schema: { type: "object", properties: { chain: chainSchema, receipts: chainSchema } } } } },
          responses: { "200": { description: "lattice", content: { "application/json": { schema: { type: "object" } } } } },
        },
      },
      "/v1/click": {
        post: {
          operationId: "click",
          summary: "Local SHA-256 of a StaticClock-shaped gear-click. No network.",
          requestBody: { content: { "application/json": { schema: { type: "object" } } } },
          responses: { "200": { description: "click", content: { "application/json": { schema: { type: "object" } } } } },
        },
      },
      "/v1/example": {
        get: {
          operationId: "example",
          summary: "Sample timeslate payload. Does not increment download KV.",
          responses: { "200": { description: "example", content: { "application/json": { schema: { type: "object" } } } } },
        },
      },
      "/v1/gate": {
        post: {
          operationId: "gate",
          summary: "Hash content, genesis or append, then verify. Stateless.",
          requestBody: { required: true, content: { "application/json": { schema: { type: "object", properties: { content: { type: "string" }, sha256: { type: "string" }, chain: chainSchema, summary: { type: "string" }, file: { type: "string" } } } } } },
          responses: { "200": { description: "gate", content: { "application/json": { schema: { type: "object" } } } } },
        },
      },
    },
  };
}

function aiHtml() {
  return `<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>TemporalLock — use with Grok, ChatGPT, Venice</title>
<style>
  :root { color-scheme: dark; }
  body { font: 16px/1.45 system-ui, sans-serif; max-width: 42rem; margin: 3rem auto; padding: 0 1.25rem; background: #0e1014; color: #e8eaef; }
  code { background: #151922; padding: .15rem .4rem; border-radius: 4px; }
  a { color: #c9d4ff; }
  .motto { color: #9aa3b2; font-style: italic; }
</style>
<body>
  <h1>TemporalLock live API</h1>
  <p class="motto">${MOTTO}</p>
  <p>Immutable timeslate lattice hash-chained against StaticClock. AZ-OS integrity log — not a kernel. Stateless: send the chain JSON in the body. The Worker does not store chains and does not run AZ-OS. Author ${AUTHOR}.</p>
  <p>StaticClock: <a href="${STATICCLOCK_HOST}/">${STATICCLOCK_HOST}</a> · AZ-OS: <a href="${AZOS_HOST}/">${AZOS_HOST}</a></p>
  <h2>ChatGPT (GPT Actions)</h2>
  <p>Paste this OpenAPI URL into GPT Actions:</p>
  <p><code>${HOST}/openapi.json</code></p>
  <h2>Grok / xAI</h2>
  <p>Custom tool pointing at <code>POST ${HOST}/v1/genesis</code>, <code>/v1/append</code>, <code>/v1/verify</code>, <code>/v1/gate</code>.</p>
  <h2>Venice</h2>
  <p>Custom HTTP tool from the same OpenAPI URL.</p>
  <h2>MCP catalog</h2>
  <p>The shared catalog (ships separately) is <code>https://aziel-runtime.vibelock.workers.dev/mcp</code>.</p>
  <p><a href="/openapi.json">openapi.json</a> · <a href="/v1/health">health</a> · <a href="/">downloads</a></p>
</body>
</html>`;
}

export async function handleRuntimeApi(request, url) {
  const path = url.pathname;
  const isApi = path === "/v1" || path.startsWith("/v1/") || path === "/openapi.json" || path === "/ai";
  if (!isApi) return null;
  try {
    if (path === "/v1/health" && request.method === "GET") {
      return json({
        ok: true,
        product: PRODUCT,
        version: VERSION,
        author: AUTHOR,
        role: ROLE,
        motto: MOTTO,
        staticclock: STATICCLOCK_HOST,
        azos: AZOS_HOST,
        note: "AZ-OS integrity lattice. Hosted /v1 does not run AZ-OS and does not store chains.",
      });
    }
    if (path === "/v1/skill" && request.method === "GET") {
      return new Response(SKILL, {
      status: 200,
      headers: { "Content-Type": "text/markdown; charset=utf-8", "Cache-Control": "private, no-store", ...corsHeaders() },
      });
  }
    if (path === "/openapi.json" && request.method === "GET") return json(openapiSpec());
    if (path === "/ai" && request.method === "GET") {
      return new Response(aiHtml(), { headers: { "Content-Type": "text/html; charset=utf-8", ...corsHeaders() } });
    }
    if (path === "/v1/genesis" && request.method === "POST") {
      let body;
      try { body = await request.json(); } catch { return json({ error: "JSON body required" }, 400); }
      return json(await genesis(body));
    }
    if (path === "/v1/append" && request.method === "POST") {
      let body;
      try { body = await request.json(); } catch { return json({ error: "JSON body required" }, 400); }
      return json(await append(body));
    }
    if (path === "/v1/verify" && request.method === "POST") {
      let body;
      try { body = await request.json(); } catch { return json({ error: "JSON body required" }, 400); }
      const chain = parseChain(body);
      const result = await verify(chain);
      return json({ product: PRODUCT, version: VERSION, motto: MOTTO, role: ROLE, author: AUTHOR, ...result });
    }
    if (path === "/v1/lattice" && request.method === "POST") {
      let body;
      try { body = await request.json(); } catch { return json({ error: "JSON body required" }, 400); }
      const chain = parseChain(body);
      const rec = await verify(chain);
      return json({ product: PRODUCT, version: VERSION, motto: MOTTO, author: AUTHOR, ...(await verifyLattice(chain, rec.errors)) });
    }
    if (path === "/v1/timeslate" && request.method === "POST") {
      let body;
      try { body = await request.json(); } catch { return json({ error: "JSON body required" }, 400); }
      return json(await timeslate(body));
    }
    if (path === "/v1/click" && request.method === "POST") {
      let body;
      try { body = await request.json(); } catch { body = {}; }
      const click = await staticclockClickDigest(body && typeof body === "object" ? body : {});
      return json({
        product: PRODUCT,
        version: VERSION,
        author: AUTHOR,
        staticclock_click: click,
        host: STATICCLOCK_HOST,
        note: "Local digest only. TemporalLock does not call StaticClock.",
      });
    }
    if (path === "/v1/example" && request.method === "GET") {
      return json({
        summary: "observed package release",
        evidence: "sha256:abc path:README.md",
        confidence: 1.0,
        click_index: 0,
        note: "POST this to /v1/genesis. Optional staticclock_click is a 64-hex StaticClock gear-click.",
        author: AUTHOR,
      });
    }
    if (path === "/v1/gate" && request.method === "POST") {
      let body;
      try { body = await request.json(); } catch { return json({ error: "JSON body required" }, 400); }
      return json(await gate(body));
    }
    return json({ error: "not found" }, 404);
  } catch (err) {
    const status = err instanceof ReceiptError || err instanceof ChainError || err instanceof LatticeError ? 400 : 400;
    return json({ error: String(err.message || err), motto: MOTTO }, status);
  }
}
