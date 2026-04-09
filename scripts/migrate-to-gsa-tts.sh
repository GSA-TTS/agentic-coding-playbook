#!/usr/bin/env bash
# migrate-to-gsa-tts.sh — Clean migration to GSA-TTS org repository
#
# Two-stage process for zero-risk migration:
#
#   Stage 1 (--archive): Creates a verified-clean tarball from the source repo.
#     - git archive strips ALL history, emails, commit metadata
#     - Rewrites williamzujkowski → gsa-tts references
#     - Produces a single .tar.gz you can inspect before proceeding
#
#   Stage 2 (--push): Unpacks the tarball, creates git repo, tags, pushes.
#     - Cleans old releases/tags on the target
#     - Handles branch protection
#     - Force-pushes clean history
#     - Creates GitHub releases with changelog excerpts
#
# Compatible with macOS (BSD) and Linux (GNU) tools.
#
# Usage:
#   ./scripts/migrate-to-gsa-tts.sh --archive              # Stage 1: create tarball
#   ./scripts/migrate-to-gsa-tts.sh --verify                # Inspect tarball for leaks
#   ./scripts/migrate-to-gsa-tts.sh --push                  # Stage 2: push to gsa-tts
#   ./scripts/migrate-to-gsa-tts.sh --push --dry-run        # Stage 2: local only, no push

set -euo pipefail

# ── Configuration ──────────────────────────────────────────────────

SOURCE_REPO="williamzujkowski/agentic-coding-playbook"
TARGET_REPO="gsa-tts/agentic-coding-playbook"
TARGET_URL="git@github.com:${TARGET_REPO}.git"
SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ARCHIVE_PATH="${SOURCE_DIR}/migration-archive.tar.gz"
WORK_DIR="/tmp/gsa-tts-migration-$(date +%s)"

# Version history — tags to recreate (oldest first)
VERSIONS=(
    "v0.1.0"
    "v0.1.1"
    "v0.2.0"
    "v0.2.1"
    "v0.3.0"
    "v0.4.0"
    "v0.5.0"
    "v0.5.1"
    "v0.6.0"
)
CURRENT_VERSION="${VERSIONS[${#VERSIONS[@]}-1]}"

# Strings that must NOT appear in the archive
LEAK_PATTERNS=(
    "williamzujkowski@"
    "/home/william"
    "williamzujkowski/agentic"
    "williamzujkowski/agentic-ai"
)

# Note: williamzujkowski/agentic-coding-playbook is allowed in the
# migration script itself (SOURCE_REPO reference for attribution).

# ── Cross-platform helpers ────────────────────────────────────────

# BSD sed (macOS) requires -i '' while GNU sed requires -i without arg
sed_inplace() {
    if sed --version 2>/dev/null | grep -q GNU; then
        sed -i "$@"
    else
        sed -i '' "$@"
    fi
}

# macOS uses shasum, Linux uses sha256sum
sha256() {
    if command -v sha256sum >/dev/null 2>&1; then
        sha256sum "$1" | awk '{print $1}'
    else
        shasum -a 256 "$1" | awk '{print $1}'
    fi
}

# ── Functions ─────────────────────────────────────────────────────

usage() {
    echo "Usage: $0 [--archive | --verify | --push [--dry-run]]"
    echo ""
    echo "  --archive    Stage 1: Create clean tarball from source repo"
    echo "  --verify     Inspect tarball for personal data leaks"
    echo "  --push       Stage 2: Unpack tarball, push to gsa-tts"
    echo "  --dry-run    With --push: create local repo only, skip push"
    exit 1
}

# ── Parse args ────────────────────────────────────────────────────

MODE=""
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --archive) MODE="archive"; shift ;;
        --verify)  MODE="verify"; shift ;;
        --push)    MODE="push"; shift ;;
        --dry-run) DRY_RUN=true; shift ;;
        -h|--help) usage ;;
        *) echo "Unknown option: $1"; usage ;;
    esac
done

[[ -z "${MODE}" ]] && usage

# ══════════════════════════════════════════════════════════════════
# Stage 1: Archive
# ══════════════════════════════════════════════════════════════════

