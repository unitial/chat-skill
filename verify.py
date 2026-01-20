#!/usr/bin/env python3
"""
Verification script for Chat Skills Runtime
Checks that all components are properly installed and configured
"""

import sys
import os
from pathlib import Path


def check_python_version():
    """Check Python version."""
    major, minor = sys.version_info[:2]
    if major < 3 or (major == 3 and minor < 10):
        print(f"❌ Python 3.10+ required, found {major}.{minor}")
        return False
    print(f"✓ Python version: {major}.{minor}")
    return True


def check_project_structure():
    """Check project structure."""
    required_files = [
        "chat_skills/__init__.py",
        "chat_skills/cli.py",
        "chat_skills/skills/loader.py",
        "chat_skills/router/agent.py",
        "chat_skills/chat/agent.py",
        "demo_skills/pdf_summary/SKILL.md",
        "demo_skills/paper_review/SKILL.md",
        "demo_skills/course_outline/SKILL.md",
        "tests/test_loader.py",
        "tests/test_router.py",
        "README.md",
        "pyproject.toml",
        "requirements.txt",
    ]

    missing = []
    for file in required_files:
        if not Path(file).exists():
            missing.append(file)

    if missing:
        print(f"❌ Missing files: {', '.join(missing)}")
        return False

    print(f"✓ Project structure: {len(required_files)} files found")
    return True


def check_dependencies():
    """Check if dependencies can be imported."""
    required_modules = [
        ("pydantic", "Pydantic"),
        ("click", "Click"),
        ("rich", "Rich"),
    ]

    missing = []
    for module_name, display_name in required_modules:
        try:
            __import__(module_name)
        except ImportError:
            missing.append(display_name)

    if missing:
        print(f"⚠ Missing dependencies: {', '.join(missing)}")
        print("  Run: pip install -r requirements.txt")
        return False

    print(f"✓ Dependencies: {len(required_modules)} packages installed")
    return True


def check_agentscope():
    """Check AgentScope installation."""
    try:
        import agentscope
        print(f"✓ AgentScope installed")
        return True
    except ImportError:
        print("⚠ AgentScope not installed")
        print("  Run: pip install agentscope")
        return False


def check_skills():
    """Check demo skills."""
    from chat_skills.skills.loader import SkillLoader

    loader = SkillLoader(Path("demo_skills"))
    skills = loader.load_skills()

    if len(skills) < 3:
        print(f"❌ Expected 3 demo skills, found {len(skills)}")
        return False

    print(f"✓ Demo skills: {len(skills)} loaded")
    for skill in skills:
        print(f"  - {skill.name}")
    return True


def check_api_key():
    """Check API key configuration."""
    if os.getenv("OPENAI_API_KEY"):
        print("✓ API key: Set (OPENAI_API_KEY)")
        return True
    else:
        print("⚠ API key: Not set (OPENAI_API_KEY)")
        print("  Set with: export OPENAI_API_KEY='your-key'")
        return False


def main():
    """Run all checks."""
    print("=== Skill-aware Chat Runtime - Verification ===\n")

    checks = [
        ("Python Version", check_python_version),
        ("Project Structure", check_project_structure),
        ("Dependencies", check_dependencies),
        ("AgentScope", check_agentscope),
        ("Demo Skills", check_skills),
        ("API Configuration", check_api_key),
    ]

    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append(result)
        except Exception as e:
            print(f"❌ {name}: Error - {e}")
            results.append(False)
        print()

    # Summary
    passed = sum(results)
    total = len(results)

    print("=" * 50)
    print(f"Verification: {passed}/{total} checks passed")
    print("=" * 50)

    if passed == total:
        print("\n✓ All checks passed! You're ready to use chat-skills.")
        print("\nTry it out:")
        print("  chat-skills --skills-dir ./demo_skills --show-routing")
        return 0
    elif passed >= total - 1:
        print("\n⚠ Most checks passed. Review warnings above.")
        print("  You can still use the system, but some features may not work.")
        return 0
    else:
        print("\n❌ Several checks failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
