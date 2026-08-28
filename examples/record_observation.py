#!/usr/bin/env python3
"""Record observations as TemporalLock receipts. No network. No narrative."""

from __future__ import annotations

from pathlib import Path

from temporallock.chain import Chain

OUT = Path(__file__).resolve().parent / "_out"
CHAIN = OUT / "observations.jsonl"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    if CHAIN.exists():
        CHAIN.unlink()

    chain = Chain.genesis(
        CHAIN,
        summary="sky over the river was overcast",
        evidence="file:./sky.jpg note: observer facing east",
        confidence=0.85,
        timestamp="2026-07-12T14:30:00Z",
    )
    first = chain[-1]

    chain.append(
        summary="rain began on the west bank",
        evidence="https://example.invalid/gauge/west-bank",
        confidence=0.70,
        timestamp="2026-07-12T14:46:00Z",
    )

    # Correction is a new receipt. The first receipt is not mutated.
    chain.append(
        summary=f"re: {first.hash} facing was west, not east",
        evidence="file:./sky.jpg exif:ImageOrientation",
        confidence=0.90,
        timestamp="2026-07-12T15:02:00Z",
    )

    result = chain.verify()
    assert result.ok, result.errors
    assert chain[0].hash == first.hash
    print(f"wrote {CHAIN} n={len(chain)} last={result.last_hash}")
    print("receipts, not truth claims")


if __name__ == "__main__":
    main()
