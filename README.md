# TemporalLock

Open-source **immutable timeslate lattice** — append-only observation
receipts hash-chained against the [StaticClock](https://github.com/AzielEliab/staticclock)
gear-click timeline (no rollbacks). This is the **AZ-OS integrity log**:
prefab OS hooks may write timeslates here. TemporalLock does not run a
kernel, does not schedule, and does not score truth.

**Author:** Aziel Eliab
**Date:** July 2026 · lattice v0.2.0
**License:** [Apache-2.0](LICENSE)

> Immutable timeslate lattice. Receipts, not truth claims.

See the spec: [docs/whitepaper.md](docs/whitepaper.md).
How to contribute: [CONTRIBUTING.md](CONTRIBUTING.md).

**Forks are welcome and always allowed.**

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"
temporallock ui
```


## One-click install

```bash
curl -fsSL https://temporallock-download-tracker.vibelock.workers.dev/install.sh | bash
```

The script curls the **counted** tarball from this project's Worker
(`/download`, User-Agent `Mozilla/5.0`), extracts, makes a venv, and
`pip install -e .`. Then run `temporallock ui`.

Or use the live software homepage (workspace + counted download):
https://temporallock-download-tracker.vibelock.workers.dev/

## Counted download (Cloudflare Worker)

**This is the counted download.** GitHub releases exist as a mirror.
The Worker serves the gzip itself (HTTP 200, no 302 to GitHub).

- Homepage: [https://temporallock-download-tracker.vibelock.workers.dev/](https://temporallock-download-tracker.vibelock.workers.dev/)
- Direct tarball: [temporallock-0.2.0.tar.gz](https://temporallock-download-tracker.vibelock.workers.dev/download?asset=temporallock-0.2.0.tar.gz)
- One-click install: [https://temporallock-download-tracker.vibelock.workers.dev/install.sh](https://temporallock-download-tracker.vibelock.workers.dev/install.sh)
- Skill: [https://temporallock-download-tracker.vibelock.workers.dev/v1/skill](https://temporallock-download-tracker.vibelock.workers.dev/v1/skill)
- OpenAPI: [https://temporallock-download-tracker.vibelock.workers.dev/openapi.json](https://temporallock-download-tracker.vibelock.workers.dev/openapi.json)
- GitHub: [https://github.com/AzielEliab/temporallock](https://github.com/AzielEliab/temporallock)
- Cite: [cite.json](https://temporallock-download-tracker.vibelock.workers.dev/cite.json) — Eliab, Aziel. (2026). TemporalLock 0.2.0 [Software]. Apache-2.0. Historical DOI 10.5281/zenodo.21431405 is tombstoned; no DOI is invented here.

Isolated counter: Worker `temporallock-download-tracker`, KV `TEMPORALLOCK_DOWNLOADS`. `/v1` does not increment downloads.

Open http://127.0.0.1:8766 (loopback only). No CDN, no telemetry.

Counted download: [https://temporallock-download-tracker.vibelock.workers.dev/](https://temporallock-download-tracker.vibelock.workers.dev/)

File gate: `temporallock gate FILE` hashes the file, appends a timeslate bound to a StaticClock click, and verifies the lattice before treating it as accepted.

**StaticClock** (gear-click timeline, no rollbacks): [https://staticclock-download-tracker.vibelock.workers.dev/](https://staticclock-download-tracker.vibelock.workers.dev/)

**AZ-OS** (prefab OS hooks; integrity precedes execution): [https://azos-download-tracker.vibelock.workers.dev/](https://azos-download-tracker.vibelock.workers.dev/)

Honest AZ-OS role: TemporalLock is the integrity lattice those hooks write into. Hosted `/v1` does not execute software, does not halt a kernel, and does not store chains.



---

## Download

**Counted download page (this project only, ticks automatically):**

# → [https://temporallock-download-tracker.vibelock.workers.dev/](https://temporallock-download-tracker.vibelock.workers.dev/) ←

The big button on that page is the download. The number next to it is
**temporallock only** — its own Worker and KV, not mixed with VibeLock or
anything else. Clicking it increments the counter. Nobody reports
anything. Forks that use the same link are counted too.

Direct tarball (also counted): [temporallock-0.2.0.tar.gz](https://temporallock-download-tracker.vibelock.workers.dev/download?asset=temporallock-0.2.0.tar.gz)

- Live count JSON: [https://temporallock-download-tracker.vibelock.workers.dev/count](https://temporallock-download-tracker.vibelock.workers.dev/count)
- Stats: [https://temporallock-download-tracker.vibelock.workers.dev/stats](https://temporallock-download-tracker.vibelock.workers.dev/stats)
- GitHub releases: [https://github.com/AzielEliab/temporallock/releases](https://github.com/AzielEliab/temporallock/releases)

---


## Local UI

`temporallock ui` serves a loopback dashboard at http://127.0.0.1:8766

Binds to `127.0.0.1` only. Self-contained HTML (no CDN). Genesis / append / verify / lattice a local timeslate chain in a process tmp dir. Receipts, not truth claims.


## iPhone & Android

Flutter sources: [`mobile/`](mobile/). Application id `com.azieeliab.temporallock`. Offline. No analytics. Dark matte / gold.

Genesis / append / verify a timeslate lattice on device. Receipts, not truth claims.

```bash
cd mobile
flutter create --org com.azieeliab --project-name temporallock .
flutter pub get
flutter run
```

The `android/` and `ios/` folders in this tree are skeleton READMEs until you run `flutter create .` (this machine has no Flutter SDK on PATH). Then open `android/` in Android Studio or `ios/Runner.xcworkspace` in Xcode. Not a store listing.

## What it does

TemporalLock records **timeslates**. A timeslate is a receipt bound to
one StaticClock gear-click. The receipt is still an observer's note —
not a verdict, not a score of truth, and not an official history.

Each receipt is cryptographically linked to the previous one
(`prev_hash` = SHA-256 of the prior receipt). v0.2.0 also binds a
**timeslate hash** to `receipt.hash`, `staticclock_click`,
`prev_timeslate_hash`, and a monotonic `click_index`. A decreasing
`click_index` is a StaticClock rollback and is refused.

The sequence cannot be altered without detection. Breaks are immediately
visible. Divergent chains (forks) are valid and detectable. TemporalLock
does not pick a winner.

There is no modify and no delete. `chain.append(...)` only. A
correction or dispute is a **new timeslate** that may mention a prior
hash (optional `re: <hash>` in the summary). The old receipt stays.

v0.2.0 runtime is stdlib only (`hashlib`, `json`). No numpy, no extra
crypto packages. The v0.1.0 core receipt hash is unchanged so older
JSONL files still verify.

## Core receipt (v0.1.0, still the hash contract)

| Field | Meaning |
|-------|---------|
| `timestamp` | UTC ISO-8601 of the observation (observer-supplied or now) |
| `summary` | Brief string of what was observed |
| `evidence` | Supporting body and/or reference URI/path (**required**; empty is invalid) |
| `confidence` | Observer-assigned float in `[0.0, 1.0]` inclusive |
| `prev_hash` | SHA-256 of the previous receipt (genesis uses 64 zero hex chars) |
| `hash` | SHA-256 of this receipt's canonical encoding (excluding `hash` itself) |

Optional extra fields may exist in a JSONL line. They **must not** enter
the core hash unless a later versioned schema says so. v0.1.0 hashes
core fields only so chains stay verifiable long-term.

## Timeslate extras (v0.2.0, not in the core hash)

| Field | Meaning |
|-------|---------|
| `staticclock_click` | SHA-256 of a StaticClock-shaped gear-click (local digest; TemporalLock does not call StaticClock) |
| `click_index` | Monotonic integer. Must not decrease. Same index = same click (forks allowed). |
| `prev_timeslate_hash` | Previous timeslate hash, or the prior receipt hash as a v0.1.0 bridge |
| `timeslate_hash` | SHA-256 of `click_index`, `prev_timeslate_hash`, `receipt_hash`, `staticclock_click` |

`temporallock lattice FILE` walks both the receipt chain and the
StaticClock binds. `temporallock click` prints a local click digest.

## Canonical encoding

UTF-8 JSON, **sorted keys**, **no extra whitespace**
(`separators=(",", ":")`). Hashed fields:

```
timestamp, summary, evidence, confidence, prev_hash
```

`confidence` is serialized as a JSON number with **exactly 6 decimal
places** (example: `0.7` → `0.700000`) so hashes are stable. See
`temporallock/canon.py`.

## Cryptographic linking

SHA-256. For a linear chain, `receipt[n].prev_hash == receipt[n-1].hash`.
Two receipts with the same `prev_hash` and different hashes are a
**fork**. Forks are allowed. Verification of each fork stored separately
still succeeds if that fork's own hashes and links are intact.

## Install

Python 3.10+. Stdlib only in the core.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

From a release artifact:

```bash
python -m pip install temporallock-0.2.0.tar.gz
```

## CLI

```bash
temporallock version
temporallock ui        # localhost UI on 127.0.0.1:8766

# First receipt (explicit genesis; append will not create a missing file)
temporallock genesis --chain notes.jsonl --summary "sky was overcast" \
  --evidence "photo:./sky.jpg" --confidence 0.9

# Later receipts (file must already exist)
temporallock append --chain notes.jsonl --summary "re: <hash> rain began" \
  --evidence "https://example.invalid/log" --confidence 0.7

temporallock verify notes.jsonl
temporallock lattice notes.jsonl
temporallock show notes.jsonl
temporallock timeslate --chain notes.jsonl --summary "hook fired" --evidence "azos:prefab"
temporallock click --timestamp 2026-07-12T14:30:00Z
```

`verify` exits 0 if the chain is intact, nonzero if broken. No special
access required. Anyone can recompute hashes from the fields.

Library:

```python
from temporallock import Chain, Receipt

chain = Chain.genesis(
    "notes.jsonl",
    summary="sky was overcast",
    evidence="photo:./sky.jpg",
    confidence=0.9,
)
chain.append("rain began", evidence="https://example.invalid/log", confidence=0.7)
result = chain.verify()
assert result.ok
lattice = chain.lattice()
assert lattice.ok and lattice.cross_hash
```

## Example

```bash
python examples/record_observation.py
```

Writes `examples/_out/observations.jsonl`, appends a correction as a
new receipt, and verifies.

## Tests

```bash
pip install -e ".[dev]"
python -m pytest -q
```

Offline. Fixtures are synthetic receipts. They cover genesis linking,
tamper detection, append-only, corrections, forks, confidence/evidence
validation, canonical stability, CLI, independent verification,
JSONL first-line immutability, timeslate StaticClock cross-hash, and
rollback refusal.

## Layout

```
temporallock/          library (receipt, hashing/canon, chain, timeslate, cli)
tests/                 pytest
docs/whitepaper.md     July 2026 spec
examples/              record an observation
workers/download-tracker/   Cloudflare Worker + wrangler.toml
CONTRIBUTING.md        forks are first-class
mobile/              Flutter iPhone + Android (`flutter create .`)
```

## What this is not

TemporalLock does not add consensus, mining, tokens, or "truth scores".
It does not interpret summaries. It does not declare a canonical fork.
It is not a kernel, not AZ-OS itself, not a scheduler, and not a remote
shell. Hosted `/v1` does not run AZ-OS. It is a receipt / timeslate log,
not an oracle.

## Use with AI assistants

Works with ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude (Anthropic), Cursor (MCP), Glama (MCP), Perplexity, Microsoft Copilot / Bing, Google Gemini / Vertex, Mistral, Meta AI, Apple Intelligence surfaces, Amazon Q tooling, DuckAssist, You.com, Cohere, and other MCP/OpenAPI-capable assistants. Author Aziel Eliab only.

Live HTTPS runtime on the existing download-tracker Worker. Stateless: send the chain JSON in the body. Receipts, not truth claims.

OpenAPI (GPT Actions, custom HTTP tools, Grok custom tools, and other OpenAPI imports):

```
https://temporallock-download-tracker.vibelock.workers.dev/openapi.json
```

Setup notes: [https://temporallock-download-tracker.vibelock.workers.dev/ai](https://temporallock-download-tracker.vibelock.workers.dev/ai)

MCP catalog (Cursor, Glama, Claude, and other MCP clients; ships separately): `https://aziel-runtime.vibelock.workers.dev/mcp`

```bash
curl -sS -X POST https://temporallock-download-tracker.vibelock.workers.dev/v1/genesis \
  -H "content-type: application/json" \
  -d '{"summary":"observed package release","evidence":"sha256:abc path:README.md","confidence":1.0}'
```

## License

Apache-2.0. See [LICENSE](LICENSE).

Forks are welcome and always allowed.
