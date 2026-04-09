"""Tests for new_project module — bootstrapping new projects from templates."""

from pathlib import Path

from playbook_validator.new_project import FILES_TO_COPY, new_project


class TestNewProject:
    """Test new project bootstrapping."""

    def _setup_playbook(self, tmp_path: Path) -> Path:
        """Create a minimal playbook directory with source files and skills."""
        playbook = tmp_path / "playbook"
        for src, _ in FILES_TO_COPY:
            f = playbook / src
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(f"# Content of {src}\n")
        # Create a skill
        skill_dir = playbook / "skills" / "test-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("---\nname: test-skill\n---\n# Test\n")
        return playbook

    def test_copies_all_files_and_skills(self, tmp_path: Path):
        playbook = self._setup_playbook(tmp_path)
        target = tmp_path / "new-project"

        copied, skipped = new_project(target, playbook)

        # Template files + skills/
        assert len(copied) == len(FILES_TO_COPY) + 1
        for _, dest in FILES_TO_COPY:
            assert (target / dest).exists()

    def test_copies_skills_directory(self, tmp_path: Path):
        playbook = self._setup_playbook(tmp_path)
        target = tmp_path / "project"

        new_project(target, playbook)

        assert (target / "skills" / "test-skill" / "SKILL.md").exists()

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

        assert len(copied) == 0
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
