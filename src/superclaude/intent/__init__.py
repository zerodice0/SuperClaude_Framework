"""
SuperClaude Intent Detection System.

This package provides automatic intent detection and skill matching
for natural language queries.

Main components:
- SkillMatcher: Orchestrates the matching pipeline
- IntentClassifier: Classifies user intent (embedded in SkillMatcher)
- ArgumentInferrer: Infers skill arguments
- ContextAnalyzer: Analyzes project context

Usage:
    >>> from superclaude.intent import SkillMatcher
    >>> from pathlib import Path
    >>>
    >>> matcher = SkillMatcher(Path("skills"))
    >>> result = matcher.match("fix the login bug")
    >>> print(result.format_suggestions())
"""

from .analyzer import ContextAnalyzer
from .inferrer import ArgumentInferrer
from .matcher import SkillMatcher
from .models import (
    ArgumentSchema,
    AutoTriggerConfig,
    Dependencies,
    FileStructure,
    GitInfo,
    InferSource,
    IntentMetadata,
    MatchResult,
    MatchSource,
    ProjectContext,
    Skill,
    SkillMatch,
    TestingInfo,
)

__all__ = [
    # Main components
    "SkillMatcher",
    "ArgumentInferrer",
    "ContextAnalyzer",
    # Data models
    "Skill",
    "SkillMatch",
    "MatchResult",
    "ProjectContext",
    "IntentMetadata",
    "ArgumentSchema",
    "AutoTriggerConfig",
    "FileStructure",
    "GitInfo",
    "Dependencies",
    "TestingInfo",
    # Enums
    "MatchSource",
    "InferSource",
]

__version__ = "1.0.0"
