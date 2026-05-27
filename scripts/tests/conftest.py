"""Shared pytest fixtures for playbook_validator tests.

This module consolidates common test fixtures to reduce code duplication
across test files. See issue #60 for the refactoring rationale.

Fixtures provided:
- result_collector: Fresh ResultCollector instance
- git_repo: Temporary directory with git initialized
- write_md: Factory for markdown files with frontmatter
- write_file: Factory for files with dedented content
- write_yaml: Factory for YAML files
- make_skill: Factory for skill directories with SKILL.md
- github_workflow: Factory for GitHub Actions workflow files
"""

import os
import subprocess
import textwrap
from contextlib import contextmanager
from unittest.mock import patch

import pytest
import yaml
from playbook_validator.output import ResultCollector

# ── Core fixtures ──────────────────────────────────────────────────────────


@pytest.fixture
def result_collector():
    """Provide a fresh ResultCollector for each test.

    Usage:
        def test_something(self, result_collector):
            check_function(path, result_collector)
            assert result_collector.checks_passed == 1
    """
    return ResultCollector()


@pytest.fixture
def git_repo(tmp_path):
    """Initialize and return a temporary git repository.

    Usage:
        def test_git_feature(self, git_repo):
            # git_repo is a Path to a directory with .git initialized
            (git_repo / "file.txt").write_text("content")
    """
    subprocess.run(
        ["git", "init", str(tmp_path)],
        check=True,
        capture_output=True,
    )
    # Configure git user for commits (required for some tests)
    subprocess.run(
        ["git", "-C", str(tmp_path), "config", "user.email", "test@example.com"],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "-C", str(tmp_path), "config", "user.name", "Test User"],
        check=True,
        capture_output=True,
    )
    return tmp_path


# ── File writer factories ──────────────────────────────────────────────────


@pytest.fixture
def write_md(tmp_path):
    """Factory to write markdown files with YAML frontmatter.

    Usage:
        def test_markdown(self, write_md):
            path = write_md("docs/test.md", title="My Doc", tier=2)
            assert path.exists()
    """

    def _write(
        filename,
        *,
        tier=1,
        title="Test",
        description="A test document",
        status="canonical",
        content="# Content\n",
        nist_controls=None,
        frameworks=None,
        **extra_fm,
    ):
        path = tmp_path / filename
        path.parent.mkdir(parents=True, exist_ok=True)

        fm_lines = [
            "---",
            f'title: "{title}"',
            f'description: "{description}"',
            f"status: {status}",
            f"tier: {tier}",
        ]
        if nist_controls:
            fm_lines.append(f"nist_controls: {nist_controls}")
        if frameworks:
            fm_lines.append(f"frameworks: {frameworks}")
        for k, v in extra_fm.items():
            if isinstance(v, str):
                fm_lines.append(f'{k}: "{v}"')
            else:
                fm_lines.append(f"{k}: {v}")
        fm_lines.append("---")

        path.write_text("\n".join(fm_lines) + "\n" + content)
        return path

    return _write


@pytest.fixture
def write_file(tmp_path):
    """Factory to write files with dedented content.

    Usage:
        def test_file(self, write_file):
            path = write_file("config.yaml", '''
                key: value
                nested:
                  item: 1
            ''')
    """

    def _write(filename, content):
        path = tmp_path / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(content).lstrip())
        return path

    return _write


@pytest.fixture
def write_yaml(tmp_path):
    """Factory to write YAML files from Python dicts.

    Usage:
        def test_yaml(self, write_yaml):
            path = write_yaml("data.yaml", {"key": "value", "items": [1, 2, 3]})
    """

    def _write(filename, data):
        path = tmp_path / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.dump(data, default_flow_style=False, sort_keys=False))
        return path

    return _write


# ── Skill directory factory ────────────────────────────────────────────────


@pytest.fixture
def make_skill(tmp_path):
    """Factory to create skill directories with SKILL.md.

    Usage:
        def test_skill(self, make_skill):
            skill_dir = make_skill("my-skill", description="Does something")
            assert (skill_dir / "SKILL.md").exists()
    """

    def _make(
        name,
        *,
        description="A test skill",
        status="canonical",
        tier=2,
        frontmatter=None,
        body="# Skill content\n",
        scripts=None,
        lines=None,
    ):
        skill_dir = tmp_path / "skills" / name
        skill_dir.mkdir(parents=True, exist_ok=True)

        if frontmatter is None:
            frontmatter = {
                "name": name,
                "description": description,
                "status": status,
                "tier": tier,
            }

        fm_text = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)
        content = f"---\n{fm_text}---\n{body}"

        # Pad to minimum line count if specified
        if lines is not None:
            current = content.count("\n")
            if current < lines:
                content += "\n" * (lines - current)

        (skill_dir / "SKILL.md").write_text(content)

        # Create script files if specified
        if scripts:
            scripts_dir = skill_dir / "scripts"
            scripts_dir.mkdir()
            for script_name in scripts:
                (scripts_dir / script_name).write_text("#!/bin/bash\necho 'stub'\n")

        return skill_dir

    return _make


# ── GitHub workflow factory ────────────────────────────────────────────────


@pytest.fixture
def github_workflow(tmp_path):
    """Factory to create GitHub Actions workflow files.

    Usage:
        def test_ci(self, github_workflow):
            wf = github_workflow("ci.yml", "name: CI\\non: push")
            assert wf.exists()
    """

    def _create(name="ci.yml", content="name: CI\non: push\n"):
        wf_dir = tmp_path / ".github" / "workflows"
        wf_dir.mkdir(parents=True, exist_ok=True)
        wf_file = wf_dir / name
        wf_file.write_text(content)
        return wf_file

    return _create


# ── Environment mocking ────────────────────────────────────────────────────


@pytest.fixture
def mock_env():
    """Context manager factory for temporarily patching environment variables.

    Usage:
        def test_with_env(self, mock_env):
            with mock_env({"API_KEY": "test123"}):
                result = function_that_reads_env()
            # Environment restored after context

        def test_clean_env(self, mock_env):
            with mock_env({}, clear=True):
                # All env vars cleared
                pass
    """

    @contextmanager
    def _mock(env_vars, clear=False):
        with patch.dict(os.environ, env_vars, clear=clear):
            yield

    return _mock


# ── ADR factory ────────────────────────────────────────────────────────────


@pytest.fixture
def make_adr(tmp_path):
    """Factory to create ADR (Architecture Decision Record) files.

    Usage:
        def test_adr(self, make_adr):
            adr = make_adr("0001-use-postgres.md", status="accepted")
    """

    def _make(
        filename,
        *,
        title="Test ADR",
        status="proposed",
        date="2026-01-01",
        deciders=None,
        content=None,
    ):
        adr_dir = tmp_path / "docs" / "adr"
        adr_dir.mkdir(parents=True, exist_ok=True)

        if content is None:
            content = textwrap.dedent(f"""
                ---
                title: "{title}"
                status: {status}
                date: {date}
                deciders: {deciders or "team"}
                ---

                # {title}

                ## Context

                Test context.

                ## Decision

                Test decision.

                ## Consequences

                Test consequences.
            """).lstrip()

        path = adr_dir / filename
        path.write_text(content)
        return path

    return _make
