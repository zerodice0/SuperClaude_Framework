# Phase C: Auto-Execution & Learning System - Design Document

**Version**: 1.0.0
**Date**: 2025-11-14
**Status**: Design Complete - Ready for Implementation

## Overview

Phase C implements automatic skill execution for high-confidence matches and a learning system that improves recommendations over time. The system includes safety validations, execution tracking, and cross-session persistence using Serena MCP.

## Architecture

### System Components

```
SkillMatcher Result (≥85% confidence)
    ↓
┌─────────────────────────────────────────┐
│        ExecutionRouter                  │
│  - Check auto-execute eligibility       │
│  - Run safety validations               │
│  - Execute skill or request confirmation│
└─────────────────────────────────────────┘
    ↓           ↓              ↓
┌──────────┐ ┌──────────┐ ┌──────────────┐
│ Safety   │ │ Learning │ │   Session    │
│Validator │ │  System  │ │ Persistence  │
└──────────┘ └──────────┘ └──────────────┘
    ↓           ↓              ↓
┌─────────────────────────────────────────┐
│         Execution Result                │
│  - Success/failure tracking             │
│  - Learning data updates                │
│  - Session persistence                  │
└─────────────────────────────────────────┘
    ↓
User receives execution result + feedback
```

### Core Classes

#### 1. ExecutionRouter

```python
class ExecutionRouter:
    """Routes high-confidence matches to automatic execution."""

    def __init__(self, matcher: SkillMatcher):
        self.matcher = matcher
        self.validator = SafetyValidator()
        self.learner = LearningSystem()

    def execute_or_suggest(
        self,
        query: str,
        context: Optional[ProjectContext] = None
    ) -> ExecutionResult:
        """
        Execute high-confidence matches automatically or suggest alternatives.

        Flow:
        1. Match query to skills (using SkillMatcher)
        2. Check if top match is auto-executable
        3. Run safety validations
        4. Execute skill or return suggestions
        5. Track execution and update learning data
        """
        # Match query
        match_result = self.matcher.match(query, context)

        if not match_result.matches:
            return ExecutionResult(
                query=query,
                executed=False,
                suggestions=match_result.format_suggestions()
            )

        top_match = match_result.top_match

        # Check auto-execute eligibility
        if not self._should_auto_execute(top_match):
            return ExecutionResult(
                query=query,
                executed=False,
                suggestions=match_result.format_suggestions()
            )

        # Run safety validations
        safety_result = self.validator.validate(top_match, context)
        if not safety_result.safe:
            return ExecutionResult(
                query=query,
                executed=False,
                suggestions=match_result.format_suggestions(),
                warning=safety_result.warning
            )

        # Execute skill
        exec_result = self._execute_skill(top_match)

        # Track execution and update learning
        self.learner.track_execution(query, top_match, exec_result)

        return exec_result

    def _should_auto_execute(self, match: SkillMatch) -> bool:
        """
        Determine if match should auto-execute.

        Criteria:
        1. Auto-trigger enabled in skill config
        2. Confidence ≥ threshold (default 0.85)
        3. All required arguments inferred
        4. No confirmation required
        5. Not a destructive operation
        """
        if not match.skill.auto_trigger.enabled:
            return False

        if match.confidence < match.skill.auto_trigger.confidence_threshold:
            return False

        required_args = [arg for arg in match.skill.arguments if arg.required]
        if not all(arg.name in match.arguments for arg in required_args):
            return False

        if match.skill.auto_trigger.confirm_before_execution:
            return False

        return True
```

#### 2. SafetyValidator

