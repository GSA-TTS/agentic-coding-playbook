"""Tests for pre-deployment security checks module."""

import json
from pathlib import Path

from playbook_validator.output import ResultCollector
from playbook_validator.pre_deploy_checks import (
    check_ci_security,
    check_crypto_keys,
    check_dependency_pinning,
    check_empty_catches,
    check_lock_file,
    check_secrets,
    check_sql_injection,
    check_unsafe_apis,
    run_pre_deploy_checks,
)

# ── 1. Secret pattern detection ─────────────────────────────────────────


class TestCheckSecrets:
    """2.1: Detect hardcoded secrets in source files."""

    def test_pass_clean_repo(self, tmp_path):
        (tmp_path / "app.py").write_text("x = 42\n")
        rc = ResultCollector()
        check_secrets(tmp_path, rc)
        assert rc.checks_passed == 1
        assert rc.checks_failed == 0

    def test_fail_password_in_py(self, tmp_path):
        (tmp_path / "config.py").write_text('password = "super_secret_password123"\n')
        rc = ResultCollector()
        check_secrets(tmp_path, rc)
        assert rc.checks_failed == 1
        assert "secret" in rc._results[0].note.lower() or "1 file" in rc._results[0].note

    def test_fail_api_key_in_yaml(self, tmp_path):
        (tmp_path / "config.yaml").write_text('api_key: "abcdefghijklmnop"\n')
        rc = ResultCollector()
        check_secrets(tmp_path, rc)
        assert rc.checks_failed == 1

    def test_skip_excluded_dirs(self, tmp_path):
        nm = tmp_path / "node_modules" / "pkg"
        nm.mkdir(parents=True)
        (nm / "index.js").write_text('token = "leaked_secret_value_1234"\n')
        rc = ResultCollector()
        check_secrets(tmp_path, rc)
        assert rc.checks_passed == 1


# ── 2. SQL injection pattern detection ───────────────────────────────────


class TestCheckSqlInjection:
    """3.2: Detect string-concatenated SQL."""

    def test_pass_parameterized(self, tmp_path):
        (tmp_path / "db.py").write_text('cursor.execute("SELECT * FROM t WHERE id = ?", (uid,))\n')
        rc = ResultCollector()
        check_sql_injection(tmp_path, rc)
        assert rc.checks_passed == 1

    def test_fail_format_string(self, tmp_path):
        (tmp_path / "db.py").write_text('cursor.execute("SELECT * FROM t WHERE id = %s" % user_input)\n')
        rc = ResultCollector()
        check_sql_injection(tmp_path, rc)
        assert rc.checks_failed == 1

    def test_fail_dot_format(self, tmp_path):
        (tmp_path / "db.py").write_text('cursor.execute("SELECT * FROM t WHERE id = {}".format(uid))\n')
        rc = ResultCollector()
        check_sql_injection(tmp_path, rc)
        assert rc.checks_failed == 1


# ── 3. Unsafe eval / innerHTML detection ─────────────────────────────────


class TestCheckUnsafeApis:
    """3.5: Detect eval/innerHTML/exec."""

    def test_pass_no_unsafe(self, tmp_path):
        (tmp_path / "app.js").write_text("console.log('hello');\n")
        rc = ResultCollector()
        check_unsafe_apis(tmp_path, rc)
        assert rc.checks_passed == 1

    def test_fail_eval(self, tmp_path):
        (tmp_path / "app.js").write_text("const x = eval(userInput);\n")
        rc = ResultCollector()
        check_unsafe_apis(tmp_path, rc)
        assert rc.checks_failed == 1

    def test_fail_innerhtml(self, tmp_path):
        (tmp_path / "app.js").write_text("el.innerHTML = data;\n")
        rc = ResultCollector()
        check_unsafe_apis(tmp_path, rc)
        assert rc.checks_failed == 1

    def test_fail_os_system(self, tmp_path):
        (tmp_path / "run.py").write_text('os.system("rm -rf /")\n')
        rc = ResultCollector()
        check_unsafe_apis(tmp_path, rc)
        assert rc.checks_failed == 1


# ── 4. Dependency pinning validation ─────────────────────────────────────


