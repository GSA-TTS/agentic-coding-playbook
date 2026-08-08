"""Refresh the derived NIST SP 800-53 control id→title map from NIST OSCAL.

Fetches the SHA-pinned OSCAL catalog from usnistgov/oscal-content, extracts ONLY
the base control id→title pairs, and writes a small derived data file
(`data/nist-800-53-control-names.json`). The full ~10 MB OSCAL catalog is NEVER
vendored — we persist only the derived {id: title} map plus provenance.

This is a maintainer-run refresh (`make refresh-oscal`), NOT part of `make
generate` — generation and CI read the committed derived map, so they stay
deterministic and offline-safe. Re-run this when NIST publishes a catalog update
and review the diff.

Usage:
    python3 scripts/refresh_oscal_control_names.py [--check]

    --check : fetch + diff against the committed map; exit 1 if they differ
              (does not write). For an optional maintainer drift check.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path

# SHA-pinned OSCAL catalog (usnistgov/oscal-content). Bump deliberately + review
# the derived-map diff. Pin, never float, per the dependency-pinning rule.
OSCAL_COMMIT = "78650f02ad9321bb7b817846f8fbd4f2bcd620de"
OSCAL_URL = (
    "https://raw.githubusercontent.com/usnistgov/oscal-content/"
    f"{OSCAL_COMMIT}/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog-min.json"
)
DERIVED_REL = "data/nist-800-53-control-names.json"
_FETCH_TIMEOUT = 30


def _walk_controls(node: dict, out: dict[str, str]) -> None:
    """Collect base (non-enhancement) control id→title pairs, recursively."""
    for control in node.get("controls", []):
        cid = control.get("id", "")
        title = control.get("title", "")
        # Base controls only: "ac-2" (keep) vs enhancements "ac-2.1" (skip).
        if cid and "." not in cid and "-" in cid:
            out[cid.upper()] = title
        _walk_controls(control, out)


def _derive_map_from_catalog(catalog_json: dict) -> dict[str, str]:
    catalog = catalog_json["catalog"]
    names: dict[str, str] = {}
    for group in catalog.get("groups", []):
        _walk_controls(group, names)
    _walk_controls(catalog, names)
    return names


def _fetch_catalog() -> dict:
    req = urllib.request.Request(OSCAL_URL, method="GET")  # noqa: S310 (pinned https)
    with urllib.request.urlopen(req, timeout=_FETCH_TIMEOUT) as resp:  # noqa: S310
        if resp.status != 200:
            raise RuntimeError(f"OSCAL fetch failed: HTTP {resp.status}")
        return json.loads(resp.read().decode("utf-8"))


def _build_derived(catalog_json: dict) -> dict:
    catalog = catalog_json["catalog"]
    meta = catalog.get("metadata", {})
    names = _derive_map_from_catalog(catalog_json)
    return {
        "_provenance": {
            "source": "usnistgov/oscal-content NIST SP 800-53 Rev 5 catalog (min)",
            "oscal_commit": OSCAL_COMMIT,
            "catalog_version": meta.get("version"),
            "catalog_last_modified": meta.get("last-modified"),
            "note": (
                "Derived id→title map only. The full OSCAL catalog is NOT vendored. "
                "Regenerate with `make refresh-oscal`."
            ),
        },
        "controls": dict(sorted(names.items())),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Refresh derived NIST 800-53 control-name map")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Diff fetched map against the committed file; exit 1 if they differ (no write)",
    )
    args = parser.parse_args(argv)
    derived_path = Path(args.root) / DERIVED_REL

    try:
        catalog = _fetch_catalog()
    except Exception as exc:  # noqa: BLE001 - report + fail, never write partial
        print(f"ERROR: could not fetch OSCAL catalog: {exc}", file=sys.stderr)
        return 2

    derived = _build_derived(catalog)
    rendered = json.dumps(derived, indent=2, ensure_ascii=False) + "\n"

    if args.check:
        if not derived_path.is_file():
            print(f"ERROR: {derived_path} missing; run without --check to create", file=sys.stderr)
            return 1
        current = derived_path.read_text(encoding="utf-8")
        if current != rendered:
            print(
                f"DRIFT: {DERIVED_REL} differs from freshly-derived NIST OSCAL map. "
                "Run `make refresh-oscal` and review.",
                file=sys.stderr,
            )
            return 1
        print(f"OK: {DERIVED_REL} matches NIST OSCAL (commit {OSCAL_COMMIT[:12]})")
        return 0

    derived_path.write_text(rendered, encoding="utf-8")
    print(
        f"Wrote {DERIVED_REL}: {len(derived['controls'])} controls "
        f"(catalog {derived['_provenance']['catalog_version']}, commit {OSCAL_COMMIT[:12]})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
