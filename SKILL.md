---
name: TemporalLock
description: Use when minting or verifying an immutable timeslate lattice hash-chained against StaticClock. AZ-OS integrity log. Receipts, not truth claims. Hosted API is stateless. Dual surface: Worker /v1 + catalog MCP. This Worker /v1/mesh/* PROXY to aziel-runtime via AZIEL_RUNTIME. Suite mesh default OFF. QNM-BUILD-1.0 live|locked|isolated. No Node Gate. No auto-heal. Not anonymity. Author Aziel Eliab.
---

# TemporalLock

Immutable timeslate lattice. Hash-chained against StaticClock. Receipts, not truth claims.

Author: **Aziel Eliab**.

Use when minting or verifying append-only timeslates bound to a StaticClock gear-click. No rollbacks. AZ-OS prefab hooks may write this integrity log. Hosted API is stateless and does not run AZ-OS.

Always send `User-Agent: Mozilla/5.0`. Cloudflare Workers may 403 an empty agent.

## Endpoints (this Worker)

Host: `https://temporallock-download-tracker.vibelock.workers.dev`

| Method | Path | What |
|--------|------|------|
| GET | `/v1/health` | Liveness. Does not increment downloads. |
| GET | `/v1/skill` | This markdown. Does not increment downloads. |
| GET | `/v1/mesh` | PROXY suite mesh status. Default OFF. QNM live|locked|isolated. Never enables. |
| GET | `/v1/mesh/nodes` | PROXY Live Nodes roster (5-minute presence). |
| POST | `/v1/mesh/{enable,disable,join,heartbeat,leave,broadcast}` | PROXY. Bearer required to enable. No auto-heal. Anon-broadcast is not a publish path. |
| GET | `/v1/example` | Sample timeslate payload. Does not increment downloads. |
| POST | `/v1/genesis` | First timeslate. Body includes summary + evidence. Optional click. |
| POST | `/v1/append` | Append a timeslate. Client sends the chain. Decreasing click_index is refused. |
| POST | `/v1/timeslate` | Genesis or append a StaticClock-bound timeslate. |
| POST | `/v1/verify` | Verify receipt hashes and prev links. Not stored. |
| POST | `/v1/lattice` | Verify receipt links + timeslate binds + no StaticClock rollback. |
| POST | `/v1/click` | Local SHA-256 of a StaticClock-shaped gear-click. No network. |
| POST | `/v1/gate` | File-gate preview (hash + timeslate). |

OpenAPI: `https://temporallock-download-tracker.vibelock.workers.dev/openapi.json`

Catalog OpenAPI: `https://aziel-runtime.vibelock.workers.dev/openapi.json`

MCP: `POST https://aziel-runtime.vibelock.workers.dev/mcp`

Catalog aliases under `/p/temporallock/…`. Catalog MCP `mesh_*` + FragGate `slug=mesh`. Suite mesh default OFF.

StaticClock (gear-click timeline): `https://staticclock-download-tracker.vibelock.workers.dev/`

AZ-OS (prefab OS hooks; integrity precedes execution): `https://azos-download-tracker.vibelock.workers.dev/`

## How to call (Mozilla/5.0)

```bash
curl -s -A 'Mozilla/5.0' https://temporallock-download-tracker.vibelock.workers.dev/v1/health
curl -s -A 'Mozilla/5.0' -X POST https://temporallock-download-tracker.vibelock.workers.dev/v1/genesis \
  -H 'content-type: application/json' \
  -d '{"summary":"desk closed","evidence":"log row"}'
curl -s -A 'Mozilla/5.0' -X POST https://temporallock-download-tracker.vibelock.workers.dev/v1/lattice \
  -H 'content-type: application/json' \
  -d '{"chain":[]}'
curl -s -A 'Mozilla/5.0' https://temporallock-download-tracker.vibelock.workers.dev/v1/skill
curl -s -A 'Mozilla/5.0' https://temporallock-download-tracker.vibelock.workers.dev/v1/mesh
```

Works with ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude (Anthropic), Cursor (MCP), Glama (MCP), Perplexity, Microsoft Copilot / Bing, Google Gemini / Vertex, Mistral, Meta AI, Apple Intelligence surfaces, Amazon Q tooling, DuckAssist, You.com, Cohere, and other MCP/OpenAPI-capable assistants. Import the catalog or Worker OpenAPI as a GPT Action, custom HTTP tool, or custom OpenAPI tool. MCP clients (Cursor, Glama, Claude, and others): `POST` the catalog MCP endpoint.

## Local (after one-click install)

```bash
curl -fsSL https://temporallock-download-tracker.vibelock.workers.dev/install.sh | bash
temporallock ui
temporallock doctor
```

Then open http://127.0.0.1:8766 (this computer only).

## Honest banner

THIS IS: an immutable timeslate lattice hash-chained against the StaticClock gear-click timeline, used as the AZ-OS integrity log. THIS IS NOT: a kernel, scheduler, truth score, court, or remote shell. The Worker does not store chains and does not run AZ-OS. Author Aziel Eliab.

Cite the GitHub repository and this Worker. Historical DOI 10.5281/zenodo.21431405 is a tombstoned Zenodo record and is not currently resolvable. No DOI is invented here.

Apache-2.0 (or the repo LICENSE). Forks are welcome and always allowed.

## Catalog + local UI

Author: **Aziel Eliab**. Honest scope: Timeslate lattice × StaticClock. AZ-OS integrity, not a kernel.

- Product homepage (workspace + counted download): https://temporallock-download-tracker.vibelock.workers.dev/
- Catalog product: https://aziel-runtime.vibelock.workers.dev/p/temporallock/
- Catalog OpenAPI: https://aziel-runtime.vibelock.workers.dev/openapi.json
- Catalog MCP: `POST https://aziel-runtime.vibelock.workers.dev/mcp`
- This Worker skill: `GET https://temporallock-download-tracker.vibelock.workers.dev/v1/skill`
- This Worker OpenAPI: https://temporallock-download-tracker.vibelock.workers.dev/openapi.json
- Sample payload: `GET https://temporallock-download-tracker.vibelock.workers.dev/v1/example`
- Suite mesh: `GET https://temporallock-download-tracker.vibelock.workers.dev/v1/mesh` (PROXY; default OFF)

Local UI: **Import JSON file** (`type=file`) and **Export JSON**. Then `temporallock doctor`. Worker homepage Live Nodes strip polls `GET /v1/mesh` (default OFF).

Works with ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude (Anthropic), Cursor (MCP), Glama (MCP), Perplexity, Microsoft Copilot / Bing, Google Gemini / Vertex, Mistral, Meta AI, Apple Intelligence surfaces, Amazon Q tooling, DuckAssist, You.com, Cohere, and other MCP/OpenAPI-capable assistants. Import catalog or Worker OpenAPI as a GPT Action, custom HTTP tool, or custom OpenAPI tool. MCP clients: `POST https://aziel-runtime.vibelock.workers.dev/mcp`.

Counted download (gzip HTTP 200, no 302): https://temporallock-download-tracker.vibelock.workers.dev/download?asset=temporallock-0.2.0.tar.gz
GitHub: https://github.com/AzielEliab/temporallock
