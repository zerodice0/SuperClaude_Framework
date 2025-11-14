"""
ArgumentInferrer - Infers skill arguments from multiple sources.

The inferrer extracts arguments from user queries, project context,
git history, and learning data.
"""

import re
from typing import Any, Dict, Optional

from .models import ArgumentSchema, InferSource, ProjectContext, Skill


class ArgumentInferrer:
    """Infers skill arguments from query, context, and learning data."""

    def infer(
        self, query: str, skill: Skill, context: ProjectContext
    ) -> Dict[str, Any]:
        """
        Infer arguments using multiple sources.

        Priority order:
        1. user_query: Direct extraction from query text
        2. project_context: Analyze project structure
        3. git_history: Parse recent commits
        4. learning: Use historical patterns
        5. default: Use skill default value

        Args:
            query: User's natural language query
            skill: Skill to infer arguments for
            context: Project context information

        Returns:
            Dict mapping argument name to inferred value
        """
        arguments: Dict[str, Any] = {}

        for arg in skill.arguments:
            value = None

            # Try each inference source in order
            if InferSource.USER_QUERY.value in arg.infer_from:
                value = self._extract_from_query(query, arg, skill)
                if value is not None:
                    arguments[arg.name] = value
                    continue

            if InferSource.PROJECT_CONTEXT.value in arg.infer_from:
                value = self._infer_from_context(context, arg)
                if value is not None:
                    arguments[arg.name] = value
                    continue

            if InferSource.GIT_HISTORY.value in arg.infer_from:
                value = self._infer_from_git(context.git_info, arg)
                if value is not None:
                    arguments[arg.name] = value
                    continue

            if InferSource.LEARNING.value in arg.infer_from:
                value = self._infer_from_learning(skill.name, arg)
                if value is not None:
                    arguments[arg.name] = value
                    continue

            # Use default if available and no value inferred
            if arg.default is not None:
                arguments[arg.name] = arg.default

        return arguments

    def _extract_from_query(
        self, query: str, arg: ArgumentSchema, skill: Skill
    ) -> Optional[Any]:
        """
        Extract argument value from user query.

        Strategies:
        1. Check if already extracted by pattern matching
        2. Look for --arg-name value format
        3. Extract from primary pattern {param} placeholders
        4. For bool args, check for presence of keywords
        """
        query_lower = query.lower()

        # Strategy 1: Flag-style arguments (--arg-name value)
        flag_pattern = rf"--{arg.name}(?:\s+([^\s-]+))?"
        match = re.search(flag_pattern, query)
        if match:
            if arg.type == "bool":
                return True
            elif match.group(1):
                return self._cast_value(match.group(1), arg.type)

        # Strategy 2: Boolean detection by keywords
        if arg.type == "bool":
            # Check for positive keywords
            positive_keywords = ["yes", "true", "enable", "on"]
            if any(kw in query_lower for kw in positive_keywords):
                return True

            # Check for negative keywords
            negative_keywords = ["no", "false", "disable", "off"]
            if any(kw in query_lower for kw in negative_keywords):
                return False

        # Strategy 3: Extract from primary patterns
        for primary in skill.intents.primary:
            if f"{{{arg.name}}}" in primary:
                # Convert primary to regex
                pattern = self._primary_to_regex(primary, arg.name)
                match = re.search(pattern, query, re.IGNORECASE)
                if match and arg.name in match.groupdict():
                    value = match.group(arg.name)
                    return self._cast_value(value, arg.type)

        # Strategy 4: Enum value detection
        if arg.type == "enum" and arg.values:
            for enum_value in arg.values:
                if enum_value.lower() in query_lower:
                    return enum_value

        return None

    def _infer_from_context(
        self, context: ProjectContext, arg: ArgumentSchema
    ) -> Optional[Any]:
        """
        Infer argument value from project context.

        Common inferences:
        - target: Current directory or main source dir
        - type: Based on project type
        - framework: Based on dependencies
        """
        # Target file/directory inference
        if arg.name in ["target", "path", "file", "directory"]:
            if context.structure.source_dirs:
                return str(context.structure.source_dirs[0])
            return str(context.structure.root_dir)

        # Type inference
        if arg.name == "type" and arg.type == "enum" and arg.values:
            if context.project_type in arg.values:
                return context.project_type

        # Framework inference
        if arg.name == "framework":
            if context.testing.framework:
                return context.testing.framework

        # Language/platform inference
        if arg.name in ["language", "platform"]:
            type_map = {
                "python": "python",
                "typescript": "typescript",
                "javascript": "javascript",
                "mixed": "typescript",  # Default to TS for mixed
            }
            return type_map.get(context.project_type)

        return None

    def _infer_from_git(self, git_info, arg: ArgumentSchema) -> Optional[Any]:
        """
        Infer argument value from git history.

        Common inferences:
        - branch: Current branch
        - changes: Recent commits or uncommitted changes
        """
        if not git_info.has_repo:
            return None

        # Branch inference
        if arg.name == "branch":
            return git_info.current_branch

        # Changes detection (boolean)
        if arg.name in ["changes", "uncommitted", "dirty"] and arg.type == "bool":
            return git_info.uncommitted_changes > 0

        # Commit message inference
        if arg.name in ["message", "commit"] and git_info.recent_commits:
            return git_info.recent_commits[0].get("message", "")

        return None

    def _infer_from_learning(
        self, skill_name: str, arg: ArgumentSchema
    ) -> Optional[Any]:
        """
        Infer argument value from learning data.

        TODO: Implement with Serena MCP integration
        This would look up commonly used argument values for this skill.
        """
        # Stub for now - will be implemented with Serena MCP
        return None

    def _primary_to_regex(self, primary: str, param_name: str) -> str:
        """
        Convert primary pattern to regex for specific parameter.

        Example:
            primary = "troubleshoot {issue}"
            param_name = "issue"
            result = "troubleshoot (?P<issue>.+)"
        """
        # Escape special regex characters except {}
        escaped = re.escape(primary)

        # Replace \{param_name\} with named group
        pattern = re.sub(
            rf"\\{{{param_name}\\}}", rf"(?P<{param_name}>.+)", escaped
        )

        # Replace other \{param\} with non-capturing groups
        pattern = re.sub(r"\\{(\w+)\\}", r"(?:.+)", pattern)

        # Make spaces flexible
        pattern = pattern.replace(r"\ ", r"\s+")

        return pattern

    def _cast_value(self, value: str, arg_type: str) -> Any:
        """Cast string value to argument type."""
        value = value.strip()

        if arg_type == "string":
            return value

        if arg_type == "int":
            try:
                return int(value)
            except ValueError:
                return value

        if arg_type == "bool":
            return value.lower() in ["true", "yes", "1", "on", "enable"]

        if arg_type == "path":
            return value

        if arg_type == "enum":
            return value

        return value
