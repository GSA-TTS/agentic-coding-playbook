#!/usr/bin/env bash
# Ensure the universal Federal AI Agent Behavioral Contract is available.
#
# Thin wrapper around the self-contained scripts/ensure-contract.py (no
# third-party dependencies). Exit 0 = contract present; non-zero = fail-closed
# halt (do NOT proceed). See scripts/ensure-contract.py for the full precedence
# logic and the project's AGENTS.md "Prerequisite" section for policy.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$HERE/ensure-contract.py" --root "${1:-.}" "${@:2}"