if [[ "${MODE}" == "archive" ]]; then
    echo "=== Stage 1: Creating clean archive ==="
    echo ""

    # Step 1: git archive to a temp dir (strips ALL git history)
    echo "Step 1: Exporting clean snapshot via git archive..."
    STAGING=$(mktemp -d)
    git -C "${SOURCE_DIR}" archive --format=tar HEAD \
        -- . ':!MIGRATION.md' ':!migration-archive.tar.gz' \
        | tar -xf - -C "${STAGING}"
    echo "  Exported to staging dir"

    # Step 2: Rewrite personal references
    echo ""
    echo "Step 2: Rewriting references..."

    # CHANGELOG.md — rewrite repo URLs
    if [[ -f "${STAGING}/CHANGELOG.md" ]]; then
        sed_inplace \
            -e "s|github.com/williamzujkowski/agentic-coding-playbook|github.com/${TARGET_REPO}|g" \
            -e "s|github.com/williamzujkowski/agentic-ai-playbook|github.com/${TARGET_REPO}|g" \
            "${STAGING}/CHANGELOG.md"
        echo "  Rewrote CHANGELOG.md links"
    fi

    # Reset release-please manifest
    cat > "${STAGING}/.release-please-manifest.json" << MANIFEST
{
  ".": "${CURRENT_VERSION#v}"
}
MANIFEST
    echo "  Reset release-please manifest to ${CURRENT_VERSION}"

    # Step 3: Verify no personal data leaked
    echo ""
    echo "Step 3: Scanning for personal data..."
    LEAKS_FOUND=false

    for pattern in "${LEAK_PATTERNS[@]}"; do
        # Search all files, exclude the migration script itself
        HITS=$(grep -rn "${pattern}" "${STAGING}" \
            --exclude="migrate-to-gsa-tts.sh" \
            2>/dev/null || true)
        if [[ -n "${HITS}" ]]; then
            echo "  LEAK FOUND: '${pattern}'"
            echo "${HITS}" | head -5 | sed 's/^/    /'
            LEAKS_FOUND=true
        fi
    done

    if [[ "${LEAKS_FOUND}" == "true" ]]; then
        echo ""
        echo "ERROR: Personal data found in archive. Fix before proceeding."
        rm -rf "${STAGING}"
        exit 1
    fi
    echo "  No leaks detected"

    # Step 4: Create tarball
    echo ""
    echo "Step 4: Creating tarball..."
    tar -czf "${ARCHIVE_PATH}" -C "${STAGING}" .
    rm -rf "${STAGING}"

    SIZE=$(du -h "${ARCHIVE_PATH}" | awk '{print $1}')
    SHA=$(sha256 "${ARCHIVE_PATH}")
    echo "  Archive: ${ARCHIVE_PATH} (${SIZE})"
    echo "  SHA256:  ${SHA}"

    echo ""
    echo "=== Stage 1 complete ==="
    echo ""
    echo "Next steps:"
    echo "  1. Inspect:  $0 --verify"
    echo "  2. Test:     $0 --push --dry-run"
    echo "  3. Migrate:  $0 --push"
    exit 0
fi

# ══════════════════════════════════════════════════════════════════
# Verify: Inspect archive for leaks
# ══════════════════════════════════════════════════════════════════

