"""
LearningSystem - Learns from usage patterns to improve recommendations.

Tracks skill usage, argument patterns, and query success to improve
future intent detection and confidence scoring.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..intent.models import SkillMatch
from .models import ExecutionResult, LearningData


class LearningSystem:
    """Learns from usage patterns to improve recommendations."""

    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize learning system.

        Args:
            storage_path: Path to store learning data (defaults to ~/.superclaude/learning.json)
        """
        if storage_path is None:
            home = Path.home()
            storage_dir = home / ".superclaude"
            storage_dir.mkdir(exist_ok=True)
            self.storage_path = storage_dir / "learning.json"
        else:
            self.storage_path = storage_path

        self._data: Optional[LearningData] = None

    def track_execution(
        self,
        query: str,
        match: SkillMatch,
        result: ExecutionResult
    ) -> None:
        """
        Track execution for learning.

        Updates:
        - Skill usage statistics
        - Query patterns for successful matches
        - Argument usage patterns
        - Recent skills list
        """
        data = self.load()

        skill_name = match.skill.name

        # Initialize skill usage if needed
        if skill_name not in data.skill_usage:
            data.skill_usage[skill_name] = {
                'count': 0,
                'success_count': 0
            }

        # Update usage stats
        data.skill_usage[skill_name]['count'] += 1
        if result.success:
            data.skill_usage[skill_name]['success_count'] += 1

        # Track query pattern for successful executions
        if result.success:
            if skill_name not in data.query_patterns:
                data.query_patterns[skill_name] = []

            if query not in data.query_patterns[skill_name]:
                # Keep max 10 query patterns per skill
                patterns = data.query_patterns[skill_name]
                if len(patterns) < 10:
                    patterns.append(query)

        # Track argument patterns
        for arg_name, arg_value in match.arguments.items():
            key = f"{skill_name}.{arg_name}"
            if key not in data.argument_patterns:
                data.argument_patterns[key] = {}

            value_str = str(arg_value)
            if value_str not in data.argument_patterns[key]:
                data.argument_patterns[key][value_str] = 0

            data.argument_patterns[key][value_str] += 1

        # Update recent skills
        data.add_recent_skill(skill_name)

        # Save updated data
        self.save(data)

    def get_recent_skills(self, limit: int = 5) -> List[str]:
        """
        Get recently used skills for context boosting.

        Args:
            limit: Maximum number of recent skills to return

        Returns:
            List of skill names (most recent first)
        """
        data = self.load()
        return data.recent_skills[:limit]

    def get_common_argument(
        self, skill_name: str, arg_name: str
    ) -> Optional[Any]:
        """
        Get most commonly used argument value for a skill.

        Args:
            skill_name: Name of the skill
            arg_name: Name of the argument

        Returns:
            Most common value or None
        """
        data = self.load()
        return data.get_most_common_argument(skill_name, arg_name)

    def get_success_rate(self, skill_name: str) -> float:
        """
        Get success rate for a skill.

        Args:
            skill_name: Name of the skill

        Returns:
            Success rate (0.0-1.0)
        """
        data = self.load()
        return data.get_skill_success_rate(skill_name)

    def calculate_learning_boost(
        self, skill_name: str, query: str
    ) -> float:
        """
        Calculate confidence boost from learning data.

        Boosts:
        - Recent usage: +0.05 if in last 5 skills
        - High success rate: +0.03 if >90% success
        - Query pattern match: +0.02 if query matches known pattern

        Args:
            skill_name: Name of the skill
            query: User query

        Returns:
            Confidence boost (0.0-0.10)
        """
        data = self.load()
        boost = 0.0

        # Recent usage boost
        if skill_name in data.recent_skills[:5]:
            boost += 0.05

        # Success rate boost
        success_rate = data.get_skill_success_rate(skill_name)
        if success_rate > 0.9:
            boost += 0.03

        # Query pattern match boost
        patterns = data.query_patterns.get(skill_name, [])
        query_lower = query.lower()
        if any(p.lower() in query_lower or query_lower in p.lower() for p in patterns):
            boost += 0.02

        return min(boost, 0.10)

    def load(self) -> LearningData:
        """
        Load learning data from storage.

        Returns:
            LearningData (creates new if file doesn't exist)
        """
        if self._data is not None:
            return self._data

        if not self.storage_path.exists():
            self._data = LearningData()
            return self._data

        try:
            with open(self.storage_path, 'r') as f:
                data_dict = json.load(f)

            self._data = LearningData(
                skill_usage=data_dict.get('skill_usage', {}),
                argument_patterns=data_dict.get('argument_patterns', {}),
                recent_skills=data_dict.get('recent_skills', []),
                query_patterns=data_dict.get('query_patterns', {})
            )
        except (json.JSONDecodeError, OSError):
            # If file is corrupted, start fresh
            self._data = LearningData()

        return self._data

    def save(self, data: LearningData) -> None:
        """
        Save learning data to storage.

        Args:
            data: LearningData to save
        """
        self._data = data

        data_dict = {
            'skill_usage': data.skill_usage,
            'argument_patterns': data.argument_patterns,
            'recent_skills': data.recent_skills,
            'query_patterns': data.query_patterns
        }

        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.storage_path, 'w') as f:
                json.dump(data_dict, f, indent=2)
        except OSError as e:
            # Log error but don't fail
            print(f"Warning: Failed to save learning data: {e}")

    def reset(self) -> None:
        """Reset all learning data."""
        self._data = LearningData()
        self.save(self._data)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get learning system statistics.

        Returns:
            Dictionary with stats (total skills tracked, most used, etc.)
        """
        data = self.load()

        total_executions = sum(
            usage['count'] for usage in data.skill_usage.values()
        )

        most_used = None
        if data.skill_usage:
            most_used = max(
                data.skill_usage.items(),
                key=lambda x: x[1]['count']
            )[0]

        return {
            'total_skills_tracked': len(data.skill_usage),
            'total_executions': total_executions,
            'most_used_skill': most_used,
            'recent_skills_count': len(data.recent_skills),
            'argument_patterns_count': len(data.argument_patterns)
        }
