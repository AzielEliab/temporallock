/**
 * TemporalLock product homepage — software UI, not a downloads shell.
 * Author: Aziel Eliab only. Apache-2.0. Forks welcome.
 * Historical Zenodo DOI is tombstoned; no DOI is invented here.
 */

const HOST = "https://temporallock-download-tracker.vibelock.workers.dev";
const GITHUB_REPO = "https://github.com/AzielEliab/temporallock";
const GITHUB_LATEST = "https://github.com/AzielEliab/temporallock/releases/latest";
const CATALOG = "https://aziel-runtime.vibelock.workers.dev/";
const CATALOG_PRODUCT = "https://aziel-runtime.vibelock.workers.dev/p/temporallock/";
const STATICCLOCK_HOST = "https://staticclock-download-tracker.vibelock.workers.dev";
const AZOS_HOST = "https://azos-download-tracker.vibelock.workers.dev";
const LICENSE = "https://www.apache.org/licenses/LICENSE-2.0";
const VERSION = "0.2.0";
const AUTHOR = "Aziel Eliab";
const TITLE = "TemporalLock — Aziel Eliab";
const DEFAULT_ASSET = "temporallock-0.2.0.tar.gz";
const INSTALL_LINE = "curl -fsSL https://temporallock-download-tracker.vibelock.workers.dev/install.sh | bash";
const HISTORICAL_DOI = "10.5281/zenodo.21431405";
const DESCRIPTION =
  "TemporalLock is Aziel Eliab software: an immutable timeslate lattice of hash-chained receipts anyone can verify. Explicit genesis, append, and verify. Receipts, not truth claims. Apache-2.0.";
const HONEST =
  "THIS IS: an immutable timeslate lattice hash-chained against the StaticClock gear-click timeline, used as the AZ-OS integrity log. THIS IS NOT: a kernel, scheduler, truth score, court, or remote shell. The Worker does not store chains and does not run AZ-OS. Hosted /v1 is stateless: this browser holds the chain. Author Aziel Eliab.";
const HOW_TO_CITE =
  "Eliab, Aziel. (2026). TemporalLock 0.2.0 [Software]. Apache-2.0. https://github.com/AzielEliab/temporallock · https://temporallock-download-tracker.vibelock.workers.dev/";

function corsHeaders() {
  return {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
  };
}

