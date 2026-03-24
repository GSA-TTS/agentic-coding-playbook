#!/bin/sh
# sync-generated-content.sh — Regenerate all derived repository artifacts

set -eu

SCRIPT_DIR=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd -P)
REPO_ROOT=$(CDPATH='' cd -- "${SCRIPT_DIR}/.." && pwd -P)

sh "${REPO_ROOT}/scripts/generate-index.sh" "$@"
sh "${REPO_ROOT}/scripts/generate-readme-structure.sh" "$@"
sh "${REPO_ROOT}/scripts/generate-readme-skills.sh" "$@"
sh "${REPO_ROOT}/scripts/generate-readme-changelog.sh" "$@"
