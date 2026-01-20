"""Skill loader for scanning and parsing SKILL.md files."""

import os
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass
import re


@dataclass
class Skill:
    """Represents a parsed skill."""

    name: str
    description: str
    triggers: str
    full_path: Path
    content: str

    def to_index_entry(self) -> str:
        """Generate a concise index entry (2-3 lines max)."""
        lines = [f"- **{self.name}**"]
        if self.description:
            lines.append(f"  {self.description}")
        if self.triggers:
            lines.append(f"  Use when: {self.triggers}")
        return "\n".join(lines)


class SkillLoader:
    """Loads and parses skills from a directory."""

    def __init__(self, skills_dir: Optional[Path] = None):
        """Initialize the skill loader.

        Args:
            skills_dir: Path to skills directory. If None, tries default locations.
        """
        self.skills_dir = self._resolve_skills_dir(skills_dir)
        self.skills: List[Skill] = []

    def _resolve_skills_dir(self, skills_dir: Optional[Path]) -> Path:
        """Resolve skills directory, trying default locations if not provided."""
        if skills_dir:
            return Path(skills_dir)

        # Try default locations
        candidates = [
            Path("./.claude/skills"),
            Path.home() / ".claude/skills",
            Path("./demo_skills"),
        ]

        for candidate in candidates:
            if candidate.exists() and candidate.is_dir():
                return candidate

        # Return first candidate as fallback
        return candidates[0]

    def load_skills(self) -> List[Skill]:
        """Scan directory and load all skills."""
        if not self.skills_dir.exists():
            print(f"Warning: Skills directory does not exist: {self.skills_dir}")
            return []

        self.skills = []

        # Walk through directory looking for SKILL.md files
        for root, dirs, files in os.walk(self.skills_dir):
            if "SKILL.md" in files:
                skill_path = Path(root) / "SKILL.md"
                try:
                    skill = self._parse_skill(skill_path)
                    if skill:
                        self.skills.append(skill)
                except Exception as e:
                    print(f"Warning: Failed to parse skill at {skill_path}: {e}")

        return self.skills

    def _parse_skill(self, skill_path: Path) -> Optional[Skill]:
        """Parse a SKILL.md file and extract metadata."""
        try:
            content = skill_path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"Error reading {skill_path}: {e}")
            return None

        # Extract name (from title or directory name)
        name = self._extract_name(content, skill_path)

        # Extract description (first few lines)
        description = self._extract_description(content)

        # Extract triggers/when-to-use
        triggers = self._extract_triggers(content)

        return Skill(
            name=name,
            description=description,
            triggers=triggers,
            full_path=skill_path,
            content=content
        )

    def _extract_name(self, content: str, skill_path: Path) -> str:
        """Extract skill name from title or use directory name."""
        # Try to find markdown title
        lines = content.split("\n")
        for line in lines[:5]:  # Check first 5 lines
            if line.startswith("# "):
                return line[2:].strip()

        # Fallback to directory name
        return skill_path.parent.name.replace("_", " ").replace("-", " ").title()

    def _extract_description(self, content: str, max_lines: int = 2) -> str:
        """Extract description from first few lines of content."""
        lines = content.split("\n")
        desc_lines = []

        started = False
        for line in lines:
            line = line.strip()

            # Skip title lines and empty lines at start
            if not started:
                if line.startswith("#") or not line:
                    continue
                started = True

            # Stop at next section header
            if started and line.startswith("#"):
                break

            if line:
                desc_lines.append(line)
                if len(desc_lines) >= max_lines:
                    break

        description = " ".join(desc_lines)
        # Truncate if too long
        if len(description) > 200:
            description = description[:197] + "..."

        return description

    def _extract_triggers(self, content: str) -> str:
        """Extract trigger conditions from skill content."""
        # Look for sections like "When to use", "适用场景", "Triggers", etc.
        patterns = [
            r"#+\s*(?:when to use|适用场景|triggers?|use cases?)\s*\n(.*?)(?=\n#|\Z)",
            r"#+\s*(?:scenario|场景)\s*\n(.*?)(?=\n#|\Z)",
        ]

        content_lower = content.lower()

        for pattern in patterns:
            match = re.search(pattern, content_lower, re.IGNORECASE | re.DOTALL)
            if match:
                trigger_text = match.group(1).strip()
                # Take first sentence or up to 150 chars
                lines = [l.strip() for l in trigger_text.split("\n") if l.strip()]
                if lines:
                    result = lines[0]
                    if len(result) > 150:
                        result = result[:147] + "..."
                    # Remove markdown formatting
                    result = re.sub(r'[*_`\[\]]', '', result)
                    return result

        return ""

    def generate_index(self) -> str:
        """Generate a concise skill index for the router."""
        if not self.skills:
            return "No skills available."

        index_lines = ["Available Skills:"]
        for skill in self.skills:
            index_lines.append(skill.to_index_entry())

        return "\n".join(index_lines)

    def get_skill_by_name(self, name: str) -> Optional[Skill]:
        """Get a skill by its name (case-insensitive)."""
        name_lower = name.lower()
        for skill in self.skills:
            if skill.name.lower() == name_lower:
                return skill
        return None

    def get_skill_names(self) -> List[str]:
        """Get list of all skill names."""
        return [skill.name for skill in self.skills]