if [[ "${MODE}" == "verify" ]]; then
    echo "=== Verifying archive ==="

    if [[ ! -f "${ARCHIVE_PATH}" ]]; then
        echo "ERROR: No archive found at ${ARCHIVE_PATH}"
        echo "Run: $0 --archive"
        exit 1
    fi

    STAGING=$(mktemp -d)
    tar -xzf "${ARCHIVE_PATH}" -C "${STAGING}"

    echo ""
    echo "--- Scanning for personal identifiers ---"
    CLEAN=true

    # Check for email addresses (use -E for extended regex on both BSD and GNU grep)
    EMAILS=$(grep -rn -E "@gmail|@proton|@yahoo|@hotmail|williamzujkowski@" "${STAGING}" \
        --exclude="migrate-to-gsa-tts.sh" 2>/dev/null || true)
    if [[ -n "${EMAILS}" ]]; then
        echo "FAIL: Personal email addresses found:"
        echo "${EMAILS}" | sed "s|${STAGING}/|  |g"
        CLEAN=false
    else
        echo "  OK: No personal email addresses"
    fi

    # Check for personal GitHub handle in non-migration files
    HANDLE=$(grep -rn "williamzujkowski" "${STAGING}" \
        --exclude="migrate-to-gsa-tts.sh" 2>/dev/null || true)
    if [[ -n "${HANDLE}" ]]; then
        echo "FAIL: Personal GitHub handle found:"
        echo "${HANDLE}" | sed "s|${STAGING}/|  |g"
        CLEAN=false
    else
        echo "  OK: No personal GitHub handle references"
    fi

    # Check for private IPs
    PRIVATE_IPS=$(grep -rn -E "192\.168\.|10\.[0-9]+\.|172\.16\." "${STAGING}" 2>/dev/null || true)
    if [[ -n "${PRIVATE_IPS}" ]]; then
        echo "WARN: Private IP addresses found:"
        echo "${PRIVATE_IPS}" | sed "s|${STAGING}/|  |g"
    else
        echo "  OK: No private IP addresses"
    fi

    # Check for home directory paths
    HOMEPATHS=$(grep -rn -E "/home/william|/Users/" "${STAGING}" 2>/dev/null || true)
    if [[ -n "${HOMEPATHS}" ]]; then
        echo "FAIL: Home directory paths found:"
        echo "${HOMEPATHS}" | sed "s|${STAGING}/|  |g"
        CLEAN=false
    else
        echo "  OK: No home directory paths"
    fi

    # Check for API key patterns (exclude .py test files)
    APIKEYS=$(grep -rn -E "sk-[a-zA-Z0-9]{20}|ghp_[a-zA-Z0-9]{36}|AKIA[A-Z0-9]{16}" "${STAGING}" \
        --exclude="*.py" 2>/dev/null || true)
    if [[ -n "${APIKEYS}" ]]; then
        echo "FAIL: Possible API keys found (outside test files):"
        echo "${APIKEYS}" | sed "s|${STAGING}/|  |g"
        CLEAN=false
    else
        echo "  OK: No API keys outside test files"
    fi

    # Verify no .git directory
    if [[ -d "${STAGING}/.git" ]]; then
        echo "FAIL: .git directory found in archive!"
        CLEAN=false
    else
        echo "  OK: No .git directory (history is clean)"
    fi

    echo ""
    echo "--- File count ---"
    FILE_COUNT=$(find "${STAGING}" -type f | wc -l | tr -d ' ')
    echo "${FILE_COUNT} files in archive"

    rm -rf "${STAGING}"

    echo ""
    if [[ "${CLEAN}" == "true" ]]; then
        echo "=== CLEAN — safe to push ==="
    else
        echo "=== ISSUES FOUND — fix before pushing ==="
        exit 1
    fi
    exit 0
fi

# ══════════════════════════════════════════════════════════════════
# Stage 2: Push
# ══════════════════════════════════════════════════════════════════

if [[ "${MODE}" == "push" ]]; then
    if [[ "${DRY_RUN}" == "true" ]]; then
        echo "=== Stage 2: Push (DRY RUN) ==="
    else
        echo "=== Stage 2: Push to ${TARGET_REPO} ==="
    fi

    if [[ ! -f "${ARCHIVE_PATH}" ]]; then
        echo "ERROR: No archive found at ${ARCHIVE_PATH}"
        echo "Run: $0 --archive"
        exit 1
    fi

    # Step 1: Unpack archive
    echo ""
    echo "Step 1: Unpacking archive..."
    mkdir -p "${WORK_DIR}"
    tar -xzf "${ARCHIVE_PATH}" -C "${WORK_DIR}"
    echo "  Unpacked to ${WORK_DIR}"

    # Step 2: Initialize git repo
    echo ""
    echo "Step 2: Initializing clean git repository..."
    cd "${WORK_DIR}"
    git init -b main
    git add -A
    git commit -m "feat: initial import of agentic-coding-playbook ${CURRENT_VERSION}

Imported from ${SOURCE_REPO} with clean history.
Original development history: https://github.com/${SOURCE_REPO}

This is a US federal government work product released under CC0 1.0.
"
    echo "  Created initial commit"

    # Step 3: Create version tags
    echo ""
    echo "Step 3: Creating version tags..."
    INITIAL_COMMIT=$(git rev-parse HEAD)
    for version in "${VERSIONS[@]}"; do
        git tag -a "${version}" "${INITIAL_COMMIT}" -m "Release ${version}

