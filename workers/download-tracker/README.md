# temporallock download tracker

Isolated Worker `temporallock-download-tracker`. Project `temporallock`.
v0.2.0 serves the timeslate lattice runtime (StaticClock cross-hash).
KV namespace `TEMPORALLOCK_DOWNLOADS` bound as `DOWNLOADS`.
Does **not** 302 to GitHub on `/download`. Serves gzip via `ASSETS.fetch`,
`Cache-Control: private, no-store`.

GET `/` is the product homepage (workspace + counted download). Increments a **page-view** counter (separate from downloads).
GET `/download` increments **downloads**.
GET `/count` returns `{project, views, downloads, total}`. Does not increment views or downloads.
`/v1` never increments DOWNLOADS KV.
GET `/install.sh` one-click install (does not increment; script curls `/download`).
GET `/v1/skill` returns skill markdown (`text/markdown`). Does not increment views or downloads.
GET `/cite.json`, `/sitemap.xml`, `/robots.txt`, `/llms.txt` are SEO / cite surfaces. Do not increment downloads.
`/v1/mesh/*` PROXY to aziel-runtime suite mesh (`AZIEL_RUNTIME` / `https://aziel-runtime.vibelock.workers.dev`). Default OFF. QNM-BUILD-1.0 live|locked|isolated. QNS-CD-1.0 photon QNS1 packet transfer is a hub cite / Worker mesh cross-map (`QNS_CD_SPEC` + `QNS_CD` on status / Live Nodes). Local qnsd is coded in https://github.com/AzielEliab/qnm-node. Runtime cites + catalog field live in https://github.com/AzielEliab/aziel-runtime. Pair custody: https://github.com/AzielEliab/azinterface. Not a Softwares-tab product. No Node Gate. No public qnsd proxy. No auto-heal. Not anonymity. Human UI Live Nodes strip polls `GET /v1/mesh`.

Verify: `curl -sS -A 'Mozilla/5.0' https://temporallock-download-tracker.vibelock.workers.dev/v1/mesh/status` returns MESH-OK style JSON with `enabled: false` by default.

Host: https://temporallock-download-tracker.vibelock.workers.dev
