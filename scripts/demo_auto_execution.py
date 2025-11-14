#!/usr/bin/env python3
"""
Demo Script: Phase C Auto-Execution & Learning System

Demonstrates the complete auto-execution pipeline:
1. Intent detection (Phase B)
2. Auto-execute eligibility check
3. Safety validation
4. Skill execution or suggestions
5. Learning from usage patterns

Usage:
    uv run python scripts/demo_auto_execution.py
"""

import sys
import tempfile
from pathlib import Path
from typing import List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from superclaude.execution import ExecutionRouter
from superclaude.intent import SkillMatcher
from superclaude.intent.models import FileStructure, GitInfo, ProjectContext, TestingInfo


def print_section(title: str) -> None:
    """Print section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_subsection(title: str) -> None:
    """Print subsection header."""
    print(f"\n--- {title} ---")


def demo_basic_flow():
    """Demo 1: Basic auto-execution flow."""
    print_section("DEMO 1: Basic Auto-Execution Flow")

    # Setup
    skills_dir = Path(__file__).parent.parent / "skills"
    matcher = SkillMatcher(skills_dir)

    with tempfile.TemporaryDirectory() as tmpdir:
        learning_path = Path(tmpdir) / "learning.json"
        router = ExecutionRouter(matcher, learning_path=learning_path)

        # Create a safe project context (feature branch)
        context = ProjectContext(
            project_type="python",
            structure=FileStructure(
                root_dir=Path.cwd(),
                source_dirs=[Path("src")],
                test_dirs=[Path("tests")],
                config_files=[Path("pyproject.toml")],
            ),
            git_info=GitInfo(
                has_repo=True,
                current_branch="feature/demo",
                uncommitted_changes=2,
                recent_commits=5,
                status="M tests/test_demo.py",
            ),
            testing=TestingInfo(framework="pytest"),
        )

        # Test queries
        queries = [
            "troubleshoot login error",
            "implement user authentication",
            "check code quality",
            "xyz nonsense query",  # Should not match
        ]

        for query in queries:
            print_subsection(f'Query: "{query}"')

            result = router.execute_or_suggest(query, context=context, dry_run=True)

            print(f"⏱️  Execution time: {result.execution_time_ms:.2f}ms")

            if result.warning:
                print(f"⚠️  Warning: {result.warning}")

            if result.executed:
                print(f"✅ Auto-executed: {result.skill_used}")
                if result.arguments_used:
                    print(f"   Arguments: {result.arguments_used}")
                print(f"\n{result.output}")
            else:
                print("❌ Not auto-executed")
                if result.suggestions:
                    print(f"\n{result.suggestions}")


def demo_safety_validation():
    """Demo 2: Safety validation in action."""
    print_section("DEMO 2: Safety Validation")

    skills_dir = Path(__file__).parent.parent / "skills"
    matcher = SkillMatcher(skills_dir)

    with tempfile.TemporaryDirectory() as tmpdir:
        learning_path = Path(tmpdir) / "learning.json"
        router = ExecutionRouter(matcher, learning_path=learning_path)

        # Scenario 1: Safe context (feature branch)
        print_subsection("Scenario 1: Feature Branch (Safe)")

        safe_context = ProjectContext(
            project_type="python",
            structure=FileStructure(
                root_dir=Path.cwd(),
                source_dirs=[Path("src")],
                test_dirs=[Path("tests")],
                config_files=[],
            ),
            git_info=GitInfo(
                has_repo=True,
                current_branch="feature/cleanup",
                uncommitted_changes=0,
                recent_commits=3,
                status="",
            ),
            testing=TestingInfo(framework="pytest"),
        )

        result = router.execute_or_suggest(
            "cleanup old files", context=safe_context, dry_run=True
        )

        print(f"Result: {'✅ Executed' if result.executed else '❌ Blocked'}")
        if result.output:
            print(f"Output: {result.output[:200]}...")

        # Scenario 2: Unsafe context (main branch)
        print_subsection("Scenario 2: Main Branch (Blocked)")

        unsafe_context = ProjectContext(
            project_type="python",
            structure=FileStructure(
                root_dir=Path.cwd(),
                source_dirs=[Path("src")],
                test_dirs=[Path("tests")],
                config_files=[],
            ),
            git_info=GitInfo(
                has_repo=True,
                current_branch="main",  # Dangerous!
                uncommitted_changes=0,
                recent_commits=10,
                status="",
            ),
            testing=TestingInfo(framework="pytest"),
        )

        result = router.execute_or_suggest(
            "cleanup old logs", context=unsafe_context, dry_run=True
        )

        print(f"Result: {'✅ Executed' if result.executed else '❌ Blocked'}")
        if result.warning:
            print(f"Warning: {result.warning}")

        # Scenario 3: Many uncommitted changes
        print_subsection("Scenario 3: Many Uncommitted Changes (Warning)")

        messy_context = ProjectContext(
            project_type="python",
            structure=FileStructure(
                root_dir=Path.cwd(),
                source_dirs=[Path("src")],
                test_dirs=[Path("tests")],
                config_files=[],
            ),
            git_info=GitInfo(
                has_repo=True,
                current_branch="feature/work",
                uncommitted_changes=15,  # Many changes
                recent_commits=5,
                status="M file1.py\nM file2.py\n...",
            ),
            testing=TestingInfo(framework="pytest"),
        )

        result = router.execute_or_suggest(
            "build project", context=messy_context, dry_run=True
        )

        print(f"Result: {'✅ Executed' if result.executed else '❌ Blocked'}")
        if result.output and "warning" in result.output.lower():
            print("⚠️  Warnings present in output")


def demo_learning_system():
    """Demo 3: Learning system and confidence boosting."""
    print_section("DEMO 3: Learning System")

    skills_dir = Path(__file__).parent.parent / "skills"
    matcher = SkillMatcher(skills_dir)

    with tempfile.TemporaryDirectory() as tmpdir:
        learning_path = Path(tmpdir) / "learning.json"
        router = ExecutionRouter(matcher, learning_path=learning_path)

        context = ProjectContext(
            project_type="python",
            structure=FileStructure(
                root_dir=Path.cwd(),
                source_dirs=[Path("src")],
                test_dirs=[Path("tests")],
                config_files=[],
            ),
            git_info=GitInfo(
                has_repo=True,
                current_branch="feature/test",
                uncommitted_changes=2,
                recent_commits=5,
                status="M test.py",
            ),
            testing=TestingInfo(framework="pytest"),
        )

        # Execute same query multiple times
        query = "troubleshoot authentication error"

        print_subsection("First Execution")
        result1 = router.execute_or_suggest(query, context=context, dry_run=True)
        print(f"Executed: {result1.executed}")
        print(f"Skill: {result1.skill_used}")

        stats_before = router.get_learning_stats()
        print(f"\nLearning stats:")
        print(f"  Total executions: {stats_before['total_executions']}")
        print(f"  Skills tracked: {stats_before['total_skills_tracked']}")

        print_subsection("Second Execution (Learning Applied)")
        result2 = router.execute_or_suggest(query, context=context, dry_run=True)
        print(f"Executed: {result2.executed}")
        print(f"Skill: {result2.skill_used}")

        stats_after = router.get_learning_stats()
        print(f"\nUpdated learning stats:")
        print(f"  Total executions: {stats_after['total_executions']}")
        print(f"  Most used skill: {stats_after['most_used_skill']}")

        # Execute different queries to track patterns
        print_subsection("Executing Multiple Different Queries")
        queries = [
            "troubleshoot network timeout",
            "troubleshoot database connection",
            "implement oauth2 login",
            "build production artifacts",
        ]

        for q in queries:
            result = router.execute_or_suggest(q, context=context, dry_run=True)
            if result.executed:
                print(f"✅ {result.skill_used}: {q}")
            else:
                print(f"❌ No auto-exec: {q}")

        final_stats = router.get_learning_stats()
        print(f"\nFinal learning stats:")
        print(f"  Total executions: {final_stats['total_executions']}")
        print(f"  Total skills tracked: {final_stats['total_skills_tracked']}")
        print(f"  Most used skill: {final_stats['most_used_skill']}")


def demo_confidence_thresholds():
    """Demo 4: Confidence threshold decision making."""
    print_section("DEMO 4: Confidence Threshold Decision Making")

    skills_dir = Path(__file__).parent.parent / "skills"
    matcher = SkillMatcher(skills_dir)

    with tempfile.TemporaryDirectory() as tmpdir:
        learning_path = Path(tmpdir) / "learning.json"
        router = ExecutionRouter(matcher, learning_path=learning_path)

        context = ProjectContext(
            project_type="python",
            structure=FileStructure(
                root_dir=Path.cwd(),
                source_dirs=[Path("src")],
                test_dirs=[Path("tests")],
                config_files=[],
            ),
            git_info=GitInfo(
                has_repo=True,
                current_branch="feature/test",
                uncommitted_changes=0,
                recent_commits=5,
                status="",
            ),
            testing=TestingInfo(framework="pytest"),
        )

        # Test queries with varying clarity/confidence
        test_cases = [
            ("troubleshoot login bug", "High confidence - clear match"),
            ("maybe check something", "Low confidence - vague"),
            ("do stuff with git", "Low confidence - ambiguous"),
            ("implement user auth system", "Medium confidence"),
        ]

        for query, description in test_cases:
            print_subsection(f"{description}")
            print(f'Query: "{query}"')

            result = router.execute_or_suggest(query, context=context, dry_run=True)

            print(f"Auto-executed: {'✅ Yes' if result.executed else '❌ No'}")
            if result.executed:
                print(f"Skill: {result.skill_used}")
            else:
                print("Returned suggestions instead of executing")


def main():
    """Run all demos."""
    print("\n" + "█" * 80)
    print("  PHASE C AUTO-EXECUTION & LEARNING SYSTEM DEMO")
    print("  SuperClaude Framework v4.1.8")
    print("█" * 80)

    try:
        demo_basic_flow()
        demo_safety_validation()
        demo_learning_system()
        demo_confidence_thresholds()

        print("\n" + "█" * 80)
        print("  ✅ ALL DEMOS COMPLETED SUCCESSFULLY")
        print("█" * 80)
        print("\nKey Takeaways:")
        print("  1. ✅ Auto-execution works for high-confidence matches (≥85%)")
        print("  2. ✅ Safety validation prevents destructive ops on main/master")
        print("  3. ✅ Learning system tracks usage and improves recommendations")
        print("  4. ✅ Low-confidence queries return suggestions instead")
        print("\n")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