See CHANGELOG.md for release notes.
Migrated from ${SOURCE_REPO}."
        echo "  Created tag ${version}"
    done

    # Dry run stops here
    if [[ "${DRY_RUN}" == "true" ]]; then
        echo ""
        echo "=== DRY RUN COMPLETE ==="
        echo "  Local repo: ${WORK_DIR}"
        echo "  Commits: $(git rev-list --count HEAD)"
        echo "  Tags: $(git tag | wc -l | tr -d ' ')"
        echo ""
        echo "To inspect: cd ${WORK_DIR} && git log --oneline --decorate"
        echo "To push manually:"
        echo "  git remote add origin ${TARGET_URL}"
        echo "  git push -u origin main --tags --force"
        exit 0
    fi

    # Step 4: Clean target repo
    echo ""
    echo "Step 4: Cleaning target repo..."

    # Check for branch protection
    PROTECTION=$(gh api "repos/${TARGET_REPO}/branches/main/protection" 2>/dev/null && echo "protected" || echo "unprotected")
    RESTORE_PROTECTION=false
    if [[ "${PROTECTION}" == "protected" ]]; then
        echo "  Temporarily disabling branch protection..."
        gh api -X DELETE "repos/${TARGET_REPO}/branches/main/protection" 2>/dev/null || true
        RESTORE_PROTECTION=true
    fi

    # Delete old releases
    echo "  Cleaning old releases..."
    OLD_RELEASES=$(gh release list --repo "${TARGET_REPO}" --json tagName -q '.[].tagName' 2>/dev/null || true)
    if [[ -n "${OLD_RELEASES}" ]]; then
        echo "${OLD_RELEASES}" | while read -r tag; do
            gh release delete "${tag}" --repo "${TARGET_REPO}" --yes --cleanup-tag 2>/dev/null || true
            echo "    Deleted release: ${tag}"
        done
    fi

    # Delete old remote tags
    echo "  Cleaning old tags..."
    REMOTE_TAGS=$(git ls-remote --tags "${TARGET_URL}" 2>/dev/null | awk '{print $2}' | sed 's|refs/tags/||' | sed 's|\^{}||' | sort -u || true)
    if [[ -n "${REMOTE_TAGS}" ]]; then
        for tag in ${REMOTE_TAGS}; do
            git push "${TARGET_URL}" --delete "refs/tags/${tag}" 2>/dev/null || true
        done
    fi

    # Step 5: Push
    echo ""
    echo "Step 5: Pushing to ${TARGET_REPO}..."
    git remote add origin "${TARGET_URL}"
    git push -u origin main --tags --force
    echo "  Force-pushed main + all tags"

    # Restore branch protection
    if [[ "${RESTORE_PROTECTION}" == "true" ]]; then
        echo "  Restoring branch protection..."
        gh api -X PUT "repos/${TARGET_REPO}/branches/main/protection" \
            -f 'required_status_checks=null' \
            -F 'enforce_admins=false' \
            -f 'required_pull_request_reviews=null' \
            -f 'restrictions=null' 2>/dev/null || echo "  Could not restore protection — re-enable manually"
    fi

    # Step 6: Create GitHub releases
    echo ""
    echo "Step 6: Creating GitHub releases..."

    extract_changelog() {
        local version="${1}"
        local changelog="${WORK_DIR}/CHANGELOG.md"
        local ver_no_v="${version#v}"
        # Use awk instead of sed + head -n -1 (BSD head doesn't support negative)
        awk "/^## \[${ver_no_v}\]/{found=1; next} /^## \[/{if(found) exit} found{print}" "${changelog}"
    }

    for version in "${VERSIONS[@]}"; do
        changelog_section=$(extract_changelog "${version}" 2>/dev/null || echo "Release ${version}")
        [[ -z "${changelog_section}" ]] && changelog_section="Release ${version} — see CHANGELOG.md for details."

        latest_flag="--latest=false"
        [[ "${version}" == "${CURRENT_VERSION}" ]] && latest_flag="--latest"

        gh release create "${version}" \
            --repo "${TARGET_REPO}" \
            --title "${version}" \
            --notes "${changelog_section}" \
            ${latest_flag} \
            --verify-tag || echo "  Failed to create release ${version}"
        echo "  Created release ${version}"
    done

    # Step 7: Verify
    echo ""
    echo "Step 7: Verification..."
    echo "  Releases: $(gh release list --repo "${TARGET_REPO}" | wc -l | tr -d ' ')"
    echo "  Tags:     $(git tag | wc -l | tr -d ' ')"

    echo ""
    echo "=== Migration complete ==="
    echo ""
    echo "Target repo: https://github.com/${TARGET_REPO}"
    echo ""
    echo "Post-migration steps:"
    echo "  1. Verify CI passes: https://github.com/${TARGET_REPO}/actions"
    echo "  2. Update any external links pointing to ${SOURCE_REPO}"
    echo "  3. Add a redirect notice to the source repo README"
    echo "  4. Configure branch protection on the target repo"
    echo "  5. Set up team access in the gsa-tts org"
    echo ""
    echo "Local working copy: ${WORK_DIR}"
    echo "Archive: ${ARCHIVE_PATH}"
    exit 0
fi