```python
class SafetyValidator:
    """Validates safety of skill execution."""

    def validate(
        self,
        match: SkillMatch,
        context: ProjectContext
    ) -> SafetyResult:
        """
        Run safety checks before execution.

        Checks:
        1. No destructive operations on main branch
        2. Required dependencies available
        3. Sufficient disk space
        4. No file conflicts
        5. Custom safety checks from skill config
        """
        warnings = []

        # Check 1: Destructive operations on main branch
        if self._is_destructive(match.skill) and context.git_info.current_branch == context.git_info.main_branch:
            return SafetyResult(
                safe=False,
                warning="Destructive operation on main branch. Switch to feature branch first."
            )

        # Check 2: Dependencies
        if not self._check_dependencies(match.skill, context):
            warnings.append("Some dependencies may not be available")

        # Check 3: Disk space (for file operations)
        if self._needs_disk_space(match.skill):
            if not self._check_disk_space():
                return SafetyResult(
                    safe=False,
                    warning="Insufficient disk space"
                )

        # Check 4: File conflicts
        if self._may_modify_files(match.skill):
            conflicts = self._check_file_conflicts(match, context)
            if conflicts:
                return SafetyResult(
                    safe=False,
                    warning=f"File conflicts detected: {', '.join(conflicts)}"
                )

        # Check 5: Custom safety checks
        for check in match.skill.auto_trigger.safety_checks:
            result = self._run_custom_check(check, match, context)
            if not result.passed:
                return SafetyResult(
                    safe=False,
                    warning=result.message
                )

        return SafetyResult(
            safe=True,
            warnings=warnings
        )

    def _is_destructive(self, skill: Skill) -> bool:
        """Check if skill performs destructive operations."""
        destructive_keywords = ['delete', 'remove', 'cleanup', 'reset', 'drop']
        return any(kw in skill.name.lower() for kw in destructive_keywords)
```

#### 3. LearningSystem

```python
class LearningSystem:
    """Learns from usage patterns to improve recommendations."""

    def __init__(self):
        # Serena MCP integration for persistent storage
        self.memory_key = "superclaude_learning_data"

    def track_execution(
        self,
        query: str,
        match: SkillMatch,
        result: ExecutionResult
    ) -> None:
        """
        Track execution for learning.

        Stores:
        - Query → Skill mapping with success rate
        - Argument inference accuracy
        - Common usage patterns
        - User corrections
        """
        data = self._load_learning_data()

        # Track query → skill mapping
        skill_name = match.skill.name
        if skill_name not in data['skill_usage']:
            data['skill_usage'][skill_name] = {
                'count': 0,
                'success_count': 0,
                'queries': []
            }

        data['skill_usage'][skill_name]['count'] += 1
        if result.success:
            data['skill_usage'][skill_name]['success_count'] += 1

        # Track query pattern
        if query not in data['skill_usage'][skill_name]['queries']:
            data['skill_usage'][skill_name]['queries'].append(query)

        # Track argument patterns
        for arg_name, arg_value in match.arguments.items():
            key = f"{skill_name}.{arg_name}"
            if key not in data['argument_patterns']:
                data['argument_patterns'][key] = {}

            value_str = str(arg_value)
            if value_str not in data['argument_patterns'][key]:
                data['argument_patterns'][key][value_str] = 0
            data['argument_patterns'][key][value_str] += 1

        # Save updated data
        self._save_learning_data(data)

    def get_recent_skills(self, limit: int = 5) -> List[str]:
        """Get recently used skills for context boosting."""
        data = self._load_learning_data()
        recent = data.get('recent_skills', [])
        return recent[:limit]

    def get_common_argument(self, skill_name: str, arg_name: str) -> Optional[Any]:
        """Get most commonly used argument value for a skill."""
        data = self._load_learning_data()
        key = f"{skill_name}.{arg_name}"

        patterns = data.get('argument_patterns', {}).get(key, {})
        if not patterns:
            return None

        # Return most common value
        return max(patterns.items(), key=lambda x: x[1])[0]

    def _load_learning_data(self) -> Dict[str, Any]:
        """
        Load learning data from Serena MCP.

        Uses Serena's read_memory tool to retrieve persistent data.
        """
        # TODO: Integrate with Serena MCP
        # For now, use in-memory storage
        if not hasattr(self, '_data'):
            self._data = {
                'skill_usage': {},
                'argument_patterns': {},
                'recent_skills': []
            }
        return self._data

    def _save_learning_data(self, data: Dict[str, Any]) -> None:
        """
        Save learning data to Serena MCP.

        Uses Serena's write_memory tool for persistent storage.
        """
        # TODO: Integrate with Serena MCP
        self._data = data
```

#### 4. SessionPersistence

