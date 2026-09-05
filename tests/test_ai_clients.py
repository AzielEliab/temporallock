"""Public copy lists the full AI client set, not an exclusive trio."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = (ROOT / "README.md").read_text(encoding="utf-8")
SKILL = (ROOT / "SKILL.md").read_text(encoding="utf-8")
RUNTIME = (ROOT / "workers/download-tracker/src/runtime.js").read_text(encoding="utf-8")

FULL_CLIENTS = (
    "ChatGPT (GPT Actions / OpenAI)",
    "Grok (xAI)",
    "Venice",
    "Claude (Anthropic)",
    "Cursor (MCP)",
    "Glama (MCP)",
    "Perplexity",
    "Microsoft Copilot / Bing",
    "Google Gemini / Vertex",
    "Mistral",
    "Meta AI",
    "Apple Intelligence surfaces",
    "Amazon Q tooling",
    "DuckAssist",
    "You.com",
    "Cohere",
    "other MCP/OpenAPI-capable assistants",
)


def test_readme_heading_is_generic() -> None:
    assert "## Use with AI assistants" in README
    assert "## Use with Grok, ChatGPT, Venice" not in README
    assert "Grok / ChatGPT / Venice" not in README


def test_readme_lists_full_client_set_and_keeps_import_notes() -> None:
    for name in FULL_CLIENTS:
        assert name in README
    assert "openapi.json" in README
    assert "aziel-runtime.vibelock.workers.dev/mcp" in README
    assert "Aziel Eliab only" in README


def test_skill_and_worker_copy_list_full_client_set() -> None:
    exclusive = "Grok: import the catalog OpenAPI as a custom tool. ChatGPT: GPT Actions. Venice: HTTP tools."
    exclusive_short = "Grok: import catalog or Worker OpenAPI as a custom tool. ChatGPT: GPT Actions. Venice: HTTP tools."
    for text in (SKILL, RUNTIME):
        assert exclusive not in text
        assert exclusive_short not in text
        for name in FULL_CLIENTS:
            assert name in text
        assert "Aziel Eliab" in text
        assert "openapi.json" in text
        assert "aziel-runtime.vibelock.workers.dev/mcp" in text


def test_ai_html_heading_is_generic() -> None:
    assert "<h2>Use with AI assistants</h2>" in RUNTIME
    assert "<h2>ChatGPT (GPT Actions)</h2>" not in RUNTIME
    assert "<h2>Grok / xAI</h2>" not in RUNTIME
    assert "<h2>Venice</h2>" not in RUNTIME
    assert "<h2>OpenAPI import</h2>" in RUNTIME
    assert "<h2>MCP catalog</h2>" in RUNTIME