function escapeHtml(value) {
  return String(value == null ? "" : value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

export function citePayload() {
  return {
    author: AUTHOR,
    title: "TemporalLock",
    version: VERSION,
    homepage: HOST + "/",
    github: GITHUB_REPO,
    download: HOST + "/download",
    install: HOST + "/install.sh",
    openapi: HOST + "/openapi.json",
    skill: HOST + "/v1/skill",
    catalog: CATALOG,
    catalog_product: CATALOG_PRODUCT,
    license: "Apache-2.0",
    license_url: LICENSE,
    one_line: DESCRIPTION,
    how_to_cite: HOW_TO_CITE,
    apa: "Eliab, A. (2026). TemporalLock (Version 0.2.0) [Computer software]. https://temporallock-download-tracker.vibelock.workers.dev/",
    bibtex:
      "@software{eliab_temporallock_2026, author = {Eliab, Aziel}, title = {TemporalLock}, version = {0.2.0}, year = {2026}, license = {Apache-2.0}, url = {https://temporallock-download-tracker.vibelock.workers.dev/}, publisher = {GitHub}, howpublished = {\\url{https://github.com/AzielEliab/temporallock}}}",
    historical_doi: HISTORICAL_DOI,
    historical_doi_url: "https://doi.org/" + HISTORICAL_DOI,
    zenodo_status: "historical_doi_tombstoned",
    software_deposit_needed: true,
    note: "Known DOI 10.5281/zenodo.21431405 is a historical Zenodo record and is not currently resolvable. No DOI is invented here. Cite GitHub and this Worker. Identity is Aziel Eliab only. Forks welcome.",
    identity: "Aziel Eliab only",
    forks: "welcome and always allowed",
  };
}

export function jsonLd() {
  return {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    name: "TemporalLock",
    alternateName: TITLE,
    applicationCategory: "DeveloperApplication",
    operatingSystem: "Linux, macOS, Windows, Cloudflare Workers",
    softwareVersion: VERSION,
    author: { "@type": "Person", name: AUTHOR, url: "https://github.com/AzielEliab" },
    creator: { "@type": "Person", name: AUTHOR, url: "https://github.com/AzielEliab" },
    codeRepository: GITHUB_REPO,
    downloadUrl: HOST + "/download",
    installUrl: HOST + "/install.sh",
    license: LICENSE,
    url: HOST + "/",
    description: DESCRIPTION,
    keywords:
      "TemporalLock, timeslate lattice, hash-chained receipts, Aziel Eliab, StaticClock, AZ-OS, genesis, append, verify",
    isAccessibleForFree: true,
    offers: { "@type": "Offer", price: "0", priceCurrency: "USD" },
    sameAs: [GITHUB_REPO, CATALOG_PRODUCT],
  };
}

function sitemapXml() {
  const paths = [
    "/",
    "/download",
    "/install.sh",
    "/v1/skill",
    "/v1/example",
    "/v1/health",
    "/openapi.json",
    "/cite.json",
    "/llms.txt",
    "/ai",
  ];
  const urls = paths
    .map((p) => `  <url><loc>${HOST}${p === "/" ? "/" : p}</loc></url>`)
    .join("\n");
  return `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls}
  <url><loc>${GITHUB_REPO}</loc></url>
</urlset>
`;
}

function robotsTxt() {
  return `User-agent: *
Allow: /

User-agent: GPTBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: anthropic-ai
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Bytespider
Allow: /

User-agent: CCBot
Allow: /

User-agent: Applebot-Extended
Allow: /

User-agent: meta-externalagent
Allow: /

User-agent: FacebookBot
Allow: /

User-agent: cohere-ai
Allow: /

User-agent: Diffbot
Allow: /

User-agent: Omgilibot
Allow: /

User-agent: Amazonbot
Allow: /

Sitemap: ${HOST}/sitemap.xml
`;
}

function llmsTxt() {
  return `# TemporalLock

Author: Aziel Eliab
One-line: ${DESCRIPTION}
GitHub: ${GITHUB_REPO}
Homepage: ${HOST}/
Download: ${HOST}/download
Install: ${HOST}/install.sh
OpenAPI: ${HOST}/openapi.json
Skill: ${HOST}/v1/skill
Cite: ${HOST}/cite.json
Ops: POST /v1/genesis, POST /v1/append, POST /v1/verify, POST /v1/lattice
Identity: Aziel Eliab only
License: Apache-2.0
Forks: welcome and always allowed
DOI: historical ${HISTORICAL_DOI} is tombstoned; no DOI is invented here.

Indexing, metadata scrape, and AI grounding of public pages are allowed.
`;
}

export function handleSeoRoutes(request, url) {
  if (request.method !== "GET" && request.method !== "HEAD") return null;
  const headers = { ...corsHeaders(), "Cache-Control": "private, no-store" };
  if (url.pathname === "/cite.json") {
    return new Response(JSON.stringify(citePayload(), null, 2), {
      status: 200,
      headers: { "Content-Type": "application/json; charset=utf-8", ...headers },
    });
  }
  if (url.pathname === "/sitemap.xml") {
    return new Response(sitemapXml(), {
      status: 200,
      headers: { "Content-Type": "application/xml; charset=utf-8", ...headers },
    });
  }
  if (url.pathname === "/robots.txt") {
    return new Response(robotsTxt(), {
      status: 200,
      headers: { "Content-Type": "text/plain; charset=utf-8", ...headers },
    });
  }
  if (url.pathname === "/llms.txt" || url.pathname === "/ai.txt") {
    return new Response(llmsTxt(), {
      status: 200,
      headers: { "Content-Type": "text/plain; charset=utf-8", ...headers },
    });
  }
  return null;
}

function breakdownList(stats) {
  const rows = stats.breakdown || [];
  if (!rows.length) return "<li>none yet</li>";
  return rows
    .map(
      (b) =>
        `<li><code>${escapeHtml(b.owner)}/${escapeHtml(b.repo)}</code> branch <code>${escapeHtml(b.branch)}</code> fork=${escapeHtml(b.fork)} → ${escapeHtml(b.count)}</li>`,
    )
    .join("");
}

export function renderHome(stats) {
  const views = Number(stats.views) || 0;
  const downloads = Number(stats.downloads != null ? stats.downloads : stats.total) || 0;
  const v = views.toLocaleString("en-US");
  const n = downloads.toLocaleString("en-US");
  const gh = stats.github || {};
  const ld = JSON.stringify(jsonLd());
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${TITLE}</title>
<meta name="description" content="${escapeHtml(DESCRIPTION)}">
<meta name="author" content="${AUTHOR}">
<meta name="robots" content="index,follow">
<link rel="canonical" href="${HOST}/">
<link rel="sitemap" type="application/xml" href="${HOST}/sitemap.xml">
<link rel="icon" type="image/png" href="/sigil.png">
<meta property="og:type" content="website">
<meta property="og:title" content="${TITLE}">
<meta property="og:description" content="${escapeHtml(DESCRIPTION)}">
<meta property="og:url" content="${HOST}/">
<meta property="og:site_name" content="Aziel Eliab">
<meta property="og:image" content="${HOST}/sigil.png">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="${TITLE}">
<meta name="twitter:description" content="${escapeHtml(DESCRIPTION)}">
<meta name="twitter:image" content="${HOST}/sigil.png">
<script type="application/ld+json">${ld}</script>
<style>
  :root {
    color-scheme: dark;
    --bg: #0b0c10;
    --panel: #141720;
    --ink: #f3efe3;
    --muted: #9aa3b2;
    --line: #2a3140;
    --gold: #d4af37;
    --gold-dim: #c9a227;
    --pass: #3dba7a;
    --bad: #d4534b;
    --focus: #e6d19a;
  }
  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; background: var(--bg); color: var(--ink); }
  body { font: 16px/1.5 system-ui, "Segoe UI", sans-serif; }
  a { color: #e6d19a; }
  code, pre, .mono { font-family: ui-monospace, Menlo, Consolas, monospace; }
  .wrap { max-width: 58rem; margin: 0 auto; padding: 1.4rem 1.2rem 4.5rem; }
  .brandrow { display: flex; align-items: center; gap: 12px; margin: 0 0 12px; }
  .brandmark {
    width: 40px; height: 40px; border-radius: 10px; object-fit: cover; flex: 0 0 auto;
    box-shadow: 0 0 0 1px #d4af3733;
  }
  .stamp { margin: 0; color: var(--gold); font-size: .88rem; letter-spacing: .02em; }
  .appbar { display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; flex-wrap: wrap; }
  h1 { font-size: 2rem; letter-spacing: .02em; margin: 0 0 .2rem; }
  .motto { color: var(--gold); font-style: italic; margin: 0 0 .7rem; }
  .lede { color: var(--muted); margin: 0 0 1rem; max-width: 46rem; }
  .pill {
    font: 650 .78rem/1 ui-monospace, Menlo, Consolas, monospace;
    letter-spacing: .06em; text-transform: uppercase;
    border: 1px solid var(--line); border-radius: 999px; padding: .4rem .7rem;
    color: var(--muted); background: #10131a;
  }
  .pill.ok { color: var(--pass); border-color: #2f6b48; }
  .pill.bad { color: var(--bad); border-color: #7a2f2c; }
  nav.toc { display: flex; flex-wrap: wrap; gap: .55rem; margin: 0 0 1.1rem; }
  nav.toc a {
    text-decoration: none; color: var(--ink); border: 1px solid var(--line);
    background: var(--panel); border-radius: 999px; padding: .35rem .75rem; font-size: .88rem;
  }
  .banner {
    border: 1px solid #5c4a1a; background: #241c0d; color: #f0d78c;
    padding: .9rem 1rem; border-radius: 10px; margin: 0 0 1.15rem; font-size: .94rem;
  }
  .card, .workspace, .cite {
    border: 1px solid var(--line); border-radius: 14px; padding: 1.15rem 1.2rem 1.25rem;
    background: var(--panel); margin: 0 0 1.1rem;
  }
  .workspace { box-shadow: 0 0 0 1px #d4af3714, 0 16px 40px #0006; }
  h2 { font-size: 1.12rem; margin: 0 0 .45rem; letter-spacing: .04em; }
  .kicker { display: block; font-size: .68rem; letter-spacing: .12em; text-transform: uppercase; color: var(--gold); margin-bottom: .15rem; font-family: ui-monospace, Menlo, Consolas, monospace; }
  .workgrid { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1.05fr); gap: 1rem; }
  @media (max-width: 820px) { .workgrid { grid-template-columns: 1fr; } }
  label { display: block; font-size: .92rem; margin: .75rem 0 .28rem; }
  input[type="text"], input[type="number"], textarea {
    width: 100%; padding: .58rem .7rem; border: 1px solid var(--line); border-radius: 8px;
    background: #0e1014; color: var(--ink); font: inherit;
  }
  input:focus, textarea:focus { outline: 2px solid var(--focus); outline-offset: 1px; }
  .row2 { display: grid; grid-template-columns: 1fr 1fr; gap: .7rem; }
  @media (max-width: 520px) { .row2 { grid-template-columns: 1fr; } }
  .actions { display: flex; flex-wrap: wrap; gap: .5rem; margin: .95rem 0 .2rem; }
  button, a.btn {
    font: 700 .88rem/1.1 ui-monospace, Menlo, Consolas, monospace;
    letter-spacing: .03em; padding: .72rem .9rem; border-radius: 9px;
    border: 1px solid transparent; cursor: pointer; text-decoration: none; display: inline-block;
  }
  button.gold, a.btn.gold { background: var(--gold-dim); color: #14110a; }
  button.ink, a.btn.ink { background: var(--ink); color: var(--bg); }
  button.ghost, a.btn.ghost, label.filebtn {
    background: transparent; color: var(--ink); border-color: var(--line);
  }
  button.copied { background: var(--pass); color: #0e1014; }
  label.filebtn { padding: .72rem .9rem; border-radius: 9px; cursor: pointer; font: 700 .88rem/1.1 ui-monospace, Menlo, Consolas, monospace; }
  label.filebtn input { display: none; }
  .status {
    margin: 0 0 .8rem; padding: .75rem .85rem; border-radius: 10px;
    border: 1px solid var(--line); background: #10131a; color: var(--muted);
  }
  .status.ok { color: var(--pass); border-color: #2f6b48; }
  .status.bad { color: var(--bad); border-color: #7a2f2c; }
  .metrics { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: .55rem; margin: 0 0 .85rem; }
  @media (max-width: 720px) { .metrics { grid-template-columns: 1fr 1fr; } }
  .metric { border: 1px solid var(--line); border-radius: 10px; padding: .55rem .65rem; background: #10131a; }
  .metric b { display: block; font-size: .72rem; color: var(--muted); font-weight: 600; letter-spacing: .04em; text-transform: uppercase; }
  .metric span { display: block; font-size: .78rem; word-break: break-all; color: var(--ink); }
  ol.receipts { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: .65rem; }
  .receipt {
    border: 1px solid var(--line); border-radius: 10px; padding: .75rem .85rem;
    background: #10131a; position: relative;
  }
  .receipt::before {
    content: ""; position: absolute; left: -1px; top: 0; bottom: 0; width: 3px;
    background: var(--gold); border-radius: 10px 0 0 10px;
  }
  .receipt h3 { margin: 0 0 .25rem; font-size: .95rem; }
  .receipt p { margin: .2rem 0; }
  .hash { font-size: .72rem; word-break: break-all; color: var(--muted); }
  .nums { display: grid; grid-template-columns: 1fr 1fr; gap: .8rem; margin: 0 0 1rem; }
  .count { font-size: 2.1rem; font-variant-numeric: tabular-nums; font-weight: 700; margin: 0; }
  .count span { display: block; font-size: .92rem; font-weight: 500; color: var(--muted); }
  .btns { display: grid; grid-template-columns: 1fr 1fr; gap: .75rem; margin: 0 0 .85rem; }
  @media (max-width: 520px) { .btns { grid-template-columns: 1fr; } }
  a.btn.block, button.btn.block {
    display: block; width: 100%; text-align: center; font-size: 1.15rem; padding: 1rem 1.1rem;
  }
  a.btn.primary { background: #e8eaef; color: #0e1014; }
  button.btn.install { background: var(--gold-dim); color: #14110a; }
  pre { background: #0e1014; padding: .75rem .9rem; overflow: auto; border-radius: 8px; font-size: .82rem; }
  .meta { margin-top: 1rem; color: var(--muted); font-size: .92rem; }
  .iso { margin-top: .75rem; font-size: .85rem; color: #7d8696; }
  details.raw { margin-top: .8rem; }
  details.raw pre { max-height: 18rem; }
  footer { color: var(--muted); font-size: .9rem; }
</style>
</head>
<body>
  <div class="wrap">
    <header>
      <div class="brandrow">
        <img class="brandmark" src="/sigil.png" width="40" height="40" alt="Everblooming sigil — Aziel Eliab" decoding="async">
        <p class="stamp">Everblooming sigil · Aziel Eliab</p>
      </div>
      <div class="appbar">
        <div>
          <h1>TemporalLock</h1>
          <p class="motto">Immutable timeslate lattice. Receipts, not truth claims.</p>
        </div>
        <p class="pill" id="api-pill">API · checking</p>
      </div>
      <p class="lede">v${VERSION} software by <strong>${AUTHOR}</strong> only. Genesis writes the first receipt. Append extends the chain you hold. Verify recomputes hashes. Anyone can check. Forks are welcome and always allowed.</p>
      <nav class="toc" aria-label="Product sections">
        <a href="#workspace">Workspace</a>
        <a href="#install">Download / install</a>
        <a href="#cite">Cite</a>
        <a href="/v1/skill">Skill</a>
        <a href="/openapi.json">OpenAPI</a>
        <a href="${GITHUB_REPO}">GitHub</a>
      </nav>
      <p class="banner">${escapeHtml(HONEST)}</p>
    </header>

    <section class="workspace" id="workspace">
      <h2><span class="kicker">Live software</span>Timeslate workspace</h2>
      <p class="lede">Real TemporalLock ops on this Worker: <code>POST /v1/genesis</code>, <code>/v1/append</code>, <code>/v1/verify</code>, <code>/v1/lattice</code>, <code>/v1/gate</code>. The Worker does not store your chain. This page keeps it in this browser until you export it.</p>
      <div class="workgrid">
        <form id="ws-form" autocomplete="off">
          <label for="summary"><span class="kicker">Summary</span> Brief note of what was observed.</label>
          <input id="summary" type="text" placeholder="sky was overcast" value="sky was overcast">
          <label for="evidence"><span class="kicker">Evidence</span> Supporting body and/or URI. Required. Empty is invalid.</label>
          <textarea id="evidence" rows="3" placeholder="photo:./sky.jpg">photo:./sky.jpg</textarea>
          <div class="row2">
            <div>
              <label for="confidence"><span class="kicker">Confidence</span> Observer float in [0, 1].</label>
              <input id="confidence" type="number" min="0" max="1" step="0.01" value="0.9">
            </div>
            <div>
              <label for="click-index"><span class="kicker">Click index</span> Optional. Must not decrease.</label>
              <input id="click-index" type="number" min="0" step="1" placeholder="auto">
            </div>
          </div>
          <label for="gate-text"><span class="kicker">Gate content</span> Optional text hashed by <code>/v1/gate</code>.</label>
          <textarea id="gate-text" rows="2" placeholder="file bytes or note"></textarea>
          <div class="actions">
            <button type="button" class="gold" id="btn-genesis">Genesis</button>
            <button type="button" class="ink" id="btn-append">Append</button>
            <button type="button" class="ghost" id="btn-verify">Verify</button>
            <button type="button" class="ghost" id="btn-lattice">Lattice</button>
            <button type="button" class="ghost" id="btn-gate">Gate</button>
            <label class="filebtn">Import JSON <input type="file" id="import-json" accept="application/json,.json,.jsonl"></label>
            <button type="button" class="ghost" id="btn-export">Export</button>
            <button type="button" class="ghost" id="btn-clear">Clear local chain</button>
          </div>
        </form>
        <div>
          <div class="status" id="ws-status">No timeslates yet. Genesis writes the first lattice node.</div>
          <div class="metrics">
            <div class="metric"><b>Length</b><span id="chain-length">0</span></div>
            <div class="metric"><b>Click</b><span id="last-click">—</span></div>
            <div class="metric"><b>Last hash</b><span id="last-hash">—</span></div>
            <div class="metric"><b>Timeslate</b><span id="last-tl">—</span></div>
          </div>
          <ol class="receipts" id="receipt-list"></ol>
          <details class="raw">
            <summary>Raw API result</summary>
            <pre id="raw-json">{}</pre>
          </details>
        </div>
      </div>
    </section>

    <section class="card" id="install">
      <h2><span class="kicker">Counted package</span>Download and one-click install</h2>
      <div class="nums">
        <p class="count">${v}<span>Views</span></p>
        <p class="count">${n}<span>Downloads</span></p>
      </div>
      <p>Download saves the gzip from this Worker (HTTP 200, counted). One-click install copies a Terminal command. After it finishes, run <code>temporallock ui</code> and open http://127.0.0.1:8766 on this computer only.</p>
      <div class="btns">
        <a class="btn block primary" href="/download?asset=${DEFAULT_ASSET}">Download</a>
        <button type="button" class="btn block install" id="install-btn">One-click install</button>
      </div>
      <pre id="install-cmd">${INSTALL_LINE}</pre>
      <p class="meta">The download count ticks on the Download click. No 302 to GitHub. Forks using this same link are counted automatically. ${DEFAULT_ASSET} — ${n} counted.</p>
      <p class="iso">Isolated counter: Worker <code>temporallock-download-tracker</code>, project <code>temporallock</code>, KV <code>TEMPORALLOCK_DOWNLOADS</code>. Not mixed with any other product. /v1 does not increment downloads.</p>
      <p class="meta">GitHub: stars ${gh.stars || 0} · forks ${gh.forks || 0} · watchers ${gh.watchers || 0} · release assets ${gh.release_download_count || 0}</p>
      <p class="meta">Cross-hash: <a href="${STATICCLOCK_HOST}/">StaticClock</a> gear-click timeline (no rollbacks). Integrity role: <a href="${AZOS_HOST}/">AZ-OS</a> prefab hooks write this lattice — TemporalLock does not execute software.</p>
      <p class="meta"><a href="/stats">JSON stats</a> · <a href="/openapi.json">OpenAPI</a> · <a href="/v1/skill">Skill</a> · <a href="/v1/example">Example</a> · <a href="/ai">AI runtime</a> · <a href="${GITHUB_REPO}">GitHub</a> · <a href="${GITHUB_LATEST}">releases</a></p>
      <h3>Per repo / branch / fork</h3>
      <ul>${breakdownList(stats)}</ul>
    </section>

    <section class="cite" id="cite">
      <h2>How to cite</h2>
      <p>${escapeHtml(HOW_TO_CITE)}</p>
      <p>Author: <strong>${AUTHOR}</strong> only · License: Apache-2.0 · Forks welcome and always allowed · Machine-readable: <a href="/cite.json">/cite.json</a></p>
      <p class="meta">Historical DOI <code>${HISTORICAL_DOI}</code> is a tombstoned Zenodo record and is not currently resolvable. No DOI is invented here. Software deposit still needed. Cite GitHub and this Worker.</p>
      <p><a href="${CATALOG}">Catalog</a> · <a href="${CATALOG_PRODUCT}">Catalog product</a> · <a href="${GITHUB_REPO}">GitHub</a> · <a href="${HOST}/download">Download</a> · <a href="/llms.txt">llms.txt</a></p>
    </section>

    <footer>
      <p>Apache-2.0 · ${AUTHOR} · TemporalLock v${VERSION}</p>
      <p>Receipts, not truth claims. The sequence cannot be altered without detection. Divergent chains are valid and detectable. TemporalLock does not pick a winner.</p>
    </footer>
  </div>
  <script>
    (function () {
      var STORAGE = "temporallock-workspace-chain-v1";
      var chain = [];
      var lastResult = null;
      function $(id) { return document.getElementById(id); }
      function loadChain() {
        try {
          var raw = localStorage.getItem(STORAGE);
          if (!raw) return;
          var parsed = JSON.parse(raw);
          if (Array.isArray(parsed)) chain = parsed;
        } catch (e) { /* local only */ }
      }
      function saveChain() {
        try { localStorage.setItem(STORAGE, JSON.stringify(chain)); } catch (e) { /* ignore quota */ }
      }
      function fields() {
        var idx = $("click-index").value;
        var body = {
          summary: $("summary").value,
          evidence: $("evidence").value,
          confidence: Number($("confidence").value)
        };
        if (idx !== "") body.click_index = Number(idx);
        return body;
      }
      function setStatus(kind, text) {
        var el = $("ws-status");
        el.className = "status" + (kind ? " " + kind : "");
        el.textContent = text;
      }
      function addHash(parent, label, value) {
        var p = document.createElement("p");
        p.className = "hash";
        p.textContent = label + " " + (value || "");
        parent.appendChild(p);
      }
      function render() {
        $("chain-length").textContent = String(chain.length);
        var last = chain.length ? chain[chain.length - 1] : null;
        $("last-hash").textContent = last && last.hash ? last.hash : "—";
        $("last-tl").textContent = last && last.timeslate_hash ? last.timeslate_hash : "—";
        $("last-click").textContent = last && last.click_index != null ? String(last.click_index) : "—";
        var ol = $("receipt-list");
        ol.textContent = "";
        chain.forEach(function (rec, i) {
          var li = document.createElement("li");
          li.className = "receipt";
          var h = document.createElement("h3");
          h.textContent = i + " · " + (rec.timestamp || "");
          var sum = document.createElement("p");
          sum.textContent = rec.summary || "";
          var ev = document.createElement("p");
          ev.className = "meta";
          ev.style.marginTop = "0";
          ev.textContent = (rec.evidence || "") + " · confidence " + rec.confidence;
          li.appendChild(h);
          li.appendChild(sum);
          li.appendChild(ev);
          addHash(li, "hash", rec.hash);
          addHash(li, "prev", rec.prev_hash);
          if (rec.timeslate_hash) {
            addHash(li, "timeslate", rec.timeslate_hash + " · click " + rec.click_index);
            addHash(li, "staticclock_click", rec.staticclock_click);
          }
          ol.appendChild(li);
        });
        $("raw-json").textContent = JSON.stringify(lastResult || { chain: chain }, null, 2);
      }
      async function api(path, body) {
        var res = await fetch(path, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body || {})
        });
        var data = await res.json();
        if (!res.ok) throw new Error(data.error || ("HTTP " + res.status));
        return data;
      }
      function applyResult(data, fallbackMsg) {
        lastResult = data;
        if (Array.isArray(data.chain)) chain = data.chain;
        saveChain();
        var ok = data.ok;
        if (ok == null && data.errors) ok = !data.errors.length;
        var msg = data.message || fallbackMsg;
        if (data.action) msg = data.action + " · " + (msg || "Receipts, not truth claims.");
        if (data.ok === true) msg = (msg || "Intact.") + (data.length != null ? " · length " + data.length : "");
        if (data.ok === false) msg = "Errors: " + ((data.errors || []).join("; ") || "verify failed");
        if (data.error) msg = data.error;
        setStatus(ok === false || data.error ? "bad" : (ok === true || data.action ? "ok" : ""), msg || "Done.");
        render();
      }
      async function run(fn, label) {
        try {
          applyResult(await fn(), label);
        } catch (err) {
          setStatus("bad", String(err.message || err));
        }
      }
      $("btn-genesis").onclick = function () {
        run(function () { return api("/v1/genesis", fields()); }, "Genesis timeslate written. Receipts, not truth claims.");
      };
      $("btn-append").onclick = function () {
        var body = fields();
        body.chain = chain;
        run(function () { return api("/v1/append", body); }, "Timeslate appended. StaticClock click locked forward.");
      };
      $("btn-verify").onclick = function () {
        run(function () { return api("/v1/verify", { chain: chain }); }, "Verify walked hashes and prev links.");
      };
      $("btn-lattice").onclick = function () {
        run(function () { return api("/v1/lattice", { chain: chain }); }, "Lattice walk: receipt links + StaticClock binds. No rollbacks.");
      };
      $("btn-gate").onclick = function () {
        var body = fields();
        body.chain = chain;
        body.content = $("gate-text").value;
        body.file = "workspace-note";
        run(function () { return api("/v1/gate", body); }, "Gate hashed content and bound a timeslate.");
      };
      $("import-json").onchange = function () {
        var f = this.files && this.files[0];
        if (!f) return;
        f.text().then(function (text) {
          var receipts;
          try {
            var parsed = JSON.parse(text);
            receipts = Array.isArray(parsed) ? parsed : (parsed.chain || parsed.receipts || []);
          } catch (e) {
            receipts = text.split(/\\n/).filter(Boolean).map(function (line) { return JSON.parse(line); });
          }
          if (!Array.isArray(receipts) || !receipts.length) throw new Error("receipts array required");
          chain = receipts;
          lastResult = { imported: true, chain: chain };
          saveChain();
          setStatus("ok", "Imported " + chain.length + " receipts. Verify or lattice next. Receipts, not truth claims.");
          render();
        }).catch(function (err) {
          setStatus("bad", String(err.message || err));
        });
      };
      $("btn-export").onclick = function () {
        var blob = new Blob([JSON.stringify(chain, null, 2)], { type: "application/json" });
        var a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = "temporallock-chain.json";
        a.click();
        URL.revokeObjectURL(a.href);
      };
      $("btn-clear").onclick = function () {
        chain = [];
        lastResult = null;
        saveChain();
        setStatus("", "Local chain cleared. The Worker never stored it. Genesis writes the first node.");
        render();
      };
      var installBtn = $("install-btn");
      var installPre = $("install-cmd");
      var installCmd = ${JSON.stringify(INSTALL_LINE)};
      if (installBtn) {
        installBtn.addEventListener("click", function () {
          function done(ok) {
            installBtn.textContent = ok ? "Copied! Paste in Terminal, then run temporallock ui" : "Select the command, copy it, then run temporallock ui";
            installBtn.classList.add("copied");
          }
          if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(installCmd).then(function () { done(true); }).catch(function () { done(false); });
          } else {
            done(false);
            if (installPre && window.getSelection) {
              var r = document.createRange();
              r.selectNodeContents(installPre);
              var sel = window.getSelection();
              sel.removeAllRanges();
              sel.addRange(r);
            }
          }
        });
      }
      fetch("/v1/health").then(function (res) { return res.json(); }).then(function (data) {
        var pill = $("api-pill");
        if (!pill) return;
        if (data && data.ok) {
          pill.textContent = "API live · v" + (data.version || "${VERSION}");
          pill.className = "pill ok";
        } else {
          pill.textContent = "API down";
          pill.className = "pill bad";
        }
      }).catch(function () {
        var pill = $("api-pill");
        if (pill) { pill.textContent = "API down"; pill.className = "pill bad"; }
      });
      loadChain();
      render();
    })();
  </script>
</body>
</html>`;
}
