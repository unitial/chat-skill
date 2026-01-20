"""Tests for skill loader."""

import pytest
from pathlib import Path
import tempfile
import os

from skill_chat.skills.loader import SkillLoader, Skill


@pytest.fixture
def temp_skills_dir():
    """Create a temporary skills directory with test skills."""
    with tempfile.TemporaryDirectory() as tmpdir:
        skills_path = Path(tmpdir)

        # Create test skill 1
        skill1_dir = skills_path / "test_skill_1"
        skill1_dir.mkdir()
        (skill1_dir / "SKILL.md").write_text("""# Test Skill One

This is a test skill for unit testing.

## When to Use

- Use for testing
- Use for validation

## Instructions

Follow these steps:
1. Step one
2. Step two
""")

        # Create test skill 2
        skill2_dir = skills_path / "test_skill_2"
        skill2_dir.mkdir()
        (skill2_dir / "SKILL.md").write_text("""# Another Test Skill

Second test skill without explicit sections.

Just some content here.
""")

        # Create directory without SKILL.md (should be ignored)
        (skills_path / "not_a_skill").mkdir()

        yield skills_path


def test_load_skills(temp_skills_dir):
    """Test loading skills from directory."""
    loader = SkillLoader(temp_skills_dir)
    skills = loader.load_skills()

    assert len(skills) == 2
    skill_names = [s.name for s in skills]
    assert "Test Skill One" in skill_names
    assert "Another Test Skill" in skill_names


def test_skill_extraction(temp_skills_dir):
    """Test skill metadata extraction."""
    loader = SkillLoader(temp_skills_dir)
    loader.load_skills()

    skill1 = loader.get_skill_by_name("Test Skill One")
    assert skill1 is not None
    assert "test skill" in skill1.description.lower()
    assert "testing" in skill1.triggers.lower() or "validation" in skill1.triggers.lower()


def test_get_skill_by_name(temp_skills_dir):
    """Test retrieving skill by name."""
    loader = SkillLoader(temp_skills_dir)
    loader.load_skills()

    # Test exact match
    skill = loader.get_skill_by_name("Test Skill One")
    assert skill is not None
    assert skill.name == "Test Skill One"

    # Test case insensitive
    skill = loader.get_skill_by_name("test skill one")
    assert skill is not None

    # Test non-existent skill
    skill = loader.get_skill_by_name("Non Existent")
    assert skill is None


def test_generate_index(temp_skills_dir):
    """Test generating skill index."""
    loader = SkillLoader(temp_skills_dir)
    loader.load_skills()

    index = loader.generate_index()

    assert "Test Skill One" in index
    assert "Another Test Skill" in index
    assert "Available Skills:" in index


def test_get_skill_names(temp_skills_dir):
    """Test getting list of skill names."""
    loader = SkillLoader(temp_skills_dir)
    loader.load_skills()

    names = loader.get_skill_names()
    assert len(names) == 2
    assert "Test Skill One" in names
    assert "Another Test Skill" in names


def test_empty_directory():
    """Test loading from empty directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        loader = SkillLoader(Path(tmpdir))
        skills = loader.load_skills()
        assert len(skills) == 0

        index = loader.generate_index()
        assert "No skills available" in index


def test_skill_to_index_entry(temp_skills_dir):
    """Test skill index entry generation."""
    loader = SkillLoader(temp_skills_dir)
    loader.load_skills()

    skill = loader.get_skill_by_name("Test Skill One")
    entry = skill.to_index_entry()

    assert "Test Skill One" in entry
    assert "**Test Skill One**" in entry  # Bold formatting
    lines = entry.split("\n")
    assert len(lines) <= 4  # Should be concise (2-3 lines max + title)


def test_nonexistent_directory():
    """Test handling of nonexistent directory."""
    loader = SkillLoader(Path("/nonexistent/path"))
    skills = loader.load_skills()
    assert len(skills) == 0


def test_skill_content_preserved(temp_skills_dir):
    """Test that full skill content is preserved."""
    loader = SkillLoader(temp_skills_dir)
    loader.load_skills()

    skill = loader.get_skill_by_name("Test Skill One")
    assert "## When to Use" in skill.content
    assert "## Instructions" in skill.content
    assert "Step one" in skill.content
