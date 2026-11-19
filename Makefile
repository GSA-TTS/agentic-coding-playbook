# Agentic AI Playbook — Developer Commands
# Run `make help` for available targets.

PYTHON := python3
PYTHONPATH_CMD := PYTHONPATH=scripts
VALIDATOR := $(PYTHONPATH_CMD) $(PYTHON) -m playbook_validator

.DEFAULT_GOAL := help

# ── Setup ──────────────────────────────────────────────────────────

.PHONY: install
install: ## Install all dependencies (use: pip or uv)
	$(PYTHON) -m pip install -e ".[dev]"

.PHONY: install-uv
install-uv: ## Install all dependencies using uv (faster)
	uv pip install -e ".[dev]"

.PHONY: setup
setup: install ## Install dependencies only (no hooks)
	@echo "✅ Dependencies installed."
	@echo "💡 Optional: Install pre-commit hooks with 'make install-hooks'"

.PHONY: install-hooks
install-hooks: ## [OPTIONAL] Install pre-commit hooks for contributors
	pre-commit install
	@echo "✅ Pre-commit hooks installed. They will run automatically on git commit."

# ── Testing ────────────────────────────────────────────────────────

.PHONY: test
test: ## Run all Python tests
	$(PYTHONPATH_CMD) $(PYTHON) -m pytest scripts/tests/ -v

.PHONY: test-quick
test-quick: ## Run tests without verbose output
	$(PYTHONPATH_CMD) $(PYTHON) -m pytest scripts/tests/ -q

# ── Linting & Formatting ──────────────────────────────────────────

LINTER_DIR := .github/linters
LINTER_DEPS := $(LINTER_DIR)/node_modules/.package-lock.json

# Single locked install shared by `lint` and `test-linters`. Both depend on this
# one target, so `make -j` runs it once before either consumer starts instead of
# letting two `npm ci` runs delete and repopulate node_modules concurrently.
$(LINTER_DEPS): $(LINTER_DIR)/package.json $(LINTER_DIR)/package-lock.json
	npm ci --prefix $(LINTER_DIR) --ignore-scripts --no-audit --no-fund --prefer-offline

.PHONY: lint
lint: $(LINTER_DEPS) ## Run ruff linter + markdown linter
	ruff check scripts/
	node $(LINTER_DIR)/run-markdownlint.mjs

.PHONY: test-linters
test-linters: $(LINTER_DEPS) ## Run the Markdown lint adapter tests
	node --test $(LINTER_DIR)/tests/*.test.mjs

.PHONY: format
format: ## Format Python code with ruff
	ruff format scripts/

.PHONY: format-check
format-check: ## Check Python formatting (no changes)
	ruff format --check scripts/

# ── Validation ─────────────────────────────────────────────────────

.PHONY: validate-docs
validate-docs: ## Validate document frontmatter
	$(VALIDATOR) validate-docs --root .

.PHONY: validate-skills
validate-skills: ## Validate skill directories
	$(VALIDATOR) validate-skills --root .

.PHONY: validate-landscape
validate-landscape: ## Validate federal AI landscape registry
	$(VALIDATOR) validate-landscape --path data/federal-ai-landscape.yaml

.PHONY: validate-plan
validate-plan: ## Validate a PROJECT_PLAN.md file
	$(VALIDATOR) validate-plan --path $(or $(PLAN),PROJECT_PLAN.md)

.PHONY: validate-risk-assessment
validate-risk-assessment: ## Validate risk assessment worksheet
	$(VALIDATOR) validate-risk-assessment --path $(or $(RISK_PATH),templates/risk-assessment.md)

.PHONY: validate-adrs
validate-adrs: ## Validate ADR decision records
	$(VALIDATOR) validate-adrs --dir $(or $(ADR_DIR),docs/decisions)

.PHONY: audit-repo
audit-repo: ## Audit repository compliance baseline
	$(VALIDATOR) audit-repo --path .

.PHONY: validate
validate: validate-docs validate-skills validate-landscape ## Run all validators

# ── Generation ─────────────────────────────────────────────────────

.PHONY: generate
generate: ## Regenerate INDEX.yaml and README skills table
	$(VALIDATOR) generate-index --root .

.PHONY: generate-check
generate-check: ## Verify INDEX.yaml is up to date (CI mode)
	$(VALIDATOR) generate-index --check --root .

.PHONY: refresh-oscal
refresh-oscal: ## Refresh derived NIST 800-53 control-name map from NIST OSCAL (maintainer, network)
	PYTHONPATH=scripts python3 scripts/refresh_oscal_control_names.py --root .

# ── Project Bootstrap ──────────────────────────────────────────────

.PHONY: new-project
new-project: ## Bootstrap a new project (usage: make new-project DIR=/path/to/new-repo)
	@if [ -z "$(DIR)" ]; then echo "Usage: make new-project DIR=/path/to/new-repo"; exit 1; fi
	$(VALIDATOR) new-project --dir $(DIR) --playbook-root .

# ── Tools ──────────────────────────────────────────────────────────

.PHONY: doctor
doctor: ## Check environment readiness for AI agents
	$(VALIDATOR) doctor --root .

.PHONY: doctor-json
doctor-json: ## Environment doctor with JSON output
	$(VALIDATOR) doctor --json --root .

.PHONY: pre-deploy
pre-deploy: ## Run pre-deployment security checks
	$(VALIDATOR) pre-deploy --path .

.PHONY: audit
audit: ## Run SCA vulnerability scan on installed packages
	pip-audit

# ── CI Reproduction ───────────────────────────────────────────────

.PHONY: ci
ci: lint test-linters format-check test validate generate-check audit ## Reproduce full CI locally

.PHONY: check
check: ci ## Alias for ci

# ── Cleanup ────────────────────────────────────────────────────────

.PHONY: clean
clean: ## Remove build artifacts and caches
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

# ── Help ───────────────────────────────────────────────────────────

.PHONY: help
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
