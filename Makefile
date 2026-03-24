SHELL := /bin/bash

.DEFAULT_GOAL := help

EXPORT_TARGET ?=
EXPORT_OUTPUT ?=
EXPORT_PROFILE ?= core
EXPORT_PROJECT_NAME ?= Your Project Name
EXPORT_SKILLS ?=
EXPORT_INCLUDES ?=
EXPORT_OVERWRITE ?= false
VERSION ?=

.PHONY: help bootstrap fix verify clean export export-dry-run doctor release-check release-tag

help: ## Show available commands
	@echo "Everyday workflow:"
	@echo "  bootstrap      Install hooks and prepare local tooling"
	@echo "  fix            Regenerate derived content and run local hooks"
	@echo "  verify         Run CI-like validation locally"
	@echo ""
	@echo "Exporting bundles:"
	@echo "  export         Export an agent bundle into a target repo or output directory"
	@echo "  export-dry-run Preview an export without writing files"
	@echo ""
	@echo "Diagnostics and cleanup:"
	@echo "  doctor         Check local tooling and script readiness"
	@echo "  clean          Remove local Python cache artifacts"
	@echo ""
	@echo "Most common commands:"
	@echo "  make fix"
	@echo "  make verify"
	@echo "  make export-dry-run EXPORT_TARGET=../my-repo"
	@echo "  make export EXPORT_TARGET=../my-repo EXPORT_OVERWRITE=true"