```python
class SessionPersistence:
    """Manages cross-session learning data."""

    def __init__(self):
        self.session_key = "superclaude_session_data"

    def save_session(
        self,
        context: ProjectContext,
        recent_queries: List[str],
        learning_data: Dict[str, Any]
    ) -> None:
        """
        Save session data for cross-session continuity.

        Stores:
        - Project context snapshot
        - Recent queries and their results
        - Learning data updates
        """
        session_data = {
            'timestamp': time.time(),
            'project_type': context.project_type,
            'recent_queries': recent_queries,
            'learning_data': learning_data
        }

        # TODO: Use Serena MCP write_memory
        self._store_session(session_data)

    def load_session(self) -> Optional[Dict[str, Any]]:
        """
        Load previous session data.

        Returns:
        - Session data if available
        - None if no previous session
        """
        # TODO: Use Serena MCP read_memory
        return self._retrieve_session()

    def _store_session(self, data: Dict[str, Any]) -> None:
        """Store session data using Serena MCP."""
        # Stub - will integrate with Serena
        pass

    def _retrieve_session(self) -> Optional[Dict[str, Any]]:
        """Retrieve session data using Serena MCP."""
        # Stub - will integrate with Serena
        return None
```

## Data Structures

### ExecutionResult

```python
@dataclass
class ExecutionResult:
    """Result of skill execution or suggestion."""

    query: str
    executed: bool
    success: bool = False
    output: str = ""
    suggestions: str = ""
    warning: Optional[str] = None
    execution_time_ms: float = 0.0
    skill_used: Optional[str] = None
```

### SafetyResult

```python
@dataclass
class SafetyResult:
    """Result of safety validation."""

    safe: bool
    warning: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
```

## Auto-Execution Flow

### Decision Tree

```
Match Result → Check Confidence
                ↓
         Confidence ≥ 85%? ───No──→ Show Suggestions
                ↓ Yes
         Auto-Trigger Enabled? ───No──→ Show Suggestions
                ↓ Yes
         Required Args Present? ───No──→ Show Suggestions
                ↓ Yes
         Confirm Required? ───Yes──→ Ask User Confirmation
                ↓ No
         Run Safety Checks
                ↓
         All Checks Pass? ───No──→ Show Warning + Suggestions
                ↓ Yes
         Execute Skill
                ↓
         Track Execution → Update Learning
                ↓
         Return Result
```

### Example: High Confidence Auto-Execute

**Query**: "help"

**Flow**:
1. Match: help skill (confidence: 0.90)
2. Auto-trigger: enabled, threshold: 0.90, no confirmation
3. Required args: None
4. Safety checks: All pass (read-only operation)
5. **Execute**: Display help content
6. Track: Update learning data
7. Return: Success with help output

### Example: Safety Block

**Query**: "cleanup all files"

**Flow**:
1. Match: cleanup skill (confidence: 0.92)
2. Auto-trigger: enabled
3. Required args: Present
4. Safety checks: **FAIL** - destructive on main branch
5. **Block**: Show warning + suggestions
6. Return: Not executed, warning displayed

### Example: Low Confidence Suggest

**Query**: "do something with the API"

**Flow**:
1. Match: Multiple matches (top: 0.72)
2. Auto-trigger: enabled
3. **Confidence < 0.85**: Cannot auto-execute
4. Return: Top 3 suggestions for user selection

## Learning Algorithm

### Usage Tracking

```python
skill_usage = {
    "troubleshoot": {
        "count": 45,
        "success_count": 42,
        "queries": [
            "fix the login bug",
            "troubleshoot API timeout",
            "debug the crash"
        ]
    }
}
```

### Argument Pattern Learning

```python
argument_patterns = {
    "implement.type": {
        "feature": 30,
        "bug": 15,
        "refactor": 8
    },
    "test.type": {
        "all": 25,
        "unit": 12,
        "integration": 8
    }
}
```

### Confidence Boost from Learning

```python
def calculate_confidence_with_learning(
    base_confidence: float,
    skill_name: str,
    learning_data: Dict
) -> float:
    """
    Boost confidence based on learning data.

    Boosts:
    - Recent usage: +0.05 if used in last 5 queries
    - High success rate: +0.03 if >90% success rate
    - Common pattern: +0.02 if query matches known pattern
    """
    confidence = base_confidence

    # Recent usage boost
    recent_skills = learning_data.get('recent_skills', [])
    if skill_name in recent_skills[:5]:
        confidence += 0.05

    # Success rate boost
    usage = learning_data.get('skill_usage', {}).get(skill_name, {})
    if usage:
        success_rate = usage['success_count'] / max(usage['count'], 1)
        if success_rate > 0.9:
            confidence += 0.03

    return min(confidence, 1.0)
```

