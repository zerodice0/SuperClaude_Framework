"""
SkillMatcher - Main orchestrator for intent detection.

The SkillMatcher loads skill metadata, coordinates the matching pipeline,
and returns ranked suggestions based on user queries.
"""

import re
import time
from pathlib import Path
from typing import Dict, List, Optional

import yaml

from .models import (
    ArgumentSchema,
    AutoTriggerConfig,
    IntentMetadata,
    MatchResult,
    ProjectContext,
    Skill,
    SkillMatch,
)


class SkillMatcher:
    """Main orchestrator for intent detection and skill matching."""

    def __init__(self, skills_dir: Path):
        """
        Initialize matcher with skills directory.

        Args:
            skills_dir: Path to skills directory containing SKILL.md files
        """
        self.skills_dir = skills_dir
        self.skills: Dict[str, Skill] = {}
        self._keyword_index: Dict[str, List[str]] = {}

        # Load all skills metadata
        self._load_skills()
        self._build_keyword_index()

    def _load_skills(self) -> None:
        """Load all skill metadata from SKILL.md files."""
        if not self.skills_dir.exists():
            raise ValueError(f"Skills directory not found: {self.skills_dir}")

        for skill_dir in self.skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue

            skill_file = skill_dir / "SKILL.md"
            if not skill_file.exists():
                continue

            try:
                skill = self._load_skill_metadata(skill_file)
                self.skills[skill.name] = skill
            except Exception as e:
                print(f"⚠️  Failed to load skill {skill_dir.name}: {e}")

    def _load_skill_metadata(self, skill_file: Path) -> Skill:
        """
        Load skill metadata from SKILL.md frontmatter.

        Args:
            skill_file: Path to SKILL.md file

        Returns:
            Skill object with metadata
        """
        content = skill_file.read_text()

        # Extract YAML frontmatter
        match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
        if not match:
            raise ValueError(f"No frontmatter found in {skill_file}")

        frontmatter = yaml.safe_load(match.group(1))

        # Parse intent metadata
        intents_data = frontmatter.get("intents", {})
        intents = IntentMetadata(
            primary=intents_data.get("primary", []),
            keywords=intents_data.get("keywords", []),
            patterns=intents_data.get("patterns", []),
            contexts=intents_data.get("contexts", []),
        )

        # Parse arguments
        arguments = []
        for arg_data in frontmatter.get("arguments", []):
            arg = ArgumentSchema(
                name=arg_data["name"],
                type=arg_data.get("type", "string"),
                required=arg_data.get("required", False),
                description=arg_data.get("description", ""),
                infer_from=arg_data.get("infer_from", []),
                default=arg_data.get("default"),
                values=arg_data.get("values"),
            )
            arguments.append(arg)

        # Parse auto-trigger config
        auto_data = frontmatter.get("auto_trigger", {})
        auto_trigger = AutoTriggerConfig(
            enabled=auto_data.get("enabled", False),
            confidence_threshold=auto_data.get("confidence_threshold", 0.85),
            confirm_before_execution=auto_data.get("confirm_before_execution", True),
            safety_checks=auto_data.get("safety_checks", []),
        )

        # Create skill object
        skill = Skill(
            name=frontmatter["name"],
            display_name=frontmatter.get("display_name", frontmatter["name"]),
            description=frontmatter.get("description", ""),
            version=frontmatter.get("version", "1.0.0"),
            category=frontmatter.get("category", "utility"),
            complexity=frontmatter.get("complexity", "standard"),
            intents=intents,
            arguments=arguments,
            auto_trigger=auto_trigger,
            mcp_servers=frontmatter.get("mcp_servers", []),
            personas=frontmatter.get("personas", []),
            author=frontmatter.get("author", ""),
            tags=frontmatter.get("tags", []),
            file_path=skill_file,
        )

        return skill

    def _build_keyword_index(self) -> None:
        """Build inverted index for fast keyword lookup."""
        self._keyword_index.clear()

        for skill_name, skill in self.skills.items():
            for keyword in skill.intents.keywords:
                keyword_lower = keyword.lower()
                if keyword_lower not in self._keyword_index:
                    self._keyword_index[keyword_lower] = []
                self._keyword_index[keyword_lower].append(skill_name)

    def match(
        self, user_query: str, context: Optional[ProjectContext] = None
    ) -> MatchResult:
        """
        Match user query to skills.

        Args:
            user_query: User's natural language query
            context: Optional project context (analyzed if not provided)

        Returns:
            MatchResult with top 3 matches ranked by confidence
        """
        start_time = time.perf_counter()

        # Normalize query
        query_lower = user_query.lower().strip()

        # Get or create context
        if context is None:
            from .analyzer import ContextAnalyzer

            analyzer = ContextAnalyzer()
            context = analyzer.analyze()

        # Stage 1: Keyword matching
        keyword_matches = self._match_keywords(query_lower)

        # Stage 2: Pattern matching
        pattern_matches = self._match_patterns(user_query)

        # Stage 3: Primary pattern matching
        primary_matches = self._match_primary(user_query)

        # Combine and deduplicate matches
        all_matches = self._combine_matches(
            keyword_matches, pattern_matches, primary_matches
        )

        # Calculate confidence scores
        for match in all_matches:
            match.confidence = self._calculate_confidence(match, user_query, context)

        # Sort by confidence and take top 3
        ranked_matches = sorted(
            all_matches, key=lambda m: m.confidence, reverse=True
        )[:3]

        # Infer arguments for top matches
        from .inferrer import ArgumentInferrer

        inferrer = ArgumentInferrer()
        for match in ranked_matches:
            match.arguments = inferrer.infer(user_query, match.skill, context)

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        return MatchResult(
            query=user_query,
            matches=ranked_matches,
            context=context,
            elapsed_ms=elapsed_ms,
        )

    def _match_keywords(self, query_lower: str) -> List[SkillMatch]:
        """Match skills by keywords."""
        matches: Dict[str, SkillMatch] = {}
        query_words = set(query_lower.split())

        for word in query_words:
            if word in self._keyword_index:
                for skill_name in self._keyword_index[word]:
                    if skill_name not in matches:
                        skill = self.skills[skill_name]
                        matches[skill_name] = SkillMatch(
                            skill=skill,
                            confidence=0.60,  # Base for single keyword
                            match_source=MatchSource.KEYWORD,
                            explanation=f"Keyword match: {word}",
                            base_confidence=0.60,
                        )
                    else:
                        # Multiple keyword match - increase confidence
                        matches[skill_name].confidence = min(
                            matches[skill_name].confidence + 0.15, 0.75
                        )
                        matches[skill_name].base_confidence = matches[
                            skill_name
                        ].confidence

        return list(matches.values())

    def _match_patterns(self, query: str) -> List[SkillMatch]:
        """Match skills by regex patterns."""
        matches: List[SkillMatch] = []

        for skill in self.skills.values():
            for pattern in skill.intents.patterns:
                try:
                    match = re.search(pattern, query, re.IGNORECASE)
                    if match:
                        # Extract named groups as arguments
                        extracted_args = match.groupdict()

                        matches.append(
                            SkillMatch(
                                skill=skill,
                                confidence=0.85,
                                match_source=MatchSource.PATTERN,
                                arguments=extracted_args,
                                explanation=f"Pattern match: {pattern}",
                                base_confidence=0.85,
                            )
                        )
                        break  # Only match first pattern
                except re.error:
                    # Invalid regex - skip
                    continue

        return matches

    def _match_primary(self, query: str) -> List[SkillMatch]:
        """Match skills by primary patterns."""
        matches: List[SkillMatch] = []
        query_lower = query.lower()

        for skill in self.skills.values():
            for primary in skill.intents.primary:
                # Convert {param} placeholders to regex
                pattern = self._primary_to_regex(primary)

                try:
                    match = re.search(pattern, query_lower)
                    if match:
                        # Extract parameters
                        extracted_args = match.groupdict()

                        matches.append(
                            SkillMatch(
                                skill=skill,
                                confidence=0.90,
                                match_source=MatchSource.PRIMARY,
                                arguments=extracted_args,
                                explanation=f"Primary pattern match: {primary}",
                                base_confidence=0.90,
                            )
                        )
                        break  # Only match first primary pattern
                except re.error:
                    # Invalid pattern - skip
                    continue

        return matches

    def _primary_to_regex(self, primary: str) -> str:
        """
        Convert primary pattern to regex.

        Example:
            "troubleshoot {issue}" -> "troubleshoot (?P<issue>.+)"
        """
        # Escape special regex characters except {}
        escaped = re.escape(primary)

        # Replace \{param\} with (?P<param>.+)
        pattern = re.sub(r"\\{(\w+)\\}", r"(?P<\1>.+)", escaped)

        # Make spaces flexible
        pattern = pattern.replace(r"\ ", r"\s+")

        return pattern

    def _combine_matches(self, *match_lists: List[SkillMatch]) -> List[SkillMatch]:
        """
        Combine and deduplicate matches from different sources.

        Higher confidence sources take precedence.
        """
        combined: Dict[str, SkillMatch] = {}

        for match_list in match_lists:
            for match in match_list:
                skill_name = match.skill.name

                if skill_name not in combined:
                    combined[skill_name] = match
                else:
                    # Keep higher confidence match
                    if match.confidence > combined[skill_name].confidence:
                        combined[skill_name] = match

        return list(combined.values())

    def _calculate_confidence(
        self, match: SkillMatch, query: str, context: ProjectContext
    ) -> float:
        """
        Calculate final confidence score with boosters.

        Base scores:
        - Primary pattern: 0.90
        - Regex pattern: 0.85
        - Multiple keywords: 0.75
        - Single keyword: 0.60

        Boosters (+0.05 each, max +0.15):
        - Context relevance
        - Recent usage
        - Argument completeness
        """
        base_score = match.base_confidence

        # Context boost
        if any(
            ctx in context.active_contexts for ctx in match.skill.intents.contexts
        ):
            base_score += 0.05
            match.explanation += " | Context boost"

        # Learning boost (recently used)
        if match.skill.name in context.recent_skills:
            base_score += 0.05
            match.explanation += " | Recent usage boost"

        # Argument completeness boost
        required_args = [arg for arg in match.skill.arguments if arg.required]
        if required_args and all(arg.name in match.arguments for arg in required_args):
            base_score += 0.05
            match.explanation += " | Complete arguments"

        return min(base_score, 1.0)

    def get_skill(self, name: str) -> Optional[Skill]:
        """Get skill by name."""
        return self.skills.get(name)

    def list_skills(self) -> List[Skill]:
        """List all loaded skills."""
        return list(self.skills.values())


# Import at end to avoid circular dependency
from .models import MatchSource
