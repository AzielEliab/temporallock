# temporallock download tracker

Isolated Worker `temporallock-download-tracker`. Project `temporallock`.
v0.2.0 serves the timeslate lattice runtime (StaticClock cross-hash).
KV namespace `TEMPORALLOCK_DOWNLOADS` bound as `DOWNLOADS`.
Does **not** 302 to GitHub on `/download`. Serves gzip via `ASSETS.fetch`,
`Cache-Control: private, no-store`.

GET `/` increments a **page-view** counter (separate from downloads).
GET `/download` increments **downloads**.
`/v1` never increments DOWNLOADS KV.
GET `/install.sh` one-click install (does not increment; script curls `/download`).
GET `/v1/skill` returns skill markdown (`text/markdown`). Does not increment views or downloads.

Host: https://temporallock-download-tracker.vibelock.workers.dev
