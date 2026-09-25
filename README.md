# TemporalLock

Record observation receipts on a local chain. Each receipt stays.

**Author:** Aziel Eliab
**License:** [Apache-2.0](LICENSE)

## Start

1. Install:
   ```bash
   python -m venv .venv && source .venv/bin/activate && pip install -e .
   ```
2. Open the app:
   ```bash
   temporallock ui
   ```
3. In the browser, open http://127.0.0.1:8766 and write a receipt.

`temporallock` alone prints these next steps. `temporallock doctor` checks the install. `temporallock --help` lists commands.

A timeslate is a receipt tied to a [StaticClock](https://github.com/AzielEliab/staticclock) gear-click. AZ-OS prefab hooks may write here. Spec: [docs/whitepaper.md](docs/whitepaper.md). Contributing: [CONTRIBUTING.md](CONTRIBUTING.md). July 2026 · version 0.2.0. Forks are welcome and always allowed.


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
- Suite mesh proxy: [https://temporallock-download-tracker.vibelock.workers.dev/v1/mesh](https://temporallock-download-tracker.vibelock.workers.dev/v1/mesh) — default OFF; QNM live / locked / isolated; QNS-CD-1.0 photon QNS1 packet transfer is a hub cite / Worker mesh cross-map only (not a Softwares-tab product; no public qnsd proxy)
- OpenAPI: [https://temporallock-download-tracker.vibelock.workers.dev/openapi.json](https://temporallock-download-tracker.vibelock.workers.dev/openapi.json)
- GitHub: [https://github.com/AzielEliab/temporallock](https://github.com/AzielEliab/temporallock)
- Cite: [cite.json](https://temporallock-download-tracker.vibelock.workers.dev/cite.json) — Eliab, Aziel. (2026). TemporalLock 0.2.0 [Software]. Apache-2.0. Historical DOI 10.5281/zenodo.21431405 is tombstoned; no DOI is invented here.

Isolated counter: Worker `temporallock-download-tracker`, KV `TEMPORALLOCK_DOWNLOADS`. `/v1` does not increment downloads.

Open http://127.0.0.1:8766 (loopback only). No CDN, no telemetry.

Counted download: [https://temporallock-download-tracker.vibelock.workers.dev/](https://temporallock-download-tracker.vibelock.workers.dev/)

File gate: `temporallock gate FILE` hashes the file, appends a timeslate bound to a StaticClock click, and verifies the lattice before treating it as accepted.

**StaticClock** (gear-click timeline, no rollbacks): [https://staticclock-download-tracker.vibelock.workers.dev/](https://staticclock-download-tracker.vibelock.workers.dev/)

**AZ-OS** (prefab OS hooks; integrity precedes execution): [https://azos-download-tracker.vibelock.workers.dev/](https://azos-download-tracker.vibelock.workers.dev/)

AZ-OS role: TemporalLock is the integrity lattice those hooks write into. Hosted `/v1` answers the request you send and leaves the chain with the caller.



---

## Download

**Counted download page (this project only, ticks automatically):**

# → [https://temporallock-download-tracker.vibelock.workers.dev/](https://temporallock-download-tracker.vibelock.workers.dev/) ←

The big button on that page is the download. The number next to it is
**temporallock only** — its own Worker and KV, not mixed with VibeLock or
anything else. Clicking it increments the counter. Nobody reports
anything. Forks that use the same link are counted too.

Direct tarball (also counted): [temporallock-0.2.0.tar.gz](https://temporallock-download-tracker.vibelock.workers.dev/download?asset=temporallock-0.2.0.tar.gz)

- Live count JSON `{project, views, downloads, total}`: [https://temporallock-download-tracker.vibelock.workers.dev/count](https://temporallock-download-tracker.vibelock.workers.dev/count)
- Stats: [https://temporallock-download-tracker.vibelock.workers.dev/stats](https://temporallock-download-tracker.vibelock.workers.dev/stats)
- GitHub releases: [https://github.com/AzielEliab/temporallock/releases](https://github.com/AzielEliab/temporallock/releases)

---


## Local UI

`temporallock ui` prints `Open http://127.0.0.1:8766/` and serves the page on this computer only.

Write one receipt on the page. Confidence, click index, link checks, timeslate binds, import, and export are under **Advanced**. The page follows the system light or dark setting. The chain for that session is removed when you stop the app.


## iPhone & Android

Flutter sources: [`mobile/`](mobile/). Application id `com.azieeliab.temporallock`. Offline. No analytics. Follows the system light or dark setting, with a gold accent.

Write one receipt on device. Confidence and the link check are under Advanced.

```bash
cd mobile
flutter create --org com.azieeliab --project-name temporallock .
flutter pub get
flutter run
```

The `android/` and `ios/` folders in this tree are skeleton READMEs until you run `flutter create .` (this machine has no Flutter SDK on PATH). Then open `android/` in Android Studio or `ios/Runner.xcworkspace` in Xcode. Not a store listing.

## What it does

TemporalLock records **timeslates**. A timeslate is a receipt bound to
one StaticClock gear-click. The receipt is the observer's note.

Each receipt is cryptographically linked to the previous one
(`prev_hash` = SHA-256 of the prior receipt). v0.2.0 also binds a
**timeslate hash** to `receipt.hash`, `staticclock_click`,
`prev_timeslate_hash`, and a monotonic `click_index`. A decreasing
`click_index` is a StaticClock rollback and is refused.

The sequence cannot be altered without detection. Breaks are immediately
visible. Divergent chains (forks) are valid and detectable. Forks stay side by side.

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
| `staticclock_click` | SHA-256 of a StaticClock-shaped gear-click (local digest, computed on this computer) |
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
temporallock            # welcome and next steps
temporallock --help
temporallock version
temporallock ui          # prints Open http://127.0.0.1:8766/
temporallock doctor
temporallock verify notes.jsonl
temporallock verify notes.jsonl --json

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

`verify` exits 0 if the chain is intact, nonzero if broken. Add `--json` when a program should read verify, lattice, click, gate, or doctor. `temporallock click --json FILE` also mixes that JSON object into the click. Anyone can recompute hashes from the fields.

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

## Notes

TemporalLock keeps an append-only timeslate lattice. Forks stay side by side. A later receipt can mention an earlier hash. Hosted `/v1` answers the request you send and does not store the chain. Author: Aziel Eliab.

## Use with AI assistants

Works with ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude (Anthropic), Cursor (MCP), Glama (MCP), Perplexity, Microsoft Copilot / Bing, Google Gemini / Vertex, Mistral, Meta AI, Apple Intelligence surfaces, Amazon Q tooling, DuckAssist, You.com, Cohere, and other MCP/OpenAPI-capable assistants. Author Aziel Eliab only.

Live HTTPS runtime on the existing download-tracker Worker. Stateless: send the chain JSON in the body. Receipts, not truth claims.

OpenAPI (GPT Actions, custom HTTP tools, Grok custom tools, and other OpenAPI imports):

```
https://temporallock-download-tracker.vibelock.workers.dev/openapi.json
```

Setup notes: [https://temporallock-download-tracker.vibelock.workers.dev/ai](https://temporallock-download-tracker.vibelock.workers.dev/ai)

MCP catalog (Cursor, Glama, Claude, and other MCP clients; ships separately): `https://aziel-runtime.vibelock.workers.dev/mcp`. Suite mesh `/v1/mesh/*` PROXY via `AZIEL_RUNTIME` (default OFF; QNM-BUILD-1.0 live|locked|isolated; QNS-CD-1.0 photon QNS1 packet transfer cross-map; no Node Gate; no public qnsd proxy). Local qnsd is coded in [qnm-node](https://github.com/AzielEliab/qnm-node). Runtime cites + catalog field live in [aziel-runtime](https://github.com/AzielEliab/aziel-runtime). Pair custody: [AZInterface](https://github.com/AzielEliab/azinterface). Not a Softwares-tab product. Catalog MCP `mesh_*` + FragGate `slug=mesh`.

```bash
curl -sS -X POST https://temporallock-download-tracker.vibelock.workers.dev/v1/genesis \
  -H "content-type: application/json" \
  -d '{"summary":"observed package release","evidence":"sha256:abc path:README.md","confidence":1.0}'
```

## License

Apache-2.0. See [LICENSE](LICENSE).

Forks are welcome and always allowed.
