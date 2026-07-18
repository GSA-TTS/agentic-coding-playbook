"""Validate data/scanner-registry.yaml against its JSON Schema and check
cross-field invariants + the NIST mapping. Mirrors the landscape-registry
test convention. (Playbook #155 / patterns #229.)

Uses PyYAML + the stdlib only (no jsonschema dependency, matching the existing
validate_landscape convention). The JSON Schema file is the published contract;
these tests enforce structural + cross-field invariants deterministically.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "data" / "scanner-registry.yaml"
SCHEMA = ROOT / "schemas" / "scanner-registry.schema.json"
NIST_MAP = ROOT / "data" / "nist-scanner-mapping.yaml"

CONTROL_RE = re.compile(r"^[A-Z]{2}-\d+")
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")

VALID_CATEGORIES = {"sast", "sca", "secrets", "iac", "container", "sbom", "license"}
VALID_OFFLINE = {"bundled", "db-split", "hard-net"}
REQUIRED_SCANNER_KEYS = {
    "id",
    "name",
    "category",
    "ecosystems",
    "install",
    "definitions",
    "output",
    "license",
    "origin",
    "maintenance",
}


def _load(p: Path):
    return yaml.safe_load(p.read_text(encoding="utf-8"))


def test_schema_file_is_valid_json_and_2020_12() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    assert schema["$schema"].endswith("2020-12/schema"), "schema must be draft-2020-12"
    assert schema.get("additionalProperties") is False


def test_registry_top_level_shape() -> None:
    reg = _load(REGISTRY)
    assert SEMVER_RE.match(reg["schema_version"])
    assert isinstance(reg["scanners"], list) and reg["scanners"]


def test_each_scanner_has_required_keys_and_valid_enums() -> None:
    for s in _load(REGISTRY)["scanners"]:
        missing = REQUIRED_SCANNER_KEYS - set(s)
        assert not missing, f"{s.get('id')}: missing {missing}"
        assert ID_RE.match(s["id"]), f"bad id: {s['id']}"
        assert s["category"] in VALID_CATEGORIES, f"{s['id']}: bad category {s['category']}"
        assert s["definitions"]["offline_mode"] in VALID_OFFLINE


def test_scanner_ids_are_unique() -> None:
    ids = [s["id"] for s in _load(REGISTRY)["scanners"]]
    assert len(ids) == len(set(ids)), "duplicate scanner ids"


def test_non_sarif_scanners_declare_a_converter() -> None:
    for s in _load(REGISTRY)["scanners"]:
        # SBOM tools emit an SBOM (SPDX/CycloneDX), not findings, so they are
        # not a SARIF source and need no converter.
        if s["category"] == "sbom":
            continue
        if not s["output"]["native_sarif"]:
            assert s["output"].get("converter"), f"{s['id']}: not SARIF-native but no converter declared"


def test_db_split_and_hard_net_declare_update_endpoint() -> None:
    for s in _load(REGISTRY)["scanners"]:
        mode = s["definitions"]["offline_mode"]
        if mode in ("db-split", "hard-net"):
            assert s["definitions"].get("update_endpoint"), (
                f"{s['id']}: offline_mode={mode} must declare update_endpoint"
            )


def test_telemetry_flagged_scanners_declare_disable_flags() -> None:
    for s in _load(REGISTRY)["scanners"]:
        if "telemetry-default-on" in s.get("supply_chain_flags", []):
            assert s.get("disable_telemetry"), f"{s['id']}: telemetry-default-on but no disable_telemetry flags"


def test_nist_control_ids_wellformed_in_registry() -> None:
    for s in _load(REGISTRY)["scanners"]:
        for c in s.get("nist_controls", []):
            assert CONTROL_RE.match(c), f"{s['id']}: malformed control {c}"


def test_nist_mapping_wellformed_and_failclosed() -> None:
    m = _load(NIST_MAP)
    for cat, v in m["by_category"].items():
        for c in v["controls"]:
            assert CONTROL_RE.match(c), f"by_category[{cat}]: malformed control {c}"
        assert v["mapping_confidence"] in ("high", "medium", "low")
    for cls, v in m["by_finding_class"].items():
        for c in v.get("add_controls", []):
            assert CONTROL_RE.match(c), f"by_finding_class[{cls}]: malformed control {c}"
    assert m["unmapped_policy"]["action"] == "escalate-to-human"
