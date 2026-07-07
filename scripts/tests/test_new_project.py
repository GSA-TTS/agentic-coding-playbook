"""Tests for new_project module — bootstrapping new projects from templates."""

from pathlib import Path

from playbook_validator.new_project import (
    DOWNSTREAM_SKILLS,
    EXCLUDED_SKILLS,
    FILES_TO_COPY,
    new_project,
)


class TestNewProject:
    """Test new project bootstrapping."""

    def _setup_playbook(self, tmp_path: Path) -> Path:
        """Create a minimal playbook directory with source files and skills."""
        playbook = tmp_path / "playbook"
        for src, _ in FILES_TO_COPY:
            f = playbook / src
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(f"# Content of {src}\n")
        # Create the full set of skills (allowlisted + excluded) so we can
        # verify the allowlist actually filters.
        for skill_name in (*DOWNSTREAM_SKILLS, *EXCLUDED_SKILLS):
            skill_dir = playbook / "skills" / skill_name
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(f"---\nname: {skill_name}\n---\n# {skill_name}\n")
        return playbook

    def test_copies_template_files(self, tmp_path: Path):
        playbook = self._setup_playbook(tmp_path)
        target = tmp_path / "new-project"

        copied, skipped = new_project(target, playbook)

        for _, dest in FILES_TO_COPY:
            assert (target / dest).exists()
        # skills/ and .gitignore are also produced.
        assert any("skills/" in c for c in copied)
        assert ".gitignore" in copied

    def test_copies_only_allowlisted_skills(self, tmp_path: Path):
        playbook = self._setup_playbook(tmp_path)
        target = tmp_path / "project"

        new_project(target, playbook)

        for skill_name in DOWNSTREAM_SKILLS:
            assert (target / "skills" / skill_name / "SKILL.md").exists()
        for skill_name in EXCLUDED_SKILLS:
            assert not (target / "skills" / skill_name).exists()

    def test_excluded_skills_reported_skipped(self, tmp_path: Path):
        playbook = self._setup_playbook(tmp_path)
        target = tmp_path / "project"

        _copied, skipped = new_project(target, playbook)

        for skill_name in EXCLUDED_SKILLS:
            assert any(skill_name in s and "excluded" in s for s in skipped)

    def test_writes_cache_gitignore(self, tmp_path: Path):
        playbook = self._setup_playbook(tmp_path)
        target = tmp_path / "project"

        new_project(target, playbook)

        gitignore = (target / ".gitignore").read_text()
        assert ".agents/cache/" in gitignore

    def test_appends_to_existing_gitignore(self, tmp_path: Path):
        playbook = self._setup_playbook(tmp_path)
        target = tmp_path / "project"
        target.mkdir()
        (target / ".gitignore").write_text("*.log\n")

        _copied, _skipped = new_project(target, playbook)

        gitignore = (target / ".gitignore").read_text()
        assert "*.log" in gitignore
        assert ".agents/cache/" in gitignore

    def test_probe_marked_executable(self, tmp_path: Path):
        playbook = self._setup_playbook(tmp_path)
        target = tmp_path / "project"

        new_project(target, playbook)

        assert (target / "scripts/ensure-contract.sh").stat().st_mode & 0o111
        assert (target / "scripts/ensure-contract.py").stat().st_mode & 0o111

    def test_no_agent_shims_created(self, tmp_path: Path):
        """AGENTS.md is the universal standard — no tool-specific shims needed."""
        playbook = self._setup_playbook(tmp_path)
        target = tmp_path / "project"

        new_project(target, playbook)

        assert not (target / ".github" / "copilot-instructions.md").exists()
        assert not (target / ".gemini").exists()
        assert not (target / ".aider.conf.yml").exists()
        assert not (target / ".cursorrules").exists()

    def test_creates_target_directory(self, tmp_path: Path):
        playbook = self._setup_playbook(tmp_path)
        target = tmp_path / "deep" / "nested" / "project"

        new_project(target, playbook)

        assert target.is_dir()

    def test_skips_existing_files(self, tmp_path: Path):
        playbook = self._setup_playbook(tmp_path)
        target = tmp_path / "existing"
        target.mkdir()
        (target / "AGENTS.md").write_text("# Existing AGENTS.md\n")

        copied, skipped = new_project(target, playbook)

        assert "AGENTS.md (already exists)" in skipped
        assert (target / "AGENTS.md").read_text() == "# Existing AGENTS.md\n"

    def test_skips_existing_skills(self, tmp_path: Path):
        playbook = self._setup_playbook(tmp_path)
        target = tmp_path / "project"
        (target / "skills").mkdir(parents=True)
        (target / "skills" / "existing.md").write_text("existing")

        copied, skipped = new_project(target, playbook)

        assert "skills/ (already exists)" in skipped

    def test_skips_missing_source(self, tmp_path: Path):
        playbook = tmp_path / "empty-playbook"
        playbook.mkdir()
        target = tmp_path / "project"

        copied, skipped = new_project(target, playbook)

        # Only the .gitignore (authored, not copied from a source) is produced.
        assert copied == [".gitignore"]
        source_skips = [s for s in skipped if "source not found" in s]
        assert len(source_skips) == len(FILES_TO_COPY) + 1  # +1 for skills/

    def test_idempotent_second_run(self, tmp_path: Path):
        playbook = self._setup_playbook(tmp_path)
        target = tmp_path / "project"

        copied1, _ = new_project(target, playbook)
        copied2, skipped2 = new_project(target, playbook)

        assert len(copied1) > 0
        assert len(copied2) == 0
        assert len(skipped2) > 0
