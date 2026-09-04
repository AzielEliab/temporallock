# TemporalLock

**An append-only observation receipt log**

Aziel Eliab
July 2026
License: Apache-2.0

> Receipts, not truth claims.

## Abstract

TemporalLock is an open-source, append-only system for recording
observations at specific moments — with evidence and confidence —
without imposing narrative, authority, or interpretive claims. A receipt
is a record that an observer noted something, not a declaration that the
something is true, official, or complete.

Receipts are cryptographically linked with SHA-256. The sequence cannot
be altered without detection. Breaks are immediately visible. Divergent
chains (forks) are valid and detectable. The system does not pick a
winner, does not mine, does not issue tokens, and does not score truth.

This document is the specification implemented by the `temporallock`
Python package. v0.1.0 is the core receipt hash contract. v0.2.0 adds
the timeslate lattice (StaticClock cross-hash) without changing that
contract. Forks are welcome and always allowed.

---

## 1. Purpose

People write down what they saw. They attach a time, a scrap of
evidence, and a sense of how sure they were. That act is useful. It
becomes harmful when the log is later treated as an oracle: when a
timestamp is confused with authority, a confidence number with a
probability of the world, or a longest chain with "what happened."

TemporalLock separates the **receipt** from the **claim**.

- A receipt says: an observer recorded this summary, at this time, with
  this evidence, at this confidence.
- A receipt does not say: this is true, this is the official story, this
  fork is canonical, this score measures reality.

The design goals are therefore modest and strict:

1. **Record, don't narrate.** The library stores fields. It does not
   interpret summaries.
2. **Link, don't govern.** Cryptographic hashes make tampering visible.
   They do not elect a historian.
3. **Append, don't edit.** The past is not rewritten. A correction is a
   new receipt.
4. **Forks are first-class.** Two honest observers, or one observer who
   changed their mind, may diverge. Divergence is detectable. It is not
   a failure mode to be hidden.

TemporalLock is a receipt log. It is not a blockchain product, not a
consensus protocol, not a court, and not a scoring engine.

---

## 2. Data model

Each receipt contains at minimum the v0.1.0 **core fields**:

| Field | Type | Rule |
|-------|------|------|
| `timestamp` | string | UTC ISO-8601. Observer-supplied, or `now` in UTC. |
| `summary` | string | Brief description of what was observed. |
| `evidence` | string | Supporting body and/or reference URI/path. **Required.** Empty evidence is invalid. |
| `confidence` | float | Assigned **by the observer**, inclusive range `0.0`–`1.0`. |
| `prev_hash` | string | SHA-256 hex of the previous receipt. Genesis uses 64 zero hex characters. |
| `hash` | string | SHA-256 hex of this receipt's canonical encoding, excluding `hash` itself. |

Implementations may carry additional optional fields (extra JSON keys on
a JSONL line). Those fields **must not** enter the core hash unless a
later **versioned** schema says so. v0.1.0 is core-only so that a chain
written today remains independently verifiable years later.

### Canonical encoding

The bytes that are hashed are UTF-8 JSON with:

- sorted keys;
- no extra whitespace (`separators=(",", ":")`);
- fields: `timestamp`, `summary`, `evidence`, `confidence`, `prev_hash`;
- `confidence` serialized as a JSON number with **exactly 6 decimal
  places** (example: `0.7` → `0.700000`).

The receipt's own `hash` field is excluded. See `temporallock/canon.py`.

This encoding is the stability contract of v0.1.0. Changing it without a
version bump would orphan existing chains.

### Storage

A chain is an in-memory list and/or a JSONL file (one receipt per line).
The file is opened append-only (mode `'a'`) after load. It is never
rewritten in place. Earlier lines' bytes must remain unchanged when a
new receipt is appended.

### Append-only

There is no modify and no delete. The only mutation is
`chain.append(...)`. Attempts to edit, pop, or replace raise
`AppendOnlyError`.

Corrections and disputes are **new receipts**. They may refer to a prior
hash in the evidence or summary text. An optional `re: <hash>` prefix in
the summary is fine. The old receipt is not mutated.

