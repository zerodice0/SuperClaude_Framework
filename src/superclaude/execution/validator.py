"""
SafetyValidator - Validates safety of skill execution.

Performs pre-execution checks to ensure safe automatic execution:
- No destructive operations on main branch
- Required dependencies available
- Sufficient disk space
- No file conflicts
- Custom safety checks from skill config
"""

import shutil
from pathlib import Path
from typing import List, Optional

from ..intent.models import ProjectContext, Skill, SkillMatch
from .models import SafetyCheck, SafetyResult


class SafetyValidator:
    """Validates safety of skill execution."""

    # Destructive operation indicators
    DESTRUCTIVE_KEYWORDS = [
        'delete', 'remove', 'cleanup', 'reset', 'drop',
        'destroy', 'clear', 'purge', 'wipe'
    ]

    # File modification indicators
    FILE_MOD_KEYWORDS = [
        'write', 'create', 'update', 'modify', 'edit',
        'generate', 'build', 'compile'
    ]

    def validate(
        self,
        match: SkillMatch,
        context: ProjectContext
    ) -> SafetyResult:
        """
        Run safety checks before execution.

        Args:
            match: Skill match to validate
            context: Project context information

        Returns:
            SafetyResult with safety decision and warnings
        """
        warnings = []
        checks = []

        # Check 1: Destructive operations on main branch
        if self._is_destructive(match.skill):
            checks.append("destructive_operation")

            if self._on_main_branch(context):
                return SafetyResult(
                    safe=False,
                    warning="Destructive operation blocked on main/master branch. "
                           "Switch to a feature branch first.",
                    checks_performed=checks
                )

        # Check 2: Dependencies
        if match.skill.mcp_servers:
            checks.append("dependencies")
            missing = self._check_mcp_dependencies(match.skill, context)
            if missing:
                warnings.append(
                    f"MCP servers may not be available: {', '.join(missing)}"
                )

        # Check 3: Disk space (for file operations)
        if self._may_modify_files(match.skill):
            checks.append("disk_space")
            if not self._check_disk_space(minimum_mb=100):
                return SafetyResult(
                    safe=False,
                    warning="Insufficient disk space. At least 100MB required.",
                    checks_performed=checks
                )

        # Check 4: File conflicts (for git/build operations)
        if context.git_info.has_repo and self._may_modify_files(match.skill):
            checks.append("file_conflicts")
            if context.git_info.uncommitted_changes > 10:
                warnings.append(
                    f"Many uncommitted changes ({context.git_info.uncommitted_changes}). "
                    "Consider committing or stashing first."
                )

        # Check 5: Custom safety checks from skill config
        for check_data in match.skill.auto_trigger.safety_checks:
            check = SafetyCheck.from_dict(check_data) if isinstance(check_data, dict) else None
            if check:
                checks.append(f"custom:{check.check_type}")
                result = self._run_custom_check(check, match, context)
                if not result.safe:
                    return result

        return SafetyResult(
            safe=True,
            warnings=warnings,
            checks_performed=checks
        )

    def _is_destructive(self, skill: Skill) -> bool:
        """Check if skill performs destructive operations."""
        skill_text = f"{skill.name} {skill.description}".lower()
        return any(kw in skill_text for kw in self.DESTRUCTIVE_KEYWORDS)

    def _may_modify_files(self, skill: Skill) -> bool:
        """Check if skill may modify files."""
        skill_text = f"{skill.name} {skill.description}".lower()
        return any(kw in skill_text for kw in self.FILE_MOD_KEYWORDS)

    def _on_main_branch(self, context: ProjectContext) -> bool:
        """Check if currently on main/master branch."""
        if not context.git_info.has_repo:
            return False

        main_branches = ['main', 'master']
        return context.git_info.current_branch in main_branches

    def _check_mcp_dependencies(
        self, skill: Skill, context: ProjectContext
    ) -> List[str]:
        """
        Check if required MCP servers are available.

        Returns:
            List of missing MCP server names
        """
        # TODO: Actual MCP server availability check
        # For now, assume all are available
        missing = []

        # Check for critical dependencies
        if 'serena' in skill.mcp_servers:
            # Serena is critical for persistence
            # Would check if MCP connection is active
            pass

        return missing

    def _check_disk_space(self, minimum_mb: int = 100) -> bool:
        """
        Check available disk space.

        Args:
            minimum_mb: Minimum required space in megabytes

        Returns:
            True if sufficient space available
        """
        try:
            stat = shutil.disk_usage(Path.cwd())
            available_mb = stat.free / (1024 * 1024)
            return available_mb >= minimum_mb
        except Exception:
            # If we can't check, assume sufficient space
            return True

    def _run_custom_check(
        self, check: SafetyCheck, match: SkillMatch, context: ProjectContext
    ) -> SafetyResult:
        """
        Run custom safety check from skill config.

        Supported checks:
        - git_branch: Validate current branch
        - disk_space: Check minimum disk space
        - no_conflicts: Check for file conflicts
        """
        if check.check_type == 'git_branch':
            return self._check_git_branch(check, context)

        elif check.check_type == 'disk_space':
            return self._check_disk_space_custom(check)

        elif check.check_type == 'no_conflicts':
            return self._check_no_conflicts(check, context)

        # Unknown check type - pass by default
        return SafetyResult(safe=True)

    def _check_git_branch(
        self, check: SafetyCheck, context: ProjectContext
    ) -> SafetyResult:
        """
        Validate current git branch against allowed patterns.

        Config:
            allowed: List of allowed branch patterns (e.g., ['feature/*', 'bugfix/*'])
        """
        if not context.git_info.has_repo:
            return SafetyResult(safe=True)

        allowed = check.params.get('allowed', [])
        current = context.git_info.current_branch

        if not allowed:
            return SafetyResult(safe=True)

        # Check if current branch matches any pattern
        for pattern in allowed:
            if self._matches_pattern(current, pattern):
                return SafetyResult(safe=True)

        message = check.message or f"Branch '{current}' not in allowed list: {allowed}"
        return SafetyResult(safe=False, warning=message)

    def _check_disk_space_custom(self, check: SafetyCheck) -> SafetyResult:
        """
        Check disk space against minimum requirement.

        Config:
            minimum_mb: Minimum required space in megabytes
        """
        minimum = check.params.get('minimum_mb', 100)

        if self._check_disk_space(minimum_mb=minimum):
            return SafetyResult(safe=True)

        message = check.message or f"Requires at least {minimum}MB free space"
        return SafetyResult(safe=False, warning=message)

    def _check_no_conflicts(
        self, check: SafetyCheck, context: ProjectContext
    ) -> SafetyResult:
        """
        Check for file conflicts.

        Config:
            files: List of files to check for modifications
        """
        if not context.git_info.has_repo:
            return SafetyResult(safe=True)

        if context.git_info.uncommitted_changes == 0:
            return SafetyResult(safe=True)

        files = check.params.get('files', [])
        if not files:
            return SafetyResult(safe=True)

        # Check if any of the specified files are modified
        status_lines = context.git_info.status.split('\n')
        modified_files = [
            line.split()[-1] for line in status_lines
            if line.strip() and not line.startswith('??')
        ]

        conflicts = [f for f in files if f in modified_files]
        if conflicts:
            message = check.message or f"Modified files conflict: {', '.join(conflicts)}"
            return SafetyResult(safe=False, warning=message)

        return SafetyResult(safe=True)

    def _matches_pattern(self, text: str, pattern: str) -> bool:
        """
        Simple pattern matching with wildcard support.

        Supports:
        - Exact match: "main"
        - Prefix match: "feature/*"
        - Suffix match: "*/dev"
        """
        if '*' not in pattern:
            return text == pattern

        if pattern.endswith('/*'):
            prefix = pattern[:-2]
            return text.startswith(prefix)

        if pattern.startswith('*/'):
            suffix = pattern[2:]
            return text.endswith(suffix)

        return False
