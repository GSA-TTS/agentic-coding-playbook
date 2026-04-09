"""Tests for PROJECT_PLAN.md validation — TDD red/green."""

import textwrap

from playbook_validator.validate_project_plan import validate_project_plan


class TestValidateProjectPlan:
    """Test PROJECT_PLAN.md validation."""

    def test_valid_plan(self, tmp_path):
        plan = tmp_path / "PROJECT_PLAN.md"
        plan.write_text(
            textwrap.dedent("""\
            # Project Plan

            ## Project Identity

            | Field | Value |
            |---|---|
            | **Project Name** | Benefits Portal API |
            | **Repository Name** | benefits-portal-api |
            | **Organization/Agency** | HHS/CMS |

            ## Business Objective

            Build a REST API for benefits eligibility checks.

            ## Tech Stack

            | Component | Choice | Rationale |
            |---|---|---|
            | **Language** | Python 3.12 | Team expertise |
            | **Framework** | FastAPI | Performance |

            ## Compliance Level

            - [x] **FIPS Moderate** — Most federal systems

            ## Data Classification

            - [x] PII (Personally Identifiable Information)
        """)
        )
        errors, warnings = validate_project_plan(plan)
        assert errors == []

    def test_unfilled_placeholder(self, tmp_path):
        plan = tmp_path / "PROJECT_PLAN.md"
        plan.write_text(
            textwrap.dedent("""\
            # Project Plan

            ## Project Identity

            | Field | Value |
            |---|---|
            | **Project Name** | <!-- e.g., Benefits Portal API --> |

            ## Business Objective

            <!-- 2-3 sentences describing what this project does -->

            ## Tech Stack

            | Component | Choice | Rationale |
            |---|---|---|
            | **Language** | <!-- e.g., Python 3.12 --> | <!-- Why? --> |
        """)
        )
        errors, warnings = validate_project_plan(plan)
        assert len(errors) >= 2  # unfilled placeholders detected

    def test_missing_required_section(self, tmp_path):
        plan = tmp_path / "PROJECT_PLAN.md"
        plan.write_text(
            textwrap.dedent("""\
            # Project Plan

            ## Project Identity

            | Field | Value |
            |---|---|
            | **Project Name** | My Project |

            ## Business Objective

            Build something.
        """)
        )
        errors, warnings = validate_project_plan(plan)
        assert any("tech stack" in e.lower() for e in errors)

    def test_no_compliance_level_checked(self, tmp_path):
        plan = tmp_path / "PROJECT_PLAN.md"
        plan.write_text(
            textwrap.dedent("""\
            # Project Plan

            ## Project Identity

            | Field | Value |
            |---|---|
            | **Project Name** | My Project |

            ## Business Objective

            Build something.

            ## Tech Stack

            | Component | Choice | Rationale |
            |---|---|---|
            | **Language** | Python 3.12 | Team |

            ## Compliance Level

            - [ ] **FIPS Low**
            - [ ] **FIPS Moderate**
            - [ ] **FIPS High**
        """)
        )
        errors, warnings = validate_project_plan(plan)
        assert any("compliance" in e.lower() for e in errors)

    def test_empty_file(self, tmp_path):
        plan = tmp_path / "PROJECT_PLAN.md"
        plan.write_text("")
        errors, warnings = validate_project_plan(plan)
        assert len(errors) > 0

    def test_file_not_found(self, tmp_path):
        plan = tmp_path / "nonexistent.md"
        errors, warnings = validate_project_plan(plan)
        assert any("not found" in e.lower() for e in errors)

    def test_business_objective_is_placeholder(self, tmp_path):
        plan = tmp_path / "PROJECT_PLAN.md"
        plan.write_text(
            textwrap.dedent("""\
            # Project Plan

            ## Project Identity

            | Field | Value |
            |---|---|
            | **Project Name** | My App |

            ## Business Objective

            <!-- 2-3 sentences describing what this project does and why it matters. -->

            ## Tech Stack

            | Component | Choice | Rationale |
            |---|---|---|
            | **Language** | Go 1.22 | Performance |

            ## Compliance Level

            - [x] **FIPS Low**
        """)
        )
        errors, warnings = validate_project_plan(plan)
        assert any("business objective" in e.lower() for e in errors)

    def test_warnings_for_optional_missing_sections(self, tmp_path):
        plan = tmp_path / "PROJECT_PLAN.md"
        plan.write_text(
            textwrap.dedent("""\
            # Project Plan

            ## Project Identity

            | Field | Value |
            |---|---|
            | **Project Name** | My App |

            ## Business Objective

            A real objective here.

            ## Tech Stack

            | Component | Choice | Rationale |
            |---|---|---|
            | **Language** | Python 3.12 | Team expertise |

            ## Compliance Level

            - [x] **FIPS Moderate**
        """)
        )
        errors, warnings = validate_project_plan(plan)
        assert errors == []
        # Missing optional sections (Data Classification, Key Requirements, etc.) → warnings
        assert len(warnings) > 0
