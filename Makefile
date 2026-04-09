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

.PHONY: install-hooks
install-hooks: ## Install pre-commit hooks
	pre-commit install

.PHONY: setup
setup: install install-hooks ## Full setup: install deps + hooks

# ── Testing ────────────────────────────────────────────────────────

.PHONY: test
test: ## Run all Python tests
	$(PYTHONPATH_CMD) $(PYTHON) -m pytest scripts/tests/ -v

.PHONY: test-quick
test-quick: ## Run tests without verbose output
	$(PYTHONPATH_CMD) $(PYTHON) -m pytest scripts/tests/ -q

# ── Linting & Formatting ──────────────────────────────────────────

.PHONY: lint
lint: ## Run ruff linter + markdown linter
	ruff check scripts/
	npx markdownlint-cli2

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
	$(VALIDATOR) validate-adrs --dir $(or $(ADR_DIR),docs/adr)

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

.PHONY: lock
lock: ## Regenerate dependency lock files (requirements.lock + requirements-dev.lock)
	pip-compile pyproject.toml -o requirements.lock --generate-hashes --strip-extras -q
	pip-compile pyproject.toml --extra dev -o requirements-dev.lock --generate-hashes --strip-extras -q

.PHONY: audit
audit: ## Run SCA vulnerability scan on locked dependencies
	pip-audit -r requirements.lock

# ── CI Reproduction ───────────────────────────────────────────────

.PHONY: ci
ci: lint format-check test validate generate-check audit ## Reproduce full CI locally

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