## Safety Validations

### Validation Categories

**1. Environment Checks**
- Git branch validation (no destructive ops on main)
- Dependency availability
- Disk space
- File system permissions

**2. Operation Checks**
- File conflict detection
- Resource locks
- Concurrent operation prevention

**3. Custom Checks**
- Skill-specific validations from config
- User-defined safety rules
- Project-specific constraints

### Safety Check Examples

```yaml
# In skill SKILL.md frontmatter
auto_trigger:
  enabled: true
  confidence_threshold: 0.85
  confirm_before_execution: false
  safety_checks:
    - check: git_branch
      allowed: [feature/*, bugfix/*]
      message: "Only auto-execute on feature/bugfix branches"
    - check: disk_space
      minimum_mb: 100
      message: "Requires at least 100MB free space"
    - check: no_conflicts
      files: ["package.json", "pyproject.toml"]
      message: "Cannot auto-execute with modified config files"
```

## Serena MCP Integration

### Memory Operations

**Write Learning Data**:
```python
# Using Serena MCP write_memory tool
serena.write_memory(
    key="superclaude_learning_data",
    value={
        "skill_usage": {...},
        "argument_patterns": {...},
        "recent_skills": [...]
    },
    metadata={
        "type": "learning_data",
        "version": "1.0.0"
    }
)
```

**Read Learning Data**:
```python
# Using Serena MCP read_memory tool
data = serena.read_memory(
    key="superclaude_learning_data"
)
```

**Think About Usage Patterns**:
```python
# Using Serena MCP think_about_* tools
insights = serena.think_about_collected_information(
    context="SuperClaude skill usage patterns",
    focus="optimization"
)
```

## Implementation Plan

### Week 5: Core Components

**Day 1-2: ExecutionRouter & SafetyValidator**
- Implement execution router with auto-execute logic
- Build safety validator with environment checks
- Add file conflict detection
- Implement custom safety check framework

**Day 3-4: LearningSystem**
- Usage tracking implementation
- Argument pattern learning
- Confidence boosting from learning data
- Serena MCP integration (stub first, then real)

**Day 5: SessionPersistence**
- Session save/load functionality
- Cross-session data sharing
- Serena MCP integration
- Learning data migration

### Week 6: Integration & Refinement

**Day 1-2: Integration Testing**
- End-to-end auto-execution tests
- Safety validation tests
- Learning system tests
- Cross-session persistence tests

**Day 3-4: Performance & UX**
- Execution feedback improvements
- Learning algorithm tuning
- Safety check optimization
- User experience refinements

**Day 5: Documentation & Launch**
- API documentation
- Usage examples
- Phase C completion report
- Production deployment preparation

## Files to Create

```
src/superclaude/execution/
├── __init__.py
├── router.py              # ExecutionRouter
├── validator.py           # SafetyValidator
├── learner.py             # LearningSystem
├── persistence.py         # SessionPersistence
├── models.py              # ExecutionResult, SafetyResult
└── utils.py               # Helper functions

tests/execution/
├── __init__.py
├── test_router.py
├── test_validator.py
├── test_learner.py
└── test_persistence.py

docs/developer-guide/
└── auto-execution-api.md  # API reference
```

## Success Criteria

### Functional Requirements
- ✅ Auto-execute skills with ≥85% confidence safely
- ✅ Block destructive operations on main branch
- ✅ Track usage and improve recommendations
- ✅ Persist learning data across sessions

### Non-Functional Requirements
- ✅ Safety validation <20ms
- ✅ Execution overhead <50ms
- ✅ Learning data storage <1MB
- ✅ Cross-session load <100ms

### Quality Requirements
- ✅ 90% test coverage for execution components
- ✅ Zero false negatives on safety checks
- ✅ Learning data backward compatible
- ✅ Comprehensive error handling

## Next Steps

1. ✅ Design document complete
2. ⏳ Implement ExecutionRouter and SafetyValidator
3. ⏳ Implement LearningSystem
4. ⏳ Implement SessionPersistence
5. ⏳ Integrate with Serena MCP
6. ⏳ Create integration tests
7. ⏳ Performance tuning
8. ⏳ Document API and usage

---

**Status**: Ready for Implementation
**Next**: Begin implementation with ExecutionRouter and SafetyValidator
