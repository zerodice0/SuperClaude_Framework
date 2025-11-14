# Phase B: Intent Detection System - Design Document

**Version**: 1.0.0
**Date**: 2025-11-14
**Status**: Design Complete - Ready for Implementation

## Overview

Phase B implements automatic intent detection to match user queries with appropriate skills. The system analyzes natural language input, infers required arguments, and suggests the top 3 matching skills with confidence scores.

## Architecture

### System Components

```
User Input
    ↓
┌─────────────────────────────────────────┐
│        SkillMatcher (Orchestrator)      │
│  - Load skills metadata                 │
│  - Coordinate matching pipeline         │
│  - Return ranked suggestions            │
└─────────────────────────────────────────┘
    ↓           ↓              ↓
┌──────────┐ ┌──────────┐ ┌──────────────┐
│ Intent   │ │ Argument │ │   Context    │
│Classifier│ │ Inferrer │ │  Analyzers   │
└──────────┘ └──────────┘ └──────────────┘
    ↓           ↓              ↓
┌─────────────────────────────────────────┐
│         Suggestion Generator            │
│  - Rank matches by confidence           │
│  - Format top 3 suggestions             │
│  - Include inferred arguments           │
└─────────────────────────────────────────┘
    ↓
User receives ranked suggestions
```

### Core Classes

#### 1. SkillMatcher (Main Orchestrator)

```python
class SkillMatcher:
    """Main orchestrator for intent detection and skill matching."""

    def __init__(self, skills_dir: Path):
        self.skills = self._load_skills_metadata(skills_dir)
        self.intent_classifier = IntentClassifier(self.skills)
        self.argument_inferrer = ArgumentInferrer()
        self.context_analyzer = ContextAnalyzer()

    def match(self, user_query: str) -> List[SkillMatch]:
        """
        Match user query to skills.

        Returns top 3 matches with confidence scores and inferred arguments.
        """
        # 1. Get project context
        context = self.context_analyzer.analyze()

        # 2. Classify intent and match skills
        matches = self.intent_classifier.classify(user_query, context)

        # 3. Infer arguments for each match
        for match in matches:
            match.arguments = self.argument_inferrer.infer(
                user_query, match.skill, context
            )

        # 4. Rank by confidence and return top 3
        return sorted(matches, key=lambda m: m.confidence, reverse=True)[:3]
```

#### 2. IntentClassifier

```python
class IntentClassifier:
    """Classifies user intent using keyword, pattern, and context matching."""

    def classify(self, query: str, context: ProjectContext) -> List[SkillMatch]:
        """
        Classify intent with multi-stage matching:

        1. Keyword matching (fast, O(1))
        2. Pattern matching (regex with named groups)
        3. Context boosting (relevance adjustment)
        4. Confidence scoring (0.0-1.0)
        """
        matches = []

        # Stage 1: Keyword matching
        keyword_matches = self._match_keywords(query)

        # Stage 2: Pattern matching
        pattern_matches = self._match_patterns(query)

        # Stage 3: Primary pattern matching
        primary_matches = self._match_primary(query)

        # Combine and deduplicate
        all_matches = self._combine_matches(
            keyword_matches, pattern_matches, primary_matches
        )

        # Stage 4: Context boosting
        for match in all_matches:
            match.confidence = self._calculate_confidence(
                match, query, context
            )

        return all_matches
```

#### 3. ArgumentInferrer

```python
class ArgumentInferrer:
    """Infers skill arguments from query, context, and learning data."""

    def infer(
        self,
        query: str,
        skill: Skill,
        context: ProjectContext
    ) -> Dict[str, Any]:
        """
        Infer arguments using multiple sources:

        1. user_query: Extract from query text
        2. project_context: Analyze project structure
        3. git_history: Parse recent commits
        4. learning: Use historical patterns
        """
        arguments = {}

        for arg in skill.arguments:
            if 'user_query' in arg.infer_from:
                value = self._extract_from_query(query, arg)
                if value:
                    arguments[arg.name] = value

            if 'project_context' in arg.infer_from:
                value = self._infer_from_context(context, arg)
                if value:
                    arguments[arg.name] = value

            if 'git_history' in arg.infer_from:
                value = self._infer_from_git(context.git_info, arg)
                if value:
                    arguments[arg.name] = value

            if 'learning' in arg.infer_from:
                value = self._infer_from_learning(skill.name, arg)
                if value:
                    arguments[arg.name] = value

            # Use default if no value inferred
            if arg.name not in arguments and arg.default:
                arguments[arg.name] = arg.default

        return arguments
```

