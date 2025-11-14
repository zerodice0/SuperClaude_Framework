"""
Data models for intent detection system.

These models represent skills, matches, and context information used
in the intent detection pipeline.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class MatchSource(Enum):
    """Source of a skill match."""

    KEYWORD = "keyword"
    PATTERN = "pattern"
    PRIMARY = "primary"
    CONTEXT = "context"


class InferSource(Enum):
    """Sources for argument inference."""

    USER_QUERY = "user_query"
    PROJECT_CONTEXT = "project_context"
    GIT_HISTORY = "git_history"
    LEARNING = "learning"


@dataclass
class IntentMetadata:
    """Intent detection metadata from skill frontmatter."""

    primary: List[str] = field(default_factory=list)
    """Primary patterns with {param} placeholders"""

    keywords: List[str] = field(default_factory=list)
    """Keywords for fast matching"""

    patterns: List[str] = field(default_factory=list)
    """Regex patterns with (?P<name>...) named groups"""

    contexts: List[str] = field(default_factory=list)
    """Context hints for relevance boosting"""


@dataclass
class ArgumentSchema:
    """Argument schema definition from skill frontmatter."""

    name: str
    type: str  # 'string', 'enum', 'int', 'bool', 'path'
    required: bool = False
    description: str = ""
    infer_from: List[str] = field(default_factory=list)
    default: Optional[Any] = None
    values: Optional[List[str]] = None  # For enum type


@dataclass
class AutoTriggerConfig:
    """Auto-execution configuration."""

    enabled: bool = False
    confidence_threshold: float = 0.85
    confirm_before_execution: bool = True
    safety_checks: List[str] = field(default_factory=list)


@dataclass
class Skill:
    """Skill metadata loaded from YAML frontmatter."""

    name: str
    display_name: str
    description: str
    version: str
    category: str
    complexity: str

    # Intent detection
    intents: IntentMetadata
    arguments: List[ArgumentSchema] = field(default_factory=list)

    # Auto-execution
    auto_trigger: AutoTriggerConfig = field(
        default_factory=lambda: AutoTriggerConfig()
    )

    # Dependencies
    mcp_servers: List[str] = field(default_factory=list)
    personas: List[str] = field(default_factory=list)

    # Metadata
    author: str = ""
    tags: List[str] = field(default_factory=list)

    # File path (for loading full content)
    file_path: Optional[Path] = None


@dataclass
class FileStructure:
    """Project file structure information."""

    root_dir: Path
    source_dirs: List[Path] = field(default_factory=list)
    test_dirs: List[Path] = field(default_factory=list)
    config_files: List[Path] = field(default_factory=list)
    total_files: int = 0


@dataclass
class GitInfo:
    """Git repository information."""

    has_repo: bool = False
    current_branch: str = ""
    main_branch: str = ""
    recent_commits: List[Dict[str, str]] = field(default_factory=list)
    uncommitted_changes: int = 0
    status: str = ""


@dataclass
class Dependencies:
    """Project dependencies information."""

    package_manager: str = ""  # 'npm', 'uv', 'pip', etc.
    config_file: Optional[Path] = None
    dependencies: Dict[str, str] = field(default_factory=dict)
    dev_dependencies: Dict[str, str] = field(default_factory=dict)


@dataclass
class TestingInfo:
    """Testing framework information."""

    framework: str = ""  # 'pytest', 'jest', 'vitest', etc.
    test_dirs: List[Path] = field(default_factory=list)
    config_file: Optional[Path] = None


@dataclass
class ProjectContext:
    """Current project context information."""

    project_type: str = "unknown"  # 'python', 'typescript', 'mixed'
    structure: FileStructure = field(default_factory=lambda: FileStructure(Path.cwd()))
    git_info: GitInfo = field(default_factory=GitInfo)
    dependencies: Dependencies = field(default_factory=Dependencies)
    testing: TestingInfo = field(default_factory=TestingInfo)

    # Active contexts for boosting
    active_contexts: List[str] = field(default_factory=list)

    # Recently used skills (for learning boost)
    recent_skills: List[str] = field(default_factory=list)


@dataclass
class SkillMatch:
    """Represents a skill match with confidence and inferred arguments."""

    skill: Skill
    confidence: float  # 0.0-1.0
    match_source: MatchSource
    arguments: Dict[str, Any] = field(default_factory=dict)
    explanation: str = ""
    base_confidence: float = 0.0  # Before boosting

    def __post_init__(self):
        """Set base_confidence from confidence if not provided."""
        if self.base_confidence == 0.0:
            self.base_confidence = self.confidence

    @property
    def auto_execute(self) -> bool:
        """Check if this match should auto-execute."""
        if not self.skill.auto_trigger.enabled:
            return False

        if self.confidence < self.skill.auto_trigger.confidence_threshold:
            return False

        # Check required arguments are present
        required_args = [arg for arg in self.skill.arguments if arg.required]
        if not all(arg.name in self.arguments for arg in required_args):
            return False

        # Don't auto-execute if confirmation required
        if self.skill.auto_trigger.confirm_before_execution:
            return False

        return True

    def format_command(self) -> str:
        """Format as slash command with arguments."""
        cmd = f"/sc:{self.skill.name}"

        for arg_name, arg_value in self.arguments.items():
            if isinstance(arg_value, bool):
                if arg_value:
                    cmd += f" --{arg_name}"
            else:
                # Quote string values if they contain spaces
                if isinstance(arg_value, str) and " " in arg_value:
                    cmd += f' --{arg_name} "{arg_value}"'
                else:
                    cmd += f" --{arg_name} {arg_value}"

        return cmd


@dataclass
class MatchResult:
    """Result of intent detection matching."""

    query: str
    matches: List[SkillMatch] = field(default_factory=list)
    context: Optional[ProjectContext] = None
    elapsed_ms: float = 0.0

    @property
    def top_match(self) -> Optional[SkillMatch]:
        """Get the highest confidence match."""
        return self.matches[0] if self.matches else None

    @property
    def high_confidence(self) -> bool:
        """Check if top match has high confidence (≥0.85)."""
        return self.top_match.confidence >= 0.85 if self.top_match else False

    def format_suggestions(self) -> str:
        """Format suggestions for display."""
        if not self.matches:
            return "❌ No matching skills found for your query."

        lines = [
            f"🎯 Intent Detection Results ({len(self.matches)} matches):",
            ""
        ]

        for i, match in enumerate(self.matches[:3], 1):
            lines.append(f"{i}. {match.format_command()}")
            lines.append(
                f"   Confidence: {match.confidence * 100:.0f}% | "
                f"Source: {match.match_source.value}"
            )
            lines.append(f"   ℹ️  {match.skill.description}")
            if match.explanation:
                lines.append(f"   💡 {match.explanation}")
            lines.append("")

        if self.top_match and self.top_match.auto_execute:
            lines.append("✅ Top match will auto-execute (high confidence)")
        else:
            lines.append("Press [1] to execute top match, or [2-3] for alternatives")

        return "\n".join(lines)
