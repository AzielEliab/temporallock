/**
 * TemporalLock hosted runtime (port of canon/receipt/chain).
 * Stateless: client sends the chain JSON in the body. Receipts not truth claims.
 * /v1 never touches DOWNLOADS KV.
 */
const PRODUCT = "temporallock";
const VERSION = "0.1.0";
const MOTTO = "Receipts, not truth claims.";
const HOST = "https://temporallock-download-tracker.vibelock.workers.dev";
const SKILL = "---\nname: TemporalLock\ndescription: Use when minting or verifying append-only observation receipts. Receipts, not truth claims. Hosted API is stateless. Hosted /v1 via this Worker or aziel-runtime. Author Aziel Eliab.\n---\n\n# TemporalLock\n\nReceipts, not truth claims.\n\nAuthor: **Aziel Eliab**.\n\nUse when minting or verifying append-only observation receipts. Receipts, not truth claims. Hosted API is stateless.\n\nAlways send `User-Agent: Mozilla/5.0`. Cloudflare Workers may 403 an empty agent.\n\n## Endpoints (this Worker)\n\nHost: `https://temporallock-download-tracker.vibelock.workers.dev`\n\n| Method | Path | What |\n|--------|------|------|\n| GET | `/v1/health` | Liveness. Does not increment downloads. |\n| GET | `/v1/skill` | This markdown. Does not increment downloads. |\n| POST | `/v1/genesis` | Start a chain. Body includes summary + evidence. |\n| POST | `/v1/append` | Append a receipt. Client sends the chain. |\n| POST | `/v1/verify` | Verify hashes and prev links. Not stored. |\n| POST | `/v1/gate` | File-gate preview (hash + receipt). |\n\nOpenAPI: `https://temporallock-download-tracker.vibelock.workers.dev/openapi.json`\n\nCatalog OpenAPI: `https://aziel-runtime.vibelock.workers.dev/openapi.json`\n\nMCP: `POST https://aziel-runtime.vibelock.workers.dev/mcp`\n\nCatalog aliases under `/p/temporallock/\u2026`.\n\n## How to call (Mozilla/5.0)\n\n```bash\ncurl -s -A 'Mozilla/5.0' https://temporallock-download-tracker.vibelock.workers.dev/v1/health\ncurl -s -A 'Mozilla/5.0' -X POST https://temporallock-download-tracker.vibelock.workers.dev/v1/genesis \\\n  -H 'content-type: application/json' \\\n  -d '{\"summary\":\"desk closed\",\"evidence\":\"log row\"}'\ncurl -s -A 'Mozilla/5.0' https://temporallock-download-tracker.vibelock.workers.dev/v1/skill\n```\n\nGrok: import the catalog OpenAPI as a custom tool. ChatGPT: GPT Actions. Venice: HTTP tools.\n\n## Local (after one-click install)\n\n```bash\ncurl -fsSL https://temporallock-download-tracker.vibelock.workers.dev/install.sh | bash\ntemporallock ui\n```\n\nThen open http://127.0.0.1:8766 (this computer only).\n\n## Honest banner\n\nTHIS IS: append-only observation receipts with evidence and confidence. THIS IS NOT: a truth score, court, narrative engine, or authority. The Worker does not store chains. Author Aziel Eliab.\n\nDOI: https://doi.org/10.5281/zenodo.21431405  \nRecord: https://zenodo.org/records/21431405\n\nApache-2.0 (or the repo LICENSE). Forks are welcome and always allowed.\n";

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
  };
}

function receiptFromDict(data) {
  const missing = ["timestamp", "summary", "evidence", "confidence", "prev_hash", "hash"].filter((k) => !(k in data));
  if (missing.length) throw new ReceiptError(`receipt missing fields: ${missing}`);
  return {
    timestamp: validateTimestamp(data.timestamp),
    summary: validateSummary(data.summary),
    evidence: validateEvidence(data.evidence),
    confidence: validateConfidence(data.confidence),
    prev_hash: requireStr("prev_hash", data.prev_hash),
    hash: requireStr("hash", data.hash),
  };
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

async function genesis(body) {
  const summary = body.summary;
  const evidence = body.evidence;
  if (summary == null) throw new ReceiptError("summary is required");
  if (evidence == null) throw new ReceiptError("evidence is required");
  const existing = parseChain(body.chain != null ? body.chain : body.receipts);
  if (existing.length) throw new ChainError("chain already exists; use append");
  const rec = await createReceipt({
    summary: String(summary),
    evidence: String(evidence),
    confidence: body.confidence == null ? 1.0 : body.confidence,
    timestamp: body.timestamp || null,
    prev_hash: GENESIS_PREV_HASH,
  });
  return { product: PRODUCT, version: VERSION, motto: MOTTO, action: "genesis", receipt: rec, chain: [rec] };
}

async function append(body) {
  const receipts = parseChain(body.chain != null ? body : body.chain);
  // parseChain on full body also looks at body.chain / body.receipts
  const chain = parseChain(body);
  if (!chain.length) throw new ChainError("chain does not exist or is empty; use genesis");
  const rec = await createReceipt({
    summary: String(body.summary),
    evidence: String(body.evidence),
    confidence: body.confidence == null ? 0.7 : body.confidence,
    timestamp: body.timestamp || null,
    prev_hash: chain[chain.length - 1].hash,
  });
  return { product: PRODUCT, version: VERSION, motto: MOTTO, action: "appended", receipt: rec, chain: [...chain, rec] };
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
    chain = [...chain, rec];
    action = "appended";
  }
  const result = await verify(chain);
  return {
    product: PRODUCT,
    version: VERSION,
    motto: MOTTO,
    ok: result.ok,
    accepted: Boolean(result.ok),
    action,
    file: fileName,
    file_sha256: digestHex,
    receipt: rec.hash,
    length: result.length,
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
      description: "Append-only observation receipts. Client sends the chain JSON (stateless). " + MOTTO,
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
          requestBody: { required: true, content: { "application/json": { schema: { type: "object", required: ["summary", "evidence"], properties: { summary: { type: "string" }, evidence: { type: "string" }, confidence: { type: "number" }, timestamp: { type: "string" } } } } } },
          responses: { "200": { description: "genesis", content: { "application/json": { schema: { type: "object" } } } } },
        },
      },
      "/v1/append": {
        post: {
          operationId: "append",
          summary: "Append a receipt. Client sends the existing chain JSON.",
          requestBody: { required: true, content: { "application/json": { schema: { type: "object", required: ["summary", "evidence"], properties: { chain: chainSchema, receipts: chainSchema, summary: { type: "string" }, evidence: { type: "string" }, confidence: { type: "number" }, timestamp: { type: "string" } } } } } },
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
  <p>Stateless: send the chain JSON in the body. Hash+link as in the Python core. The Worker does not store chains.</p>
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
      return json({ ok: true, product: PRODUCT, version: VERSION });
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
      return json({ product: PRODUCT, version: VERSION, motto: MOTTO, ...result });
    }
    if (path === "/v1/gate" && request.method === "POST") {
      let body;
      try { body = await request.json(); } catch { return json({ error: "JSON body required" }, 400); }
      return json(await gate(body));
    }
    return json({ error: "not found" }, 404);
  } catch (err) {
    const status = err instanceof ReceiptError || err instanceof ChainError ? 400 : 400;
    return json({ error: String(err.message || err), motto: MOTTO }, status);
  }
}