#### 4. ContextAnalyzer

```python
class ContextAnalyzer:
    """Analyzes project structure, git history, and dependencies."""

    def analyze(self) -> ProjectContext:
        """
        Analyze project context:

        - Project type (Python, TypeScript, etc.)
        - File structure and key directories
        - Git status and recent commits
        - Dependencies (package.json, pyproject.toml)
        - Testing framework
        """
        return ProjectContext(
            project_type=self._detect_project_type(),
            structure=self._analyze_structure(),
            git_info=self._analyze_git(),
            dependencies=self._analyze_dependencies(),
            testing=self._detect_testing_framework()
        )
```

## Data Structures

### SkillMatch

```python
@dataclass
class SkillMatch:
    """Represents a skill match with confidence and inferred arguments."""

    skill: Skill
    confidence: float  # 0.0-1.0
    match_source: str  # 'keyword', 'pattern', 'primary', 'context'
    arguments: Dict[str, Any]
    explanation: str  # Why this skill matched
```

### Skill (Metadata)

```python
@dataclass
class Skill:
    """Skill metadata loaded from YAML frontmatter."""

    name: str
    display_name: str
    description: str
    category: str
    complexity: str

    # Intent detection
    intents: IntentMetadata
    arguments: List[ArgumentSchema]

    # Auto-execution
    auto_trigger: AutoTriggerConfig

    # Dependencies
    mcp_servers: List[str]
    personas: List[str]
```

### IntentMetadata

```python
@dataclass
class IntentMetadata:
    """Intent detection metadata from skill frontmatter."""

    primary: List[str]      # Primary patterns with {param}
    keywords: List[str]     # Fast keyword matching
    patterns: List[str]     # Regex patterns with (?P<name>...)
    contexts: List[str]     # Context hints for boosting
```

### ProjectContext

```python
@dataclass
class ProjectContext:
    """Current project context information."""

    project_type: str  # 'python', 'typescript', 'mixed'
    structure: FileStructure
    git_info: GitInfo
    dependencies: Dependencies
    testing: TestingInfo
```

## Matching Algorithm

### Confidence Calculation

```python
def calculate_confidence(
    match: SkillMatch,
    query: str,
    context: ProjectContext
) -> float:
    """
    Calculate confidence score (0.0-1.0):

    Base scores:
    - Primary pattern match: 0.90
    - Regex pattern match: 0.85
    - Keyword match (multiple): 0.75
    - Keyword match (single): 0.60

    Boosters (+0.05 each, max +0.15):
    - Context relevance
    - Recent usage (learning)
    - Argument completeness

    Final score capped at 1.0
    """
    base_score = match.base_confidence

    # Context boost
    if any(ctx in context.active_contexts for ctx in skill.intents.contexts):
        base_score += 0.05

    # Learning boost (recently used)
    if skill.name in context.recent_skills:
        base_score += 0.05

    # Argument completeness boost
    required_args = [arg for arg in skill.arguments if arg.required]
    if required_args and all(arg.name in match.arguments for arg in required_args):
        base_score += 0.05

    return min(base_score, 1.0)
```

### Matching Stages

**Stage 1: Keyword Matching (Fast)**
- Build inverted index: keyword → skills
- O(1) lookup for each keyword in query
- Multiple keyword matches increase confidence

**Stage 2: Pattern Matching (Regex)**
- Apply regex patterns with named groups
- Extract argument values from matches
- Higher confidence than keyword-only

**Stage 3: Primary Pattern Matching**
- Match primary patterns with `{param}` placeholders
- Highest base confidence (0.90)
- Extract parameter values

**Stage 4: Context Boosting**
- Analyze project context
- Boost relevance based on context hints
- Consider recent usage patterns

## Performance Requirements

### Targets

- **Intent Classification**: <50ms
- **Argument Inference**: <30ms
- **Context Analysis**: <20ms (cached)
- **Total Matching**: <100ms

### Optimization Strategies

1. **Lazy Loading**: Load only frontmatter at startup
2. **Caching**: Cache context analysis results
3. **Inverted Index**: Fast keyword lookup
4. **Early Exit**: Return immediately for ≥0.95 confidence
5. **Parallel Processing**: Match multiple skills concurrently

## Auto-Execution Logic

