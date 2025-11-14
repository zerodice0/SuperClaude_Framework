"""
Data models for auto-execution system.

These models represent execution results, safety validation, and learning data.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ExecutionResult:
    """Result of skill execution or suggestion display."""

    query: str
    executed: bool
    success: bool = False
    output: str = ""
    suggestions: str = ""
    warning: Optional[str] = None
    execution_time_ms: float = 0.0
    skill_used: Optional[str] = None
    arguments_used: Dict[str, Any] = field(default_factory=dict)

    def format_result(self) -> str:
        """Format execution result for display."""
        if self.warning:
            return f"⚠️  {self.warning}\n\n{self.suggestions}"

        if not self.executed:
            return self.suggestions

        if self.success:
            header = f"✅ Executed: /sc:{self.skill_used}"
            if self.arguments_used:
                args_str = " ".join(
                    f"--{k} {v}" for k, v in self.arguments_used.items()
                )
                header += f" {args_str}"

            return f"{header}\n\n{self.output}"
        else:
            return f"❌ Execution failed: {self.output}"


@dataclass
class SafetyResult:
    """Result of safety validation."""

    safe: bool
    warning: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    checks_performed: List[str] = field(default_factory=list)

    def has_warnings(self) -> bool:
        """Check if there are any warnings."""
        return bool(self.warning or self.warnings)

    def format_warnings(self) -> str:
        """Format warnings for display."""
        if not self.has_warnings():
            return ""

        lines = []
        if self.warning:
            lines.append(f"⚠️  {self.warning}")

        for w in self.warnings:
            lines.append(f"⚠️  {w}")

        return "\n".join(lines)


@dataclass
class SafetyCheck:
    """Configuration for a custom safety check."""

    check_type: str  # 'git_branch', 'disk_space', 'no_conflicts', etc.
    params: Dict[str, Any] = field(default_factory=dict)
    message: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SafetyCheck":
        """Create SafetyCheck from dictionary."""
        return cls(
            check_type=data.get("check", ""),
            params={k: v for k, v in data.items() if k not in ["check", "message"]},
            message=data.get("message", "")
        )


@dataclass
class LearningData:
    """Learning data for skill usage patterns."""

    skill_usage: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    """Maps skill_name → usage statistics"""

    argument_patterns: Dict[str, Dict[str, int]] = field(default_factory=dict)
    """Maps 'skill.argument' → {value: count}"""

    recent_skills: List[str] = field(default_factory=list)
    """Recently used skills (most recent first)"""

    query_patterns: Dict[str, List[str]] = field(default_factory=dict)
    """Maps skill_name → list of successful queries"""

    def get_skill_success_rate(self, skill_name: str) -> float:
        """Get success rate for a skill."""
        if skill_name not in self.skill_usage:
            return 0.0

        usage = self.skill_usage[skill_name]
        total = usage.get('count', 0)
        success = usage.get('success_count', 0)

        if total == 0:
            return 0.0

        return success / total

    def get_most_common_argument(
        self, skill_name: str, arg_name: str
    ) -> Optional[str]:
        """Get most commonly used argument value."""
        key = f"{skill_name}.{arg_name}"
        patterns = self.argument_patterns.get(key, {})

        if not patterns:
            return None

        return max(patterns.items(), key=lambda x: x[1])[0]

    def add_recent_skill(self, skill_name: str, max_recent: int = 10) -> None:
        """Add skill to recent list (maintains FIFO)."""
        if skill_name in self.recent_skills:
            self.recent_skills.remove(skill_name)

        self.recent_skills.insert(0, skill_name)

        # Keep only max_recent items
        self.recent_skills = self.recent_skills[:max_recent]


@dataclass
class SessionData:
    """Session data for cross-session persistence."""

    timestamp: float
    project_type: str
    recent_queries: List[str] = field(default_factory=list)
    learning_data: Optional[LearningData] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            'timestamp': self.timestamp,
            'project_type': self.project_type,
            'recent_queries': self.recent_queries,
            'learning_data': {
                'skill_usage': self.learning_data.skill_usage,
                'argument_patterns': self.learning_data.argument_patterns,
                'recent_skills': self.learning_data.recent_skills,
                'query_patterns': self.learning_data.query_patterns
            } if self.learning_data else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SessionData":
        """Create SessionData from dictionary."""
        learning_data = None
        if data.get('learning_data'):
            ld = data['learning_data']
            learning_data = LearningData(
                skill_usage=ld.get('skill_usage', {}),
                argument_patterns=ld.get('argument_patterns', {}),
                recent_skills=ld.get('recent_skills', []),
                query_patterns=ld.get('query_patterns', {})
            )

        return cls(
            timestamp=data['timestamp'],
            project_type=data['project_type'],
            recent_queries=data.get('recent_queries', []),
            learning_data=learning_data
        )