bootstrap: ## Install hooks and set executable bits for repo scripts
	@command -v pre-commit >/dev/null 2>&1 || { echo "Missing: pre-commit (brew install pre-commit)"; exit 1; }
	@command -v shellcheck >/dev/null 2>&1 || { echo "Missing: shellcheck (brew install shellcheck)"; exit 1; }
	@pre-commit install
	@chmod +x scripts/*.sh scripts/lib/*.sh
	@find skills -type f \( -name "*.sh" -o -name "*.py" \) -exec chmod +x {} \;
	@echo "Bootstrap complete."

fix: ## Regenerate derived content and run all local hooks
	@bash scripts/sync-generated-content.sh
	@prek run --all-files || true
	@echo ""
	@echo "If hooks changed files, stage them and run your commit again."

verify: ## Run CI-like validation locally
	@bash scripts/sync-generated-content.sh --check
	@bash scripts/validate-docs.sh
	@bash scripts/validate-skills.sh
	@bash scripts/run-shellcheck.sh
	@prek run --all-files

export: ## Export agent bundle into a target repo path or output directory
	@set -euo pipefail; \
	if [ -n "$(EXPORT_TARGET)" ] && [ -n "$(EXPORT_OUTPUT)" ]; then \
		echo ""; \
		echo "Set either EXPORT_TARGET or EXPORT_OUTPUT, not both."; \
		echo "Recommendation: prefer EXPORT_TARGET for populating another repo."; \
		echo ""; \
		exit 1; \
	fi; \
	if [ -z "$(EXPORT_TARGET)" ] && [ -z "$(EXPORT_OUTPUT)" ]; then \
		echo ""; \
		echo "Agent Bundle Export"; \
		echo "==================="; \
		echo ""; \
		echo "Most common:"; \
		echo "  make export EXPORT_TARGET=../my-repo EXPORT_OVERWRITE=true"; \
		echo ""; \
		echo "Preview first:"; \
		echo "  make export-dry-run EXPORT_TARGET=../my-repo"; \
		echo ""; \
		echo "Export with all bundled skills:"; \
		echo "  make export EXPORT_TARGET=../my-repo EXPORT_PROFILE=all EXPORT_OVERWRITE=true"; \
		echo ""; \
		echo "Advanced custom example:"; \
		echo "  make export \\"; \
		echo "    EXPORT_TARGET=../my-repo \\"; \
		echo "    EXPORT_PROJECT_NAME='Internal API' \\"; \
		echo "    EXPORT_SKILLS='federal-agents-config federal-pre-deployment-check' \\"; \
		echo "    EXPORT_INCLUDES='templates/risk-assessment.md checklists/pre-deployment.md' \\"; \
		echo "    EXPORT_OVERWRITE=true"; \
		echo ""; \
		echo "Options:"; \
		echo "  EXPORT_TARGET        path to the repo to populate (recommended)"; \
		echo "  EXPORT_OUTPUT        explicit output directory instead of a repo path"; \
		echo "  EXPORT_PROFILE       minimal | core | all (default: core)"; \
		echo "  EXPORT_PROJECT_NAME  project name for generated templates"; \
		echo "  EXPORT_SKILLS        space-separated list of skills"; \
		echo "  EXPORT_INCLUDES      space-separated list of template/checklist files"; \
		echo "  EXPORT_OVERWRITE     must be true to write files"; \
		echo ""; \
		echo "To see available skills:"; \
		echo "  bash scripts/export-agent-bundle.sh --list-skills"; \
		echo ""; \
		exit 0; \
	fi; \
	if [ "$(EXPORT_OVERWRITE)" != "true" ]; then \
		echo ""; \
		echo "Refusing to write without explicit confirmation."; \
		echo "Re-run with EXPORT_OVERWRITE=true"; \
		echo ""; \
		exit 1; \
	fi; \
	OUTPUT_PATH="$(EXPORT_OUTPUT)"; \
	if [ -n "$(EXPORT_TARGET)" ]; then \
		OUTPUT_PATH="$(EXPORT_TARGET)"; \
	fi; \
	if [ "$$OUTPUT_PATH" = "." ] || [ "$$OUTPUT_PATH" = "/" ]; then \
		echo ""; \
		echo "Refusing to export into '$$OUTPUT_PATH'."; \
		echo "Choose a specific repo path or output directory."; \
		echo ""; \
		exit 1; \
	fi; \
	echo "Exporting bundle to: $$OUTPUT_PATH"; \
	bash scripts/export-agent-bundle.sh \
		--output "$$OUTPUT_PATH" \
		--profile "$(EXPORT_PROFILE)" \
		--project-name "$(EXPORT_PROJECT_NAME)" \
		$(foreach skill,$(EXPORT_SKILLS),--skill $(skill)) \
		$(foreach include,$(EXPORT_INCLUDES),--include $(include)) \
		--overwrite

export-dry-run: ## Preview an export without writing files
	@set -euo pipefail; \
	if [ -n "$(EXPORT_TARGET)" ] && [ -n "$(EXPORT_OUTPUT)" ]; then \
		echo ""; \
		echo "Set either EXPORT_TARGET or EXPORT_OUTPUT, not both."; \
		echo ""; \
		exit 1; \
	fi; \
	if [ -z "$(EXPORT_TARGET)" ] && [ -z "$(EXPORT_OUTPUT)" ]; then \
		echo ""; \
		echo "Usage:"; \
		echo "  make export-dry-run EXPORT_TARGET=../my-repo"; \
		echo "  make export-dry-run EXPORT_OUTPUT=./dist/agent-bundle"; \
		echo ""; \
		exit 1; \
	fi; \
	OUTPUT_PATH="$(EXPORT_OUTPUT)"; \
	if [ -n "$(EXPORT_TARGET)" ]; then \
		OUTPUT_PATH="$(EXPORT_TARGET)"; \
	fi; \
	if [ "$$OUTPUT_PATH" = "." ] || [ "$$OUTPUT_PATH" = "/" ]; then \
		echo ""; \
		echo "Refusing to preview export into '$$OUTPUT_PATH'."; \
		echo "Choose a specific repo path or output directory."; \
		echo ""; \
		exit 1; \
	fi; \
	echo "Previewing export to: $$OUTPUT_PATH"; \
	bash scripts/export-agent-bundle.sh \
		--dry-run \
		--output "$$OUTPUT_PATH" \
		--profile "$(EXPORT_PROFILE)" \
		--project-name "$(EXPORT_PROJECT_NAME)" \
		$(foreach skill,$(EXPORT_SKILLS),--skill $(skill)) \
		$(foreach include,$(EXPORT_INCLUDES),--include $(include))

doctor: ## Check local tooling and script readiness
	@set -e; \
	echo "Tooling checks:"; \
	command -v bash >/dev/null 2>&1 && echo "  OK: bash ($$(bash --version | head -1))" || { echo "  MISSING: bash"; exit 1; }; \
	command -v python3 >/dev/null 2>&1 && echo "  OK: python3" || { echo "  MISSING: python3"; exit 1; }; \
	command -v pre-commit >/dev/null 2>&1 && echo "  OK: pre-commit" || echo "  MISSING: pre-commit"; \
	command -v shellcheck >/dev/null 2>&1 && echo "  OK: shellcheck" || echo "  MISSING: shellcheck"; \
	echo ""; \
	echo "Script checks:"; \
	test -x scripts/export-agent-bundle.sh && echo "  OK: scripts/export-agent-bundle.sh is executable" || echo "  WARN: scripts/export-agent-bundle.sh is not executable"; \
	test -x scripts/sync-generated-content.sh && echo "  OK: scripts/sync-generated-content.sh is executable" || echo "  WARN: scripts/sync-generated-content.sh is not executable"; \
	echo ""; \
	echo "Workflow readiness:"; \
	echo "  - local contribution: run 'make bootstrap', then 'make fix', then 'make verify'"; \
	echo "  - export bundles: run 'make export-dry-run EXPORT_TARGET=../my-repo' first"; \
	echo "  - maintainers: update CHANGELOG.md, then run 'make release-check' before tagging"

release-check:
	@set -euo pipefail; \
	echo "Running release readiness checks..."; \
	$(MAKE) verify; \
	LATEST_HEADING="$$(grep -E '^## \[[^]]+\]' CHANGELOG.md | head -1)"; \
	if echo "$$LATEST_HEADING" | grep -q '^\## \[Unreleased\]'; then \
		echo ""; \
		echo "CHANGELOG.md top entry is still [Unreleased]."; \
		echo "Convert it to a versioned entry before cutting a release."; \
		echo ""; \
		exit 1; \
	fi; \
	echo ""; \
	echo "Latest changelog entry: $$LATEST_HEADING"; \
	echo "Release readiness checks passed."

release-tag:
	@set -euo pipefail; \
	if [ -z "$(VERSION)" ]; then \
		echo "Usage: make release-tag VERSION=vX.Y.Z"; \
		exit 1; \
	fi; \
	if ! echo "$(VERSION)" | grep -Eq '^v[0-9]+\.[0-9]+\.[0-9]+$$'; then \
		echo "VERSION must look like vX.Y.Z"; \
		exit 1; \
	fi; \
	git diff --quiet || { echo "Working tree is not clean"; exit 1; }; \
	git diff --cached --quiet || { echo "Index has staged but uncommitted changes"; exit 1; }; \
	git rev-parse --verify "$(VERSION)" >/dev/null 2>&1 && { echo "Tag already exists: $(VERSION)"; exit 1; } || true; \
	LATEST_HEADING="$$(grep -E '^## \[[^]]+\]' CHANGELOG.md | head -1)"; \
	EXPECTED_HEADING="## [$(patsubst v%,%,$(VERSION))]"; \
	if [ "$$LATEST_HEADING" != "$$EXPECTED_HEADING" ] && ! printf '%s\n' "$$LATEST_HEADING" | grep -q "^$$EXPECTED_HEADING - "; then \
		echo "CHANGELOG.md top entry does not match $(VERSION)"; \
		echo "Expected heading starting with: $$EXPECTED_HEADING"; \
		echo "Actual heading: $$LATEST_HEADING"; \
		exit 1; \
	fi; \
	git tag -a "$(VERSION)" -m "Release $(VERSION)"; \
	echo "Created tag $(VERSION)"; \
	echo "Next step:"; \
	echo "  git push origin $(VERSION)"

clean: ## Remove local Python cache artifacts
	@find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@echo "Cleaned Python cache artifacts."
