"""Worker homepage is TemporalLock software, not a downloads shell."""

from __future__ import annotations

from pathlib import Path

HOME = Path("workers/download-tracker/src/home.js").read_text(encoding="utf-8")
INDEX = Path("workers/download-tracker/src/index.js").read_text(encoding="utf-8")


def test_title_is_product_not_downloads_shell() -> None:
    assert "TemporalLock — Aziel Eliab" in HOME
    assert "TemporalLock downloads" not in HOME
    assert 'title: "TemporalLock"' in HOME or 'title: "TemporalLock"' in HOME


def test_seo_and_softwareapplication_json_ld() -> None:
    assert "application/ld+json" in HOME
    assert "SoftwareApplication" in HOME
    assert "Aziel Eliab" in HOME
    assert "cite.json" in HOME
    assert "sitemap.xml" in HOME
    assert "Everblooming sigil" in HOME
    assert "/sigil.png" in HOME


def test_workspace_calls_real_ops() -> None:
    for path in ("/v1/genesis", "/v1/append", "/v1/verify", "/v1/lattice", "/v1/gate"):
        assert path in HOME
    assert "btn-genesis" in HOME
    assert "btn-append" in HOME
    assert "btn-verify" in HOME
    assert "Timeslate workspace" in HOME


def test_download_install_and_identity_remain() -> None:
    assert "/download?asset=temporallock-0.2.0.tar.gz" in HOME
    assert "One-click install" in HOME
    assert "Aziel Eliab only" in HOME
    assert "Apache-2.0" in HOME
    assert "Forks welcome" in HOME or "Forks are welcome" in HOME


def test_no_invented_or_live_zenodo_identifier() -> None:
    assert "identifier:" not in HOME.split("export function jsonLd")[1].split("export function handleSeoRoutes")[0]
    assert "zenodo_status: \"historical_doi_tombstoned\"" in HOME
    assert "No DOI is invented here" in HOME
    assert "DOI =" not in INDEX
    assert "ZENODO =" not in INDEX


def test_worker_serves_home_and_seo() -> None:
    assert "renderHome" in INDEX
    assert "handleSeoRoutes" in INDEX
    assert 'url.pathname === "/"' in INDEX
    assert "/download" in INDEX