```python
def should_auto_execute(match: SkillMatch) -> bool:
    """
    Determine if skill should auto-execute:

    1. Auto-trigger enabled in skill config
    2. Confidence >= threshold (default 0.85)
    3. All required arguments inferred
    4. Safety checks pass
    5. User confirmation (if required)
    """
    if not match.skill.auto_trigger.enabled:
        return False

    if match.confidence < match.skill.auto_trigger.confidence_threshold:
        return False

    required_args = [arg for arg in match.skill.arguments if arg.required]
    if not all(arg.name in match.arguments for arg in required_args):
        return False

    if match.skill.auto_trigger.confirm_before_execution:
        # Require user confirmation
        return False

    # All checks passed
    return True
```

## Example Workflow

### User Input: "fix the login bug"

**Step 1: Intent Classification**
```python
matches = [
    SkillMatch(
        skill=troubleshoot_skill,
        confidence=0.88,
        match_source='primary',  # "troubleshoot {issue}"
        arguments={'issue': 'login bug'},
        explanation='Primary pattern match: troubleshoot {issue}'
    ),
    SkillMatch(
        skill=implement_skill,
        confidence=0.72,
        match_source='keyword',  # 'fix'
        arguments={},
        explanation='Keyword match: fix'
    ),
    SkillMatch(
        skill=analyze_skill,
        confidence=0.65,
        match_source='context',  # debugging context
        arguments={'target': 'login'},
        explanation='Context match: debugging'
    )
]
```

**Step 2: Argument Inference**
```python
# For troubleshoot skill
arguments = {
    'issue': 'login bug',  # from user_query
    'analyze': True,       # from context (debugging)
    'root_cause': True     # from skill default
}
```

**Step 3: Suggestion UI**
```
🎯 Intent Detection Results (3 matches):

1. /sc:troubleshoot "login bug" --analyze --root-cause
   Confidence: 88% | Source: Primary pattern match
   ℹ️  Issue diagnosis and resolution with root cause analysis

2. /sc:implement
   Confidence: 72% | Source: Keyword match (fix)
   ℹ️  Feature and code implementation

3. /sc:analyze login
   Confidence: 65% | Source: Context match
   ℹ️  Code and architecture analysis

Press [1] to execute top match, or [2-3] for alternatives
```

## Implementation Plan

### Week 3: Core Components

**Day 1-2: SkillMatcher & IntentClassifier**
- Implement skill metadata loading
- Build keyword matching with inverted index
- Implement pattern matching with regex
- Add primary pattern matching

**Day 3-4: ArgumentInferrer**
- Query extraction with regex
- Project context inference
- Git history parsing
- Learning data integration (stub for now)

**Day 5: ContextAnalyzer**
- Project type detection
- File structure analysis
- Git status and history
- Dependency parsing

### Week 4: Integration & Testing

**Day 1-2: Suggestion UI & Auto-Execution**
- Format suggestion output
- Implement auto-execution logic
- Add safety validations
- User confirmation handling

**Day 3-4: Integration Testing**
- End-to-end tests for common queries
- Argument inference validation
- Performance benchmarks
- Edge case handling

**Day 5: Documentation & Refinement**
- API documentation
- Usage examples
- Performance tuning
- Phase B completion report

## Files to Create

```
src/superclaude/intent/
├── __init__.py
├── matcher.py              # SkillMatcher orchestrator
├── classifier.py           # IntentClassifier
├── inferrer.py             # ArgumentInferrer
├── analyzer.py             # ContextAnalyzer
├── models.py               # Data structures
└── utils.py                # Helper functions

tests/intent/
├── __init__.py
├── test_matcher.py
├── test_classifier.py
├── test_inferrer.py
├── test_analyzer.py
└── fixtures/
    └── sample_skills/

docs/developer-guide/
└── intent-detection-api.md  # API reference
```

## Success Criteria

### Functional Requirements
- ✅ Match user queries to skills with ≥70% accuracy
- ✅ Infer required arguments with ≥80% accuracy
- ✅ Return top 3 suggestions ranked by confidence
- ✅ Support all 30 migrated skills

### Non-Functional Requirements
- ✅ Intent classification <50ms
- ✅ Total matching pipeline <100ms
- ✅ Context analysis cached (startup only)
- ✅ Memory footprint <50MB for metadata

### Quality Requirements
- ✅ 90% test coverage for core components
- ✅ All tests pass with pytest
- ✅ Type hints for all public APIs
- ✅ Comprehensive documentation

## Next Steps

1. ✅ Design document complete
2. ⏳ Implement SkillMatcher and data models
3. ⏳ Implement IntentClassifier
4. ⏳ Implement ArgumentInferrer
5. ⏳ Implement ContextAnalyzer
6. ⏳ Create integration tests
7. ⏳ Benchmark performance
8. ⏳ Document API and usage

---

**Status**: Ready for Implementation
**Next**: Begin implementation with SkillMatcher and core data models