class TestCheckDependencyPinning:
    """5.1: Dependencies pinned to exact versions."""

    def test_pass_pinned_package_json(self, tmp_path):
        (tmp_path / "package.json").write_text('{"dependencies": {"express": "4.18.2"}}')
        rc = ResultCollector()
        check_dependency_pinning(tmp_path, rc)
        assert rc.checks_passed == 1

    def test_fail_caret_range(self, tmp_path):
        (tmp_path / "package.json").write_text('{"dependencies": {"express": "^4.18.2"}}')
        rc = ResultCollector()
        check_dependency_pinning(tmp_path, rc)
        assert rc.checks_failed == 1

    def test_fail_tilde_range(self, tmp_path):
        (tmp_path / "package.json").write_text('{"dependencies": {"express": "~4.18.2"}}')
        rc = ResultCollector()
        check_dependency_pinning(tmp_path, rc)
        assert rc.checks_failed == 1

    def test_pass_pinned_requirements(self, tmp_path):
        (tmp_path / "requirements.txt").write_text("flask==2.3.0\nrequests==2.31.0\n")
        rc = ResultCollector()
        check_dependency_pinning(tmp_path, rc)
        assert rc.checks_passed == 1

    def test_fail_unpinned_requirements(self, tmp_path):
        (tmp_path / "requirements.txt").write_text("flask>=2.3.0\nrequests\n")
        rc = ResultCollector()
        check_dependency_pinning(tmp_path, rc)
        assert rc.checks_failed == 1

    def test_pass_pinned_pyproject(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text('[project]\ndependencies = [\n    "PyYAML==6.0.3",\n]\n')
        rc = ResultCollector()
        check_dependency_pinning(tmp_path, rc)
        assert rc.checks_passed == 1

    def test_fail_unpinned_pyproject(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text('[project]\ndependencies = [\n    "PyYAML>=6.0",\n]\n')
        rc = ResultCollector()
        check_dependency_pinning(tmp_path, rc)
        assert rc.checks_failed == 1

    def test_pass_pinned_pyproject_with_name_and_tables(self, tmp_path):
        """Regression (#239): a fully-pinned pyproject with a project name and
        tool tables must PASS. The old whole-file regex matched the bare quoted
        name (e.g. "playbook-validator") and any quoted table key/rule code, so
        this always failed and no pyproject could ever pass."""
        (tmp_path / "pyproject.toml").write_text(
            "[project]\n"
            'name = "playbook-validator"\n'
            "dependencies = [\n"
            '    "PyYAML==6.0.3",\n'
            '    "feedparser==6.0.14",\n'
            "]\n\n"
            "[project.optional-dependencies]\n"
            "dev = [\n"
            '    "pytest==9.1.1",\n'
            '    "ruff==0.16.2",\n'
            "]\n\n"
            "[tool.ruff.lint]\n"
            'select = ["E", "W", "F", "S101"]\n'
        )
        rc = ResultCollector()
        check_dependency_pinning(tmp_path, rc)
        assert rc.checks_passed == 1
        assert rc.checks_failed == 0

    def test_fail_pyproject_caret_tilde_and_bare(self, tmp_path):
        for spec in ('"PyYAML^6.0"', '"PyYAML~=6.0"', '"PyYAML"'):
            (tmp_path / "pyproject.toml").write_text(f'[project]\nname = "x"\ndependencies = [\n    {spec},\n]\n')
            rc = ResultCollector()
            check_dependency_pinning(tmp_path, rc)
            assert rc.checks_failed == 1, f"{spec} should be flagged unpinned"

    def test_pass_pyproject_extras_marker_and_git(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text(
            '[project]\nname = "x"\ndependencies = [\n'
            '    "uvicorn[standard]==0.30.0",\n'
            "    \"tomli==2.0.1; python_version < '3.11'\",\n"
            '    "mylib @ git+https://example.com/mylib.git@v1.0",\n'
            "]\n"
        )
        rc = ResultCollector()
        check_dependency_pinning(tmp_path, rc)
        assert rc.checks_passed == 1
        assert rc.checks_failed == 0

    def test_pass_pyproject_commented_floating(self, tmp_path):
        """A floating spec that appears only in a comment must not fail."""
        (tmp_path / "pyproject.toml").write_text(
            '[project]\nname = "x"\ndependencies = [\n'
            '    # "flask>=2.0" was rejected; pinned below\n'
            '    "PyYAML==6.0.3",\n'
            "]\n"
        )
        rc = ResultCollector()
        check_dependency_pinning(tmp_path, rc)
        assert rc.checks_passed == 1

    def test_fail_pyproject_optional_floating(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text(
            '[project]\nname = "x"\n[project.optional-dependencies]\ndev = [\n    "pytest>=9",\n]\n'
        )
        rc = ResultCollector()
        check_dependency_pinning(tmp_path, rc)
        assert rc.checks_failed == 1

    def test_real_repo_pyproject_passes(self):
        """The playbook's OWN fully-pinned pyproject must pass (#239 false-fail)."""
        repo_root = Path(__file__).resolve().parents[2]
        rc = ResultCollector()
        check_dependency_pinning(repo_root, rc)
        assert rc.checks_failed == 0, "the repo's own pinned pyproject must not be flagged"

    def test_pass_no_manifest(self, tmp_path):
        rc = ResultCollector()
        check_dependency_pinning(tmp_path, rc)
        assert rc.checks_passed == 1  # nothing to check -> pass with note


# ── 5. Lock file check ──────────────────────────────────────────────────


class TestCheckLockFile:
    """5.2: Lock file committed."""

    def test_pass_with_package_lock(self, tmp_path):
        (tmp_path / "package-lock.json").write_text("{}")
        rc = ResultCollector()
        check_lock_file(tmp_path, rc)
        assert rc.checks_passed == 1

    def test_pass_with_poetry_lock(self, tmp_path):
        (tmp_path / "poetry.lock").write_text("")
        rc = ResultCollector()
        check_lock_file(tmp_path, rc)
        assert rc.checks_passed == 1

    def test_fail_no_lock(self, tmp_path):
        rc = ResultCollector()
        check_lock_file(tmp_path, rc)
        assert rc.checks_failed == 1

    def test_fail_untracked_lock_in_git_repo(self, tmp_path):
        # #259: present-but-untracked lock fails (git repo present).
        import subprocess

        subprocess.run(["git", "-C", str(tmp_path), "init", "-q"], check=True)
        (tmp_path / "uv.lock").write_text("version = 1\n")
        rc = ResultCollector()
        check_lock_file(tmp_path, rc)
        assert rc.checks_failed == 1

    def test_pass_tracked_lock_in_git_repo(self, tmp_path):
        import subprocess

        subprocess.run(["git", "-C", str(tmp_path), "init", "-q"], check=True)
        (tmp_path / "uv.lock").write_text("version = 1\n")
        subprocess.run(["git", "-C", str(tmp_path), "add", "-f", "uv.lock"], check=True)
        rc = ResultCollector()
        check_lock_file(tmp_path, rc)
        assert rc.checks_passed == 1


# ── 6. Empty catch block detection ───────────────────────────────────────


class TestCheckEmptyCatches:
    """6.1: No empty catch/except blocks."""

    def test_pass_no_empty_catch(self, tmp_path):
        (tmp_path / "app.js").write_text("try { x(); } catch(e) { log(e); }\n")
        rc = ResultCollector()
        check_empty_catches(tmp_path, rc)
        assert rc.checks_passed == 1

    def test_fail_empty_js_catch(self, tmp_path):
        (tmp_path / "app.js").write_text("try { x(); } catch(e) {}\n")
        rc = ResultCollector()
        check_empty_catches(tmp_path, rc)
        assert rc.checks_failed == 1

    def test_fail_python_bare_except_pass(self, tmp_path):
        (tmp_path / "app.py").write_text("try:\n    x()\nexcept:\n    pass\n")
        rc = ResultCollector()
        check_empty_catches(tmp_path, rc)
        assert rc.checks_failed == 1


# ── 7. CI SAST/SCA presence ─────────────────────────────────────────────


class TestCheckCiSecurity:
    """9.4 + 9.5: SAST and SCA scanning in CI."""

    def test_pass_both_tools(self, tmp_path):
        wf_dir = tmp_path / ".github" / "workflows"
        wf_dir.mkdir(parents=True)
        (wf_dir / "security.yml").write_text(
            "jobs:\n  scan:\n    steps:\n      - run: semgrep\n      - run: npm audit\n"
        )
        rc = ResultCollector()
        check_ci_security(tmp_path, rc)
        assert rc.checks_passed == 2
        assert rc.checks_failed == 0

    def test_fail_no_ci(self, tmp_path):
        rc = ResultCollector()
        check_ci_security(tmp_path, rc)
        assert rc.checks_failed == 2  # both SAST and SCA fail

    def test_partial_sast_only(self, tmp_path):
        wf_dir = tmp_path / ".github" / "workflows"
        wf_dir.mkdir(parents=True)
        (wf_dir / "ci.yml").write_text("steps:\n  - run: bandit\n")
        rc = ResultCollector()
        check_ci_security(tmp_path, rc)
        assert rc.checks_passed == 1  # SAST
        assert rc.checks_failed == 1  # SCA missing

    def test_gitlab_ci(self, tmp_path):
        (tmp_path / ".gitlab-ci.yml").write_text("security:\n  script: trivy fs .\n  script: codeql\n")
        rc = ResultCollector()
        check_ci_security(tmp_path, rc)
        assert rc.checks_passed == 2


# ── 8. ResultCollector output format ─────────────────────────────────────


class TestResultCollectorFormat:
    """Verify JSON output structure from ResultCollector."""

    def test_json_structure(self, tmp_path):
        rc = run_pre_deploy_checks(str(tmp_path))
        output = json.loads(rc.to_json())
        assert "status" in output
        assert "checks_passed" in output
        assert "checks_failed" in output
        assert "results" in output
        assert isinstance(output["results"], list)
        assert "warnings" in output
        assert "errors" in output

    def test_each_result_has_required_keys(self, tmp_path):
        rc = run_pre_deploy_checks(str(tmp_path))
        output = json.loads(rc.to_json())
        for r in output["results"]:
            assert "file" in r
            assert "check" in r
            assert "pass" in r

    def test_text_format(self, tmp_path):
        rc = run_pre_deploy_checks(str(tmp_path))
        text = rc.format_text()
        assert "Passed:" in text
        assert "Failed:" in text


# ── 9. Clean repo (all pass) ────────────────────────────────────────────


class TestCleanRepo:
    """A repo with no violations should pass all checks."""

    def test_all_pass(self, tmp_path):
        # Clean source file
        (tmp_path / "main.py").write_text("print('hello world')\n")
        # Pinned deps
        (tmp_path / "requirements.txt").write_text("flask==2.3.0\n")
        # Lock file
        (tmp_path / "poetry.lock").write_text("[metadata]\n")
        # CI with both SAST + SCA
        wf = tmp_path / ".github" / "workflows"
        wf.mkdir(parents=True)
        (wf / "ci.yml").write_text("jobs:\n  scan:\n    steps:\n      - run: bandit src/\n      - run: pip-audit\n")

        rc = run_pre_deploy_checks(str(tmp_path))
        assert rc.checks_failed == 0
        assert rc.status == "success"
        assert rc.exit_code == 0


# ── 10. Repo with known violations ──────────────────────────────────────


class TestKnownViolations:
    """A repo with multiple violations should flag them all."""

    def test_multiple_failures(self, tmp_path):
        # Secret
        (tmp_path / "config.py").write_text('api_key = "my_secret_api_key_12345678"\n')
        # SQL injection
        (tmp_path / "db.py").write_text('cursor.execute("SELECT * FROM t WHERE id = %s" % uid)\n')
        # Unsafe eval
        (tmp_path / "run.js").write_text("eval(userInput);\n")
        # Floating deps
        (tmp_path / "package.json").write_text('{"dependencies": {"express": "^4.18.2"}}')
        # No lock file
        # Empty catch
        (tmp_path / "handler.js").write_text("try { run(); } catch(e) {}\n")
        # No CI

        rc = run_pre_deploy_checks(str(tmp_path))
        assert rc.checks_failed >= 6  # secrets, sql, eval, pinning, lock, catch, SAST, SCA
        assert rc.status != "success"
        assert rc.exit_code == 1

    def test_invalid_path(self):
        rc = run_pre_deploy_checks("/nonexistent/path/xyzzy")
        assert len(rc._errors) == 1
        assert "does not exist" in rc._errors[0]


# ── 11. Crypto key detection ────────────────────────────────────────────


class TestCheckCryptoKeys:
    """7.6: No hardcoded crypto keys."""

    def test_pass_no_keys(self, tmp_path):
        (tmp_path / "app.py").write_text("x = 1\n")
        rc = ResultCollector()
        check_crypto_keys(tmp_path, rc)
        assert rc.checks_passed == 1

    def test_fail_pem_block(self, tmp_path):
        (tmp_path / "key.py").write_text('key = "-----BEGIN RSA PRIVATE KEY-----"\n')
        rc = ResultCollector()
        check_crypto_keys(tmp_path, rc)
        assert rc.checks_failed == 1
