"""Immutable observation receipt.

A receipt is a record of an observation at a moment. It is not a truth
claim, not an authority, and not a narrative. Corrections are new
receipts; this object cannot be edited.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from math import isfinite
from typing import Any, Mapping

from temporallock.errors import AppendOnlyError, ReceiptError
from temporallock.hashing import GENESIS_PREV_HASH, digest

_HEX = set("0123456789abcdef")


def utc_now() -> str:
    """Observer-clock 'now' as UTC ISO-8601 with a trailing Z, second precision."""
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _require_str(name: str, value: Any) -> str:
    if not isinstance(value, str):
        raise ReceiptError(f"{name} must be a string")
    return value


def validate_evidence(evidence: str) -> str:
    evidence = _require_str("evidence", evidence)
    if evidence.strip() == "":
        raise ReceiptError("empty evidence is invalid")
    return evidence


def validate_confidence(confidence: Any) -> float:
    try:
        value = float(confidence)
    except (TypeError, ValueError) as exc:
        raise ReceiptError("confidence must be a float in [0.0, 1.0]") from exc
    if not isfinite(value) or value < 0.0 or value > 1.0:
        raise ReceiptError("confidence must be a float in [0.0, 1.0] inclusive")
    return value


def validate_summary(summary: str) -> str:
    return _require_str("summary", summary)


def validate_timestamp(timestamp: str) -> str:
    ts = _require_str("timestamp", timestamp)
    if ts.strip() == "":
        raise ReceiptError("timestamp must be a non-empty UTC ISO-8601 string")
    return ts


@dataclass
class Receipt:
    """Frozen observation receipt (v0.1.0 core + optional v0.2.0 timeslate extras).

    Fields hashed (v0.1.0, unchanged): timestamp, summary, evidence,
    confidence, prev_hash. ``hash`` is SHA-256 of that encoding.

    Lattice extras (``staticclock_click``, ``click_index``,
    ``prev_timeslate_hash``, ``timeslate_hash``) are stored beside the
    receipt and MUST NOT enter the core hash.
    """

    timestamp: str
    summary: str
    evidence: str
    confidence: float
    prev_hash: str
    hash: str
    staticclock_click: str = ""
    click_index: int = 0
    prev_timeslate_hash: str = ""
    timeslate_hash: str = ""
    _frozen: bool = field(default=False, init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "timestamp", validate_timestamp(self.timestamp))
        object.__setattr__(self, "summary", validate_summary(self.summary))
        object.__setattr__(self, "evidence", validate_evidence(self.evidence))
        object.__setattr__(self, "confidence", validate_confidence(self.confidence))
        object.__setattr__(self, "prev_hash", _require_str("prev_hash", self.prev_hash))
        object.__setattr__(self, "hash", _require_str("hash", self.hash))
        object.__setattr__(self, "staticclock_click", _require_str("staticclock_click", self.staticclock_click or ""))
        try:
            object.__setattr__(self, "click_index", int(self.click_index))
        except (TypeError, ValueError) as exc:
            raise ReceiptError("click_index must be an integer >= 0") from exc
        if self.click_index < 0:
            raise ReceiptError("click_index must be an integer >= 0")
        object.__setattr__(self, "prev_timeslate_hash", _require_str("prev_timeslate_hash", self.prev_timeslate_hash or ""))
        object.__setattr__(self, "timeslate_hash", _require_str("timeslate_hash", self.timeslate_hash or ""))
        object.__setattr__(self, "_frozen", True)

    def __setattr__(self, name: str, value: Any) -> None:
        if getattr(self, "_frozen", False):
            raise AppendOnlyError(
                "receipts cannot be modified; append a correction as a new receipt"
            )
        object.__setattr__(self, name, value)

    def __delattr__(self, name: str) -> None:
        raise AppendOnlyError(
            "receipts cannot be deleted; append a correction as a new receipt"
        )

    def __hash__(self) -> int:  # type: ignore[override]
        return hash(self.hash)

    @classmethod
    def create(
        cls,
        *,
        summary: str,
        evidence: str,
        confidence: float = 1.0,
        timestamp: str | None = None,
        prev_hash: str = GENESIS_PREV_HASH,
    ) -> "Receipt":
        """Mint a new receipt, computing ``hash`` from the core fields."""
        ts = utc_now() if timestamp is None else timestamp
        conf = validate_confidence(confidence)
        rec_hash = digest(
            timestamp=validate_timestamp(ts),
            summary=validate_summary(summary),
            evidence=validate_evidence(evidence),
            confidence=conf,
            prev_hash=_require_str("prev_hash", prev_hash),
        )
        return cls(
            timestamp=ts,
            summary=summary,
            evidence=evidence,
            confidence=conf,
            prev_hash=prev_hash,
            hash=rec_hash,
        )

    def recomputed_hash(self) -> str:
        """Independent verifier: SHA-256 from fields only (ignores stored hash)."""
        return digest(
            timestamp=self.timestamp,
            summary=self.summary,
            evidence=self.evidence,
            confidence=self.confidence,
            prev_hash=self.prev_hash,
        )

    def hash_ok(self) -> bool:
        return self.recomputed_hash() == self.hash

    def to_dict(self) -> dict[str, Any]:
        body: dict[str, Any] = {
            "timestamp": self.timestamp,
            "summary": self.summary,
            "evidence": self.evidence,
            "confidence": self.confidence,
            "prev_hash": self.prev_hash,
            "hash": self.hash,
        }
        if self.timeslate_hash:
            body["staticclock_click"] = self.staticclock_click
            body["click_index"] = self.click_index
            body["prev_timeslate_hash"] = self.prev_timeslate_hash
            body["timeslate_hash"] = self.timeslate_hash
        return body

    def with_timeslate(
        self,
        *,
        staticclock_click: str,
        click_index: int,
        prev_timeslate_hash: str,
        timeslate_hash: str,
    ) -> "Receipt":
        """Copy core fields and attach lattice extras. Core hash is unchanged."""
        return Receipt(
            timestamp=self.timestamp,
            summary=self.summary,
            evidence=self.evidence,
            confidence=self.confidence,
            prev_hash=self.prev_hash,
            hash=self.hash,
            staticclock_click=staticclock_click,
            click_index=click_index,
            prev_timeslate_hash=prev_timeslate_hash,
            timeslate_hash=timeslate_hash,
        )

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Receipt":
        """Load core fields plus optional timeslate extras. Extras are not hashed."""
        missing = [k for k in ("timestamp", "summary", "evidence", "confidence", "prev_hash", "hash") if k not in data]
        if missing:
            raise ReceiptError(f"receipt missing fields: {missing}")
        extras: dict[str, Any] = {}
        if data.get("timeslate_hash"):
            extras = {
                "staticclock_click": data.get("staticclock_click") or "",
                "click_index": data.get("click_index") or 0,
                "prev_timeslate_hash": data.get("prev_timeslate_hash") or "",
                "timeslate_hash": data.get("timeslate_hash") or "",
            }
        return cls(
            timestamp=data["timestamp"],
            summary=data["summary"],
            evidence=data["evidence"],
            confidence=data["confidence"],
            prev_hash=data["prev_hash"],
            hash=data["hash"],
            **extras,
        )
