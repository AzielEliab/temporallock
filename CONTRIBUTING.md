# Contributing to TemporalLock

**Forks are first-class.** This project is Apache-2.0; you do not need
permission to fork, patch, or redistribute. Pull requests are welcome
if you want a change upstream. Keep a fork forever if you do not.

**Forks are welcome and always allowed.**

Divergent receipt chains are the same idea: two children of one
`prev_hash` are valid and detectable. Do not add code that picks a
winner.

## How to run tests

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m pytest -q
```

Python 3.10+. Core is stdlib only (`hashlib`, `json`, `argparse`).
pytest is the dev extra. No network.

## Ground rules

1. Treat `origin` as one peer among many. Downstream forks are part of
   the download-tracking model (see `workers/download-tracker`): they
   report as `{owner}/{repo}`, not as anonymous noise.
2. **Do not add narrative, authority, or scoring-of-truth.** TemporalLock
   records receipts. It does not interpret summaries, rank forks, or
   emit a "truth score". Forks that add consensus, mining, or tokens
   are outside this spec.
3. **Do not allow edits.** Receipts are append-only. There is no modify,
   no delete, no rewrite of JSONL. Corrections are new receipts. Raise
   `AppendOnlyError` on any attempt to edit, pop, or replace.
4. **Keep the dependency list tiny.** Stdlib only in the core. Optional
   dev extra is pytest. Do not add numpy or extra crypto packages.
5. **Do not change the v0.1.0 canonical encoding** without a versioned
   schema. Hashed fields are `timestamp`, `summary`, `evidence`,
   `confidence`, `prev_hash`. Confidence is 6 decimal places. Optional
   fields must not enter the core hash. v0.2.0 timeslate extras
   (`staticclock_click`, `click_index`, `prev_timeslate_hash`,
   `timeslate_hash`) are stored beside the receipt and hashed separately.
6. **No StaticClock rollbacks.** A decreasing `click_index` is refused
   (`LatticeError`). Same index is a fork on one gear-click and is
   allowed. TemporalLock does not call StaticClock; it binds a local
   digest of a StaticClock-shaped click.
7. **Honest AZ-OS role.** TemporalLock is the integrity lattice AZ-OS
   prefab hooks may write. It is not a kernel and does not execute
   software. Do not claim hosted `/v1` runs AZ-OS.
8. New behavior needs a test that fails without the change.
9. **Evidence is required.** Empty evidence is invalid. Confidence is
   `[0.0, 1.0]` inclusive, assigned by the observer — not computed as
   a claim about the world.

## Where to change things

- Canonical encoding / SHA-256: `temporallock/canon.py`, `temporallock/hashing.py`
- Receipt dataclass: `temporallock/receipt.py`
- Timeslate lattice / StaticClock click: `temporallock/timeslate.py`
- Chain load/append/verify/lattice/forks: `temporallock/chain.py`
- CLI: `temporallock/cli.py`
- Errors: `temporallock/errors.py`

## Reporting downloads from a fork

Point users at GitHub Releases. If you cut your own releases, POST
`/event` on the download-tracker worker so counts stay attributed to
your `owner/repo` (see `workers/download-tracker/README.md`).

## License of contributions

By submitting a change you agree it is licensed under Apache-2.0, the
same license as the rest of the tree. Keep the copyright lines honest.
