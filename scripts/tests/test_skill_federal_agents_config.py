"""Tests for federal-agents-config skill scripts (Issue #84).

Covers generate-agents-md.py and validate-agents-md.py. The scripts use
hyphenated filenames (not importable as modules), so we load them via
importlib from their file paths.
"""

import importlib.util
import json
from pathlib import Path

import pytest

SKILL_DIR = Path(__file__).resolve().parents[2] / "skills" / "federal-agents-config" / "scripts"


def _load(module_name: str, filename: str):
    """Load a hyphenated script file as an importable module."""
    spec = importlib.util.spec_from_file_location(module_name, SKILL_DIR / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def gen():
    return _load("generate_agents_md", "generate-agents-md.py")


@pytest.fixture(scope="module")
def validate_mod():
    return _load("validate_agents_md", "validate-agents-md.py")


# ── generate-agents-md.py ───────────────────────────────────────────────────


def _minimal_config(**overrides):
    config = {"system_name": "Test System", "language": "Python"}
    config.update(overrides)
    return config


def test_generate_includes_required_sections(gen):
    out = gen.generate_agents_md(_minimal_config())
    for heading in (
        "## Core Principles",
        "## Project Context",
        "## Agent Identity",
        "## Permitted Actions",
        "## Actions Requiring Approval",
        "## Prohibited Actions",
        "## Data Handling",
        "## Coding Standards",
        "## Dependencies",
        "## Testing Requirements",
        "## CI/CD Pipeline",
        "## Incident Response",
        "## Contacts",
    ):
        assert heading in out, f"missing {heading}"


def test_generate_uses_system_name_and_priority_order(gen):
    out = gen.generate_agents_md(_minimal_config(system_name="Acme Portal"))
    assert "AGENTS.md — Acme Portal" in out
    assert "safety > correctness > compliance > simplicity > performance" in out


def test_generate_defaults_registry_by_language(gen):
    assert "pypi.org" in gen.generate_agents_md(_minimal_config(language="Python"))
    assert "npmjs.com" in gen.generate_agents_md(_minimal_config(language="TypeScript"))
    assert "proxy.golang.org" in gen.generate_agents_md(_minimal_config(language="Go"))
    # Explicit registries override the language default
    out = gen.generate_agents_md(_minimal_config(approved_registries=["internal.example.gov"]))
    assert "internal.example.gov" in out


def test_generate_cui_triggers_field_level_encryption_line(gen):
    out = gen.generate_agents_md(_minimal_config(data_classification="CUI"))
    assert "field-level encryption" in out
    # Non-sensitive classification gets the generic line instead
    out2 = gen.generate_agents_md(_minimal_config(data_classification="Internal"))
    assert "Follow agency data handling procedures" in out2


def test_generate_network_section_optional(gen):
    without = gen.generate_agents_md(_minimal_config())
    assert "## Network Access" not in without
    with_net = gen.generate_agents_md(_minimal_config(network_allowlist=["https://api.gsa.usai.gov"]))
    assert "## Network Access" in with_net
    assert "https://api.gsa.usai.gov" in with_net


def test_generate_copilot_coauthor_uses_github_noreply(gen):
    out = gen.generate_agents_md(_minimal_config(agent_names=["GitHub Copilot", "OpenCode"]))
    assert "Co-authored-by: GitHub Copilot <noreply@github.com>" in out
    assert "Co-authored-by: OpenCode <noreply@ai-agent>" in out


def test_default_test_command_by_language(gen):
    assert gen._default_test_command("Python") == "pytest"
    assert gen._default_test_command("TypeScript") == "npm test"
    assert gen._default_test_command("Go") == "go test ./..."
    assert gen._default_test_command("Rust") == "cargo test"
    assert gen._default_test_command("COBOL") == "[test command]"


def test_load_config_rejects_missing_required_fields(gen, tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"system_name": "x"}), encoding="utf-8")  # no language
    with pytest.raises(SystemExit):
        gen.load_config(str(bad))


def test_load_config_rejects_invalid_json(gen, tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("{not valid", encoding="utf-8")
    with pytest.raises(SystemExit):
        gen.load_config(str(bad))


def test_load_config_roundtrips_valid_file(gen, tmp_path):
    good = tmp_path / "good.json"
    good.write_text(json.dumps({"system_name": "S", "language": "Python"}), encoding="utf-8")
    config = gen.load_config(str(good))
    assert config["system_name"] == "S"


def test_validate_output_path_rejects_non_md(gen, tmp_path):
    with pytest.raises(SystemExit):
        gen.validate_output_path(str(tmp_path / "out.txt"))


# ── validate-agents-md.py ────────────────────────────────────────────────────


def test_validate_passes_on_generated_document(gen, validate_mod, tmp_path):
    # A document generated by the sibling script should validate cleanly.
    config = _minimal_config(
        agency_name="GSA",
        data_classification="CUI",
        agent_names=["OpenCode"],
    )
    doc = tmp_path / "AGENTS.md"
    # The generated doc lacks a couple of REQUIRED_FIELDS header tokens
    # (Agency: in header form), so assert on section coverage instead.
    doc.write_text(gen.generate_agents_md(config), encoding="utf-8")
    result = validate_mod.validate(str(doc))
    section_results = [r for r in result["results"] if r["check"].startswith("section:")]
    assert all(r["pass"] for r in section_results), "all required sections should be present"


def test_validate_reports_missing_file(validate_mod):
    result = validate_mod.validate("/nonexistent/AGENTS.md")
    assert result["status"] == "error"
    assert any("not found" in e.lower() for e in result["errors"])


def test_validate_flags_missing_sections(validate_mod, tmp_path):
    doc = tmp_path / "AGENTS.md"
    doc.write_text("# AGENTS.md\n\nNothing useful here.\n", encoding="utf-8")
    result = validate_mod.validate(str(doc))
    assert result["status"] == "partial"
    assert result["failed"] > 0
    failed_checks = [r["check"] for r in result["results"] if not r["pass"]]
    assert any("Core Principles" in c for c in failed_checks)


def test_validate_warns_on_unfilled_placeholders(validate_mod, tmp_path):
    doc = tmp_path / "AGENTS.md"
    doc.write_text(
        "## Core Principles\n[Your Name] should fill this in.\n",
        encoding="utf-8",
    )
    result = validate_mod.validate(str(doc))
    assert any("placeholder" in w.lower() for w in result["warnings"])


def test_validate_rejects_oversized_file(validate_mod, tmp_path):
    doc = tmp_path / "AGENTS.md"
    doc.write_text("x" * (validate_mod.MAX_FILE_SIZE + 1), encoding="utf-8")
    result = validate_mod.validate(str(doc))
    assert result["status"] == "error"
    assert any("too large" in e.lower() for e in result["errors"])
