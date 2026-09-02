---
name: TemporalLock
description: Use when calling TemporalLock hosted /v1 or installing the local package. Author Aziel Eliab.
---

# TemporalLock

Receipts, not truth claims. Author: **Aziel Eliab**.

**THIS IS:** append-only observation receipts with cryptographic linking.

**THIS IS NOT:** a truth score, court filing, or consensus token. Hosted `/v1` does not increment downloads or views.

Always send `User-Agent: Mozilla/5.0`. Cloudflare Workers may 403 an empty agent.

## Call these URLs

- Worker OpenAPI: https://temporallock-download-tracker.vibelock.workers.dev/openapi.json
- Catalog OpenAPI: https://aziel-runtime.vibelock.workers.dev/openapi.json
- MCP: `POST https://aziel-runtime.vibelock.workers.dev/mcp`
- Live skill (this markdown): `GET https://temporallock-download-tracker.vibelock.workers.dev/v1/skill`

Ops (do **not** increment downloads or views):

- `GET /v1/health` — liveness
- `GET /v1/skill` — this file
- Product POSTs listed in OpenAPI

Grok: import OpenAPI as a custom tool. ChatGPT: GPT Actions. Venice: HTTP tools.

## Example

```bash
curl -s -A 'Mozilla/5.0' https://temporallock-download-tracker.vibelock.workers.dev/v1/health
curl -s -A 'Mozilla/5.0' https://temporallock-download-tracker.vibelock.workers.dev/v1/skill
```

## Local (after one-click install)

```bash
curl -fsSL https://temporallock-download-tracker.vibelock.workers.dev/install.sh | bash
temporallock ui
temporallock doctor
```

Then open http://127.0.0.1:8766 (loopback only).

Counted download (gzip HTTP 200, no 302): https://temporallock-download-tracker.vibelock.workers.dev/download?asset=temporallock-0.1.0.tar.gz
GitHub: https://github.com/AzielEliab/temporallock

Paper: DOI https://doi.org/10.5281/zenodo.21431405 · https://zenodo.org/records/21431405 · Apache-2.0. Forks welcome.

## Catalog + local UI

Author: **Aziel Eliab**. Honest scope: Append-only observation receipts. Receipts, not truth claims.

- Catalog product: https://aziel-runtime.vibelock.workers.dev/p/temporallock/
- Catalog OpenAPI: https://aziel-runtime.vibelock.workers.dev/openapi.json
- Catalog MCP: `POST https://aziel-runtime.vibelock.workers.dev/mcp`
- This Worker skill: `GET https://temporallock-download-tracker.vibelock.workers.dev/v1/skill`
- This Worker OpenAPI: https://temporallock-download-tracker.vibelock.workers.dev/openapi.json
- Sample payload: `GET https://temporallock-download-tracker.vibelock.workers.dev/v1/example`

Local UI: **Import JSON file** (`type=file`) and **Export JSON**. Then `temporallock doctor`.

Grok: import catalog or Worker OpenAPI as a custom tool. ChatGPT: GPT Actions. Venice: HTTP tools.
