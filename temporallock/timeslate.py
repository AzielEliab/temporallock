"""Immutable timeslate lattice, hash-chained against StaticClock.

A timeslate is a receipt bound to one StaticClock gear-click. The v0.1.0
core receipt hash is unchanged. Lattice extras (click, index, timeslate
hash) are stored beside the receipt and hashed separately.

TemporalLock is the integrity lattice AZ-OS prefab hooks can write into.
It is not a kernel, not a scheduler, and not a truth oracle. Hosted
``/v1`` does not run AZ-OS and does not store chains.

Author: Aziel Eliab.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence

from temporallock.errors import LatticeError, ReceiptError
from temporallock.hashing import GENESIS_PREV_HASH
from temporallock.receipt import Receipt

AUTHOR = "Aziel Eliab"
PRODUCT = "temporallock"
STATICCLOCK_PRODUCT = "staticclock"
STATICCLOCK_HOST = "https://staticclock-download-tracker.vibelock.workers.dev"
AZOS_HOST = "https://azos-download-tracker.vibelock.workers.dev"
ROLE = "immutable timeslate lattice"
MOTTO = "Receipts, not truth claims."
HONEST_SCOPE = (
    "THIS IS: an immutable timeslate lattice hash-chained against the "
    "StaticClock gear-click timeline, used as the AZ-OS integrity log. "
    "THIS IS NOT: a kernel, scheduler, truth score, court, or remote shell. "
    "Hosted /v1 does not store chains and does not run AZ-OS. Author Aziel Eliab."
)

LATTICE_FIELDS = (
    "click_index",
    "prev_timeslate_hash",
    "receipt_hash",
    "staticclock_click",
)


def _require_hex64(name: str, value: str) -> str:
    if not isinstance(value, str):
        raise ReceiptError(f"{name} must be a string")
    text = value.strip().lower()
    if len(text) != 64 or any(c not in "0123456789abcdef" for c in text):
        raise ReceiptError(f"{name} must be 64 lowercase hex characters")
    return text


def validate_click_index(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        try:
            value = int(value)
        except (TypeError, ValueError) as exc:
            raise ReceiptError("click_index must be an integer >= 0") from exc
    if value < 0:
        raise ReceiptError("click_index must be an integer >= 0")
    return value


def _sorted_json(payload: Mapping[str, Any]) -> bytes:
    return json.dumps(
        dict(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def timeslate_digest(
    receipt_hash: str,
    staticclock_click: str,
    prev_timeslate_hash: str,
    click_index: int,
) -> str:
    """SHA-256 of the lattice bind. Does not enter the v0.1.0 core hash."""
    payload = {
        "click_index": validate_click_index(click_index),
        "prev_timeslate_hash": _require_hex64("prev_timeslate_hash", prev_timeslate_hash),
        "receipt_hash": _require_hex64("receipt_hash", receipt_hash),
        "staticclock_click": _require_hex64("staticclock_click", staticclock_click),
    }
    return hashlib.sha256(_sorted_json(payload)).hexdigest()


def staticclock_click_digest(payload: Mapping[str, Any] | None = None) -> str:
    """Local SHA-256 of a StaticClock-shaped gear-click. No network.

    TemporalLock does not call StaticClock. The caller supplies an advisory
    or action object; this digest is the click the timeslate binds to.
    ``product`` is always forced to ``staticclock``.
    """
    body: dict[str, Any] = dict(payload or {})
    body["product"] = STATICCLOCK_PRODUCT
    body.setdefault("kind", "gear-click")
    return hashlib.sha256(_sorted_json(body)).hexdigest()


def default_gear_click(*, timestamp: str, click_index: int) -> str:
    """Derive a StaticClock click from the observation second + index."""
    return staticclock_click_digest(
        {
            "kind": "gear-click",
            "timestamp": timestamp,
            "click_index": validate_click_index(click_index),
        }
    )


def parse_utc_seconds(timestamp: str) -> int | None:
    """Best-effort UTC unix seconds from an ISO-8601 string. None if unknown."""
    text = timestamp.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp())


@dataclass(frozen=True)
class LatticeResult:
    """Mechanical lattice walk. Not a truth score. Not an AZ-OS halt."""

    ok: bool
    length: int
    bound: int
    cross_hash: bool
    first_hash: str | None
    last_hash: str | None
    last_timeslate_hash: str | None
    last_click_index: int | None
    errors: list[str] = field(default_factory=list)
    receipt_ok: bool = True
    staticclock: str = STATICCLOCK_HOST
    role: str = ROLE
    note: str = (
        "Timeslate lattice integrity only. Receipts, not truth claims. "
        "AZ-OS prefab hooks may write here; this log does not execute software."
    )


def prev_timeslate_link(prev: Receipt | None) -> str:
    """Previous lattice node, or the v0.1.0 receipt hash as a bridge."""
    if prev is None:
        return GENESIS_PREV_HASH
    if prev.timeslate_hash:
        return prev.timeslate_hash
    return prev.hash


def min_click_index(prev: Receipt | None) -> int:
    if prev is None:
        return 0
    if prev.timeslate_hash or prev.staticclock_click:
        return prev.click_index
    return 0


def resolve_click(
    *,
    timestamp: str,
    prev: Receipt | None,
    staticclock_click: str | None = None,
    click_index: int | None = None,
    click_payload: Mapping[str, Any] | None = None,
) -> tuple[str, int]:
    """Pick the next gear-click. Refuses a decreasing click_index."""
    floor = min_click_index(prev)
    if click_index is None:
        index = 0 if prev is None else floor + 1
    else:
        index = validate_click_index(click_index)
    if index < floor:
        raise LatticeError(
            f"StaticClock rollback refused: click_index {index} < previous {floor}"
        )
    if staticclock_click:
        click = _require_hex64("staticclock_click", staticclock_click)
    elif click_payload is not None:
        click = staticclock_click_digest(click_payload)
    else:
        click = default_gear_click(timestamp=timestamp, click_index=index)
    return click, index


def bind_timeslate(
    receipt: Receipt,
    *,
    prev: Receipt | None = None,
    staticclock_click: str | None = None,
    click_index: int | None = None,
    click_payload: Mapping[str, Any] | None = None,
) -> Receipt:
    """Return a new receipt object with lattice extras filled.

    The v0.1.0 core hash is already computed. This only sets extras.
    """
    click, index = resolve_click(
        timestamp=receipt.timestamp,
        prev=prev,
        staticclock_click=staticclock_click,
        click_index=click_index,
        click_payload=click_payload,
    )
    prev_tl = prev_timeslate_link(prev)
    tl_hash = timeslate_digest(receipt.hash, click, prev_tl, index)
    return receipt.with_timeslate(
        staticclock_click=click,
        click_index=index,
        prev_timeslate_hash=prev_tl,
        timeslate_hash=tl_hash,
    )


def verify_lattice(receipts: Sequence[Receipt], *, receipt_errors: Sequence[str] = ()) -> LatticeResult:
    """Walk timeslate binds and refuse StaticClock rollbacks."""
    errors = list(receipt_errors)
    n = len(receipts)
    bound = 0
    last_tl = None
    last_click = None
    for i, rec in enumerate(receipts):
        if not rec.timeslate_hash:
            if i > 0 and receipts[i - 1].timeslate_hash:
                errors.append(f"index {i}: missing timeslate after lattice bind")
            continue
        bound += 1
        try:
            expected = timeslate_digest(
                rec.hash,
                rec.staticclock_click,
                rec.prev_timeslate_hash,
                rec.click_index,
            )
        except ReceiptError as exc:
            errors.append(f"index {i}: {exc}")
            continue
        if rec.timeslate_hash != expected:
            errors.append(
                f"index {i}: stored timeslate_hash {rec.timeslate_hash} != recomputed {expected}"
            )
        if i == 0:
            if rec.prev_timeslate_hash != GENESIS_PREV_HASH:
                errors.append(
                    f"index 0: prev_timeslate_hash {rec.prev_timeslate_hash} != genesis zeros"
                )
        else:
            prev = receipts[i - 1]
            expected_prev = prev_timeslate_link(prev)
            if rec.prev_timeslate_hash != expected_prev:
                errors.append(
                    f"index {i}: prev_timeslate_hash {rec.prev_timeslate_hash} "
                    f"!= previous timeslate {expected_prev}"
                )
            floor = min_click_index(prev)
            if rec.click_index < floor:
                errors.append(
                    f"index {i}: StaticClock rollback: click_index {rec.click_index} < {floor}"
                )
        last_tl = rec.timeslate_hash
        last_click = rec.click_index
    first = receipts[0].hash if n else None
    last = receipts[-1].hash if n else None
    if n and last_click is None and receipts[-1].timeslate_hash:
        last_click = receipts[-1].click_index
        last_tl = receipts[-1].timeslate_hash
    return LatticeResult(
        ok=not errors,
        length=n,
        bound=bound,
        cross_hash=bound > 0,
        first_hash=first,
        last_hash=last,
        last_timeslate_hash=last_tl,
        last_click_index=last_click,
        errors=errors,
        receipt_ok=not receipt_errors,
    )
