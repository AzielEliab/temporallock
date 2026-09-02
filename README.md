# TemporalLock

Open-source, append-only system for recording observations at specific
moments — with evidence and confidence — without imposing narrative,
authority, or interpretive claims.

**Author:** Aziel Eliab
**Date:** July 2026
**License:** [Apache-2.0](LICENSE)

> Receipts, not truth claims.

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

Or tap **Download** / **One-click install** on the Worker homepage:
https://temporallock-download-tracker.vibelock.workers.dev/

## Counted download (Cloudflare Worker)

**This is the counted download.** GitHub releases exist as a mirror.
The Worker serves the gzip itself (HTTP 200, no 302 to GitHub).

- Homepage: [https://temporallock-download-tracker.vibelock.workers.dev/](https://temporallock-download-tracker.vibelock.workers.dev/)
- Direct tarball: [temporallock-0.1.0.tar.gz](https://temporallock-download-tracker.vibelock.workers.dev/download?asset=temporallock-0.1.0.tar.gz)
- One-click install: [https://temporallock-download-tracker.vibelock.workers.dev/install.sh](https://temporallock-download-tracker.vibelock.workers.dev/install.sh)
- Skill: [https://temporallock-download-tracker.vibelock.workers.dev/v1/skill](https://temporallock-download-tracker.vibelock.workers.dev/v1/skill)
- OpenAPI: [https://temporallock-download-tracker.vibelock.workers.dev/openapi.json](https://temporallock-download-tracker.vibelock.workers.dev/openapi.json)
- GitHub: [https://github.com/AzielEliab/temporallock](https://github.com/AzielEliab/temporallock)
- Zenodo DOI: [10.5281/zenodo.21431405](https://doi.org/10.5281/zenodo.21431405) · [record](https://zenodo.org/records/21431405)

Isolated counter: Worker `temporallock-download-tracker`, KV `TEMPORALLOCK_DOWNLOADS`. `/v1` does not increment downloads.

Open http://127.0.0.1:8766 (loopback only). No CDN, no telemetry.

Counted download: [https://temporallock-download-tracker.vibelock.workers.dev/](https://temporallock-download-tracker.vibelock.workers.dev/)

File gate: `temporallock gate FILE` hashes the file, appends a receipt, and verifies before treating it as accepted.



---

## Download

**Counted download page (this project only, ticks automatically):**

# → [https://temporallock-download-tracker.vibelock.workers.dev/](https://temporallock-download-tracker.vibelock.workers.dev/) ←

The big button on that page is the download. The number next to it is
**temporallock only** — its own Worker and KV, not mixed with VibeLock or
anything else. Clicking it increments the counter. Nobody reports
anything. Forks that use the same link are counted too.

Direct tarball (also counted): [temporallock-0.1.0.tar.gz](https://temporallock-download-tracker.vibelock.workers.dev/download?asset=temporallock-0.1.0.tar.gz)

- Live count JSON: [https://temporallock-download-tracker.vibelock.workers.dev/count](https://temporallock-download-tracker.vibelock.workers.dev/count)
- Stats: [https://temporallock-download-tracker.vibelock.workers.dev/stats](https://temporallock-download-tracker.vibelock.workers.dev/stats)
- GitHub releases: [https://github.com/AzielEliab/temporallock/releases](https://github.com/AzielEliab/temporallock/releases)

---


## Local UI

`temporallock ui` serves a loopback dashboard at http://127.0.0.1:8766

Binds to `127.0.0.1` only. Self-contained HTML (no CDN). Genesis / append / verify a local chain in a process tmp dir. Receipts, not truth claims.


## iPhone & Android

Flutter sources: [`mobile/`](mobile/). Application id `com.azieeliab.temporallock`. Offline. No analytics. Dark matte / gold.

Genesis / append / verify on device. Receipts, not truth claims.

```bash
cd mobile
flutter create --org com.azieeliab --project-name temporallock .
flutter pub get
flutter run
```

The `android/` and `ios/` folders in this tree are skeleton READMEs until you run `flutter create .` (this machine has no Flutter SDK on PATH). Then open `android/` in Android Studio or `ios/Runner.xcworkspace` in Xcode. Not a store listing.

## What it does

TemporalLock records **receipts**. A receipt is an observer's note that
something was observed at a time, with supporting evidence and a
confidence the observer assigned. It is not a verdict, not a score of
truth, and not an official history.

Each receipt is cryptographically linked to the previous one
(`prev_hash` = SHA-256 of the prior receipt). The sequence cannot be
altered without detection. Breaks are immediately visible. Divergent
chains (forks) are valid and detectable. TemporalLock does not pick a
winner.

There is no modify and no delete. `chain.append(...)` only. A
correction or dispute is a **new receipt** that may mention a prior
hash (optional `re: <hash>` in the summary). The old receipt stays.

v0.1.0 runtime is stdlib only (`hashlib`, `json`). No numpy, no extra
crypto packages.

## Core receipt (v0.1.0)

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
python -m pip install temporallock-0.1.0.tar.gz
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
temporallock show notes.jsonl
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
validation, canonical stability, CLI, independent verification, and
JSONL first-line immutability.

## Layout

```
temporallock/          library (receipt, hashing/canon, chain, cli)
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
It is a receipt log, not an oracle.

## Use with Grok, ChatGPT, Venice

Live HTTPS runtime on the existing download-tracker Worker. Stateless: send the chain JSON in the body. Receipts, not truth claims.

OpenAPI (ChatGPT GPT Actions / Venice custom HTTP / Grok custom tool):

```
https://temporallock-download-tracker.vibelock.workers.dev/openapi.json
```

Setup notes: [https://temporallock-download-tracker.vibelock.workers.dev/ai](https://temporallock-download-tracker.vibelock.workers.dev/ai)

MCP catalog (ships separately): `https://aziel-runtime.vibelock.workers.dev/mcp`

```bash
curl -sS -X POST https://temporallock-download-tracker.vibelock.workers.dev/v1/genesis \
  -H "content-type: application/json" \
  -d '{"summary":"observed package release","evidence":"sha256:abc path:README.md","confidence":1.0}'
```

## License

Apache-2.0. See [LICENSE](LICENSE).

Forks are welcome and always allowed.