---

## 3. Cryptographic linking and forks

Linking uses SHA-256 from the Python standard library. No extra crypto
packages are required.

For a linear chain:

```
receipt[n].prev_hash == receipt[n-1].hash
```

Genesis:

```
receipt[0].prev_hash == 64 zero hex characters
```

A break — a stored hash that does not match the canonical digest of the
fields, or a `prev_hash` that does not match the previous receipt — is
immediately detectable by anyone who can read the file. No special
access is required. An independent verifier recomputes hashes from the
fields only.

### Forks

A **fork** is two (or more) receipts that share the same `prev_hash` and
have different hashes. Forks are **valid**. They are **detectable**
(`Chain.forks()` / `detect_forks(receipts)`). TemporalLock does not pick
a winner, does not rank length, and does not collapse divergence into a
single "canonical" history.

If two forks are stored as separate JSONL files, each file may still
verify internally: its own hashes match, and its own consecutive links
hold. A single linear file that contains both children of one parent
will fail the consecutive-link check; that is detection, not a demand
that one child be deleted.

Fork-permissive cryptographic linking is the point. Permission to fork
the *software* and permission to fork the *chain* are the same ethic.

---

## 4. Verification, independence, and limits

### Verification

```
temporallock verify path.jsonl
```

walks the chain, checks hashes and consecutive links, and exits 0 if
intact, nonzero if broken.

The library returns:

```
Chain.verify() -> VerifyResult(ok, length, first_hash, last_hash, errors)
```

Verification is mechanical. It does not read the summary for meaning.
It does not upgrade a high confidence into a fact. It does not treat
the first or last hash as authority.

### Independent verifier

Anyone can recompute `hash` from `timestamp`, `summary`, `evidence`,
`confidence`, and `prev_hash` using the canonical encoding in section 2.
Agreement with the stored `hash` is a check on the bytes, not a check
on the world.

### CLI surface (v0.1.0)

```
temporallock version
temporallock genesis --chain FILE.jsonl --summary "..." --evidence "..."
temporallock append  --chain FILE.jsonl --summary "..." --evidence "..."
                     [--confidence 0.7] [--timestamp ISO]
temporallock verify FILE.jsonl
temporallock show FILE.jsonl
```

`genesis` writes the first receipt. `append` requires an existing chain.
This is deliberate: creating a chain and extending a chain are different
acts.

### Limits (what this paper refuses)

TemporalLock does not:

- add consensus, mining, or tokens;
- compute or publish "truth scores";
- interpret summaries;
- elect a canonical fork;
- rewrite or redact receipts.

Those refusals are part of the specification, not optional product
taste. A fork of the software may add them; that fork is no longer
this spec.

---

## 5. v0.2.0 timeslate lattice (StaticClock × AZ-OS)

v0.2.0 elevates TemporalLock to an **immutable timeslate lattice**
hash-chained against the StaticClock gear-click timeline.

A **timeslate** is a receipt plus a StaticClock bind. The v0.1.0 core
hash is unchanged. Lattice extras are stored on the JSONL line and
hashed separately:

```
timeslate_hash = SHA-256(canonical{
  click_index,
  prev_timeslate_hash,
  receipt_hash,
  staticclock_click
})
```

`staticclock_click` is a local SHA-256 of a StaticClock-shaped
gear-click object (`product` forced to `staticclock`). TemporalLock
does not call StaticClock and does not schedule. A decreasing
`click_index` is a rollback and is refused. The same index is a fork
on one gear-click and is allowed.

**AZ-OS integrity role (honest).** AZ-OS is a portable ethical overlay
whose prefab hooks may write this lattice. TemporalLock is that
integrity log. It is not a kernel, not a remote shell, and not an
execution engine. Hosted `/v1` does not run AZ-OS and does not store
chains. Verification remains mechanical: hashes and links, not truth.

CLI additions: `temporallock lattice`, `temporallock timeslate`,
`temporallock click`.

Author remains **Aziel Eliab** only.

---

Aziel Eliab
July 2026 · lattice addendum September 2026
