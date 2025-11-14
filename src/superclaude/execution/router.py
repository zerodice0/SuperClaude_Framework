"""
ExecutionRouter - Routes high-confidence matches to automatic execution.

The router orchestrates the auto-execution pipeline:
1. Match query to skills
2. Check auto-execute eligibility
3. Run safety validations
4. Execute skill or return suggestions
5. Track execution and update learning
"""

import time
from pathlib import Path
from typing import Optional

from ..intent.matcher import SkillMatcher
from ..intent.models import ProjectContext, SkillMatch
from .learner import LearningSystem
from .models import ExecutionResult
from .validator import SafetyValidator


class ExecutionRouter:
    """Routes high-confidence matches to automatic execution."""

    def __init__(
        self,
        matcher: SkillMatcher,
        learning_path: Optional[Path] = None
    ):
        """
        Initialize execution router.

        Args:
            matcher: SkillMatcher instance for intent detection
            learning_path: Optional path for learning data storage
        """
        self.matcher = matcher
        self.validator = SafetyValidator()
        self.learner = LearningSystem(storage_path=learning_path)

    def execute_or_suggest(
        self,
        query: str,
        context: Optional[ProjectContext] = None,
        dry_run: bool = False
    ) -> ExecutionResult:
        """
        Execute high-confidence matches automatically or suggest alternatives.

        Flow:
        1. Match query to skills (using SkillMatcher)
        2. Check if top match is auto-executable
        3. Run safety validations
        4. Execute skill or return suggestions
        5. Track execution and update learning data

        Args:
            query: User's natural language query
            context: Optional project context
            dry_run: If True, don't actually execute (for testing)

        Returns:
            ExecutionResult with execution status and output
        """
        start_time = time.perf_counter()

        # Step 1: Match query to skills
        match_result = self.matcher.match(query, context)

        if not match_result.matches:
            return ExecutionResult(
                query=query,
                executed=False,
                suggestions="❌ No matching skills found for your query.",
                execution_time_ms=(time.perf_counter() - start_time) * 1000
            )

        top_match = match_result.top_match
        context = match_result.context

        # Step 2: Check auto-execute eligibility
        if not self._should_auto_execute(top_match):
            return ExecutionResult(
                query=query,
                executed=False,
                suggestions=match_result.format_suggestions(),
                execution_time_ms=(time.perf_counter() - start_time) * 1000
            )

        # Step 3: Run safety validations
        safety_result = self.validator.validate(top_match, context)

        if not safety_result.safe:
            return ExecutionResult(
                query=query,
                executed=False,
                suggestions=match_result.format_suggestions(),
                warning=safety_result.warning,
                execution_time_ms=(time.perf_counter() - start_time) * 1000
            )

        # Step 4: Execute skill (or simulate in dry run)
        if dry_run:
            exec_result = ExecutionResult(
                query=query,
                executed=False,  # Not actually executed in dry run
                success=True,
                output=f"[DRY RUN] Would execute: {top_match.format_command()}",
                skill_used=top_match.skill.name,
                arguments_used=top_match.arguments,
                execution_time_ms=(time.perf_counter() - start_time) * 1000
            )
        else:
            exec_result = self._execute_skill(
                top_match,
                start_time=start_time
            )

        # Step 5: Track execution and update learning
        if exec_result.executed:
            self.learner.track_execution(query, top_match, exec_result)

        # Add safety warnings if any
        if safety_result.has_warnings():
            if exec_result.output:
                exec_result.output += "\n\n" + safety_result.format_warnings()
            else:
                exec_result.output = safety_result.format_warnings()

        return exec_result

    def _should_auto_execute(self, match: SkillMatch) -> bool:
        """
        Determine if match should auto-execute.

        Criteria:
        1. Auto-trigger enabled in skill config
        2. Confidence ≥ threshold (default 0.85)
        3. All required arguments inferred
        4. No confirmation required

        Args:
            match: SkillMatch to check

        Returns:
            True if should auto-execute
        """
        # Check 1: Auto-trigger enabled
        if not match.skill.auto_trigger.enabled:
            return False

        # Check 2: Confidence threshold
        if match.confidence < match.skill.auto_trigger.confidence_threshold:
            return False

        # Check 3: Required arguments
        required_args = [arg for arg in match.skill.arguments if arg.required]
        if not all(arg.name in match.arguments for arg in required_args):
            return False

        # Check 4: Confirmation requirement
        if match.skill.auto_trigger.confirm_before_execution:
            return False

        return True

    def _execute_skill(
        self,
        match: SkillMatch,
        start_time: float
    ) -> ExecutionResult:
        """
        Execute skill (simulation for now).

        In production, this would:
        1. Load full skill content
        2. Execute skill logic
        3. Capture output
        4. Return result

        For now, we simulate successful execution.

        Args:
            match: SkillMatch to execute
            start_time: Execution start time for timing

        Returns:
            ExecutionResult with execution status
        """
        # Simulate execution
        output = self._simulate_skill_execution(match)

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        return ExecutionResult(
            query="",  # Will be set by caller
            executed=True,
            success=True,
            output=output,
            skill_used=match.skill.name,
            arguments_used=match.arguments,
            execution_time_ms=elapsed_ms
        )

    def _simulate_skill_execution(self, match: SkillMatch) -> str:
        """
        Simulate skill execution (placeholder).

        In production, this would execute the actual skill.

        Args:
            match: SkillMatch to execute

        Returns:
            Simulated output string
        """
        skill = match.skill
        args = match.arguments

        output_lines = [
            f"Executing: {skill.display_name}",
            f"Description: {skill.description}",
            ""
        ]

        if args:
            output_lines.append("Arguments:")
            for arg_name, arg_value in args.items():
                output_lines.append(f"  - {arg_name}: {arg_value}")
            output_lines.append("")

        if skill.mcp_servers:
            output_lines.append(f"MCP Servers: {', '.join(skill.mcp_servers)}")

        if skill.personas:
            output_lines.append(f"Personas: {', '.join(skill.personas)}")

        output_lines.append("")
        output_lines.append("✅ Execution completed successfully")

        return "\n".join(output_lines)

    def get_learning_stats(self):
        """Get learning system statistics."""
        return self.learner.get_stats()

    def reset_learning(self) -> None:
        """Reset all learning data."""
        self.learner.reset()
