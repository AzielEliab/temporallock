---
name: TemporalLock
description: Use when minting or verifying an immutable timeslate lattice hash-chained against StaticClock. AZ-OS integrity log. Receipts, not truth claims. Hosted API is stateless. Hosted /v1 via this Worker or aziel-runtime. Author Aziel Eliab.
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

Catalog aliases under `/p/temporallock/…`.

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
```

Grok: import the catalog OpenAPI as a custom tool. ChatGPT: GPT Actions. Venice: HTTP tools.

## Local (after one-click install)

```bash
curl -fsSL https://temporallock-download-tracker.vibelock.workers.dev/install.sh | bash
temporallock ui
temporallock doctor
```

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
- Catalog MCP: `POST https://aziel-runtime.vibelock.workers.dev/mcp`
- This Worker skill: `GET https://temporallock-download-tracker.vibelock.workers.dev/v1/skill`
- This Worker OpenAPI: https://temporallock-download-tracker.vibelock.workers.dev/openapi.json
- Sample payload: `GET https://temporallock-download-tracker.vibelock.workers.dev/v1/example`

Local UI: **Import JSON file** (`type=file`) and **Export JSON**. Then `temporallock doctor`.

Grok: import catalog or Worker OpenAPI as a custom tool. ChatGPT: GPT Actions. Venice: HTTP tools.

Counted download (gzip HTTP 200, no 302): https://temporallock-download-tracker.vibelock.workers.dev/download?asset=temporallock-0.2.0.tar.gz
GitHub: https://github.com/AzielEliab/temporallock
