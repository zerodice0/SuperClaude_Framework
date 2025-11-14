# Skill Metadata Schema

**Version**: 1.0.0
**Date**: 2025-11-14
**Purpose**: Define extended YAML frontmatter for Intent-Driven Skills

## Overview

Skills use extended YAML frontmatter to enable automatic intent detection, argument inference, and execution routing. This schema makes skills machine-readable while maintaining human-readable documentation.

## Complete Schema

```yaml
---
# === Basic Information ===
name: skill-name                      # Required: Kebab-case identifier
display_name: "Human Readable Name"   # Required: Display in UI
description: "Brief description"      # Required: One-line summary
version: 1.0.0                        # Required: Semantic versioning
category: workflow|utility|research|special  # Required
complexity: basic|standard|enhanced|advanced|high  # Required

# === Intent Detection ===
intents:
  primary:                            # Required: Main intent patterns
    - "verb {param}"                  # Template with {param} placeholders
    - "action {target}"
  keywords:                           # Required: Keyword list
    - keyword1, keyword2, keyword3
  patterns:                           # Required: Regex patterns
    - "^(verb1|verb2) (?P<param>.+)$"
  contexts:                           # Optional: Context hints
    - component_development
    - api_implementation

# === Argument Schema ===
arguments:                            # Required if skill takes arguments
  - name: argument_name               # Required: Argument identifier
    type: string|enum|int|bool|path   # Required: Data type
    required: true|false              # Required: Is mandatory?
    description: "What this arg does" # Required: Help text
    infer_from: user_query|project_context|git_history|learning  # Required
    default: value                    # Optional: Default value
    values: [opt1, opt2]             # Required for enum type
    validation: regex_pattern         # Optional: Validation pattern

# === Auto-Execution ===
auto_trigger:
  enabled: true|false                 # Required: Can auto-execute?
  confidence_threshold: 0.85          # Required: Min confidence (0.0-1.0)
  confirm_before_execution: true|false  # Required: Ask confirmation?
  safety_checks:                      # Optional: Pre-execution checks
    - confidence-check
    - architecture-compliance

# === Dependencies ===
mcp_servers:                          # Optional: Required MCP servers
  - context7
  - sequential
personas:                             # Optional: Personas to activate
  - architect
  - frontend
requires_skills:                      # Optional: Prerequisite skills
  - skill-name
optional_skills:                      # Optional: Enhancement skills
  - skill-name

# === Metadata ===
author: "Author Name"                 # Optional
tags:                                 # Optional: Search tags
  - tag1
  - tag2
---

# Skill Documentation

[Markdown documentation follows...]
```

## Field Specifications

### Basic Information

#### `name` (Required)
- **Type**: string
- **Format**: kebab-case
- **Example**: `implement`, `troubleshoot`, `deep-research`
- **Purpose**: Unique skill identifier, used in file paths and commands

#### `display_name` (Required)
- **Type**: string
- **Format**: Human-readable title case
- **Example**: "Feature Implementation", "Bug Troubleshooting"
- **Purpose**: Shown in UI and suggestions

#### `description` (Required)
- **Type**: string
- **Format**: Single sentence, <100 characters
- **Example**: "Diagnose and resolve code issues with systematic debugging"
- **Purpose**: Brief summary for skill selection

#### `version` (Required)
- **Type**: string
- **Format**: Semantic versioning (MAJOR.MINOR.PATCH)
- **Example**: "1.0.0", "2.1.3"
- **Purpose**: Track skill evolution, compatibility

#### `category` (Required)
- **Type**: enum
- **Values**: `workflow`, `utility`, `research`, `special`, `orchestration`
- **Purpose**: Organize skills by function
- **Examples**:
  - `workflow`: implement, troubleshoot, improve
  - `utility`: test, build, cleanup
  - `research`: research, analyze
  - `special`: brainstorm, pm

#### `complexity` (Required)
- **Type**: enum
- **Values**: `basic`, `standard`, `enhanced`, `advanced`, `high`
- **Purpose**: Indicate skill sophistication and token budget
- **Token Budgets**:
  - `basic`: 200 tokens
  - `standard`: 1,000 tokens
  - `enhanced`: 2,500 tokens
  - `advanced`: 5,000 tokens
  - `high`: 10,000+ tokens

### Intent Detection

#### `intents.primary` (Required)
- **Type**: array of strings
- **Format**: Template strings with `{param}` placeholders
- **Purpose**: Main intent patterns for matching
- **Examples**:
  ```yaml
  primary:
    - "implement {feature}"
    - "create {component}"
    - "build {functionality}"
    - "add {feature} feature"
  ```

#### `intents.keywords` (Required)
- **Type**: array of strings
- **Format**: Lowercase keywords, comma-separated
- **Purpose**: Fast keyword-based matching
- **Examples**:
  ```yaml
  keywords:
    - implement, create, build, develop, code, add
    - fix, debug, troubleshoot, resolve, diagnose
  ```

#### `intents.patterns` (Required)
- **Type**: array of strings
- **Format**: Python regex with named groups `(?P<name>...)`
- **Purpose**: Structured argument extraction
- **Examples**:
  ```yaml
  patterns:
    - "^(implement|create|build) (a |an )?(?P<feature>.+)$"
    - "^fix (?P<issue>.+) in (?P<location>.+)$"
    - "^(?P<action>analyze|improve) (?P<target>.+)$"
  ```

#### `intents.contexts` (Optional)
- **Type**: array of strings
- **Format**: Context identifiers
- **Purpose**: Boost relevance in specific contexts
- **Examples**:
  ```yaml
  contexts:
    - component_development
    - api_implementation
    - database_design
    - performance_optimization
  ```

### Argument Schema

#### Argument Object

Each argument is an object with the following fields:

```yaml
- name: feature                       # Unique identifier
  type: string                        # Data type
  required: true                      # Mandatory?
  description: "Feature to implement" # Help text
  infer_from: user_query             # Inference source
  default: null                       # Default value (optional)
  values: []                          # For enum types
  validation: null                    # Regex pattern (optional)
```

#### `arguments[].name` (Required)
- **Type**: string
- **Format**: snake_case
- **Purpose**: Argument identifier
- **Examples**: `feature`, `target`, `framework`, `test_type`

#### `arguments[].type` (Required)
- **Type**: enum
- **Values**: `string`, `enum`, `int`, `bool`, `path`
- **Purpose**: Data type for validation
- **Examples**:
  ```yaml
  - name: feature
    type: string

  - name: framework
    type: enum
    values: [react, vue, angular]

  - name: depth
    type: int

  - name: verbose
    type: bool

  - name: config_file
    type: path
  ```

#### `arguments[].required` (Required)
- **Type**: boolean
- **Purpose**: Is this argument mandatory?
- **Examples**:
  ```yaml
  - name: feature
    required: true

  - name: framework
    required: false
    default: auto-detect
  ```

#### `arguments[].infer_from` (Required)
- **Type**: enum
- **Values**: `user_query`, `project_context`, `git_history`, `learning`
- **Purpose**: Specify inference source
- **Examples**:
  ```yaml
  - name: feature
    infer_from: user_query          # Extract from query

  - name: framework
    infer_from: project_context      # From package.json

  - name: branch_pattern
    infer_from: git_history          # From git log

  - name: preferred_style
    infer_from: learning             # From usage history
  ```

#### `arguments[].values` (Required for enum type)
- **Type**: array of strings
- **Purpose**: Valid options for enum type
- **Examples**:
  ```yaml
  - name: framework
    type: enum
    values: [react, vue, angular, svelte]

  - name: test_type
    type: enum
    values: [unit, integration, e2e]
  ```

### Auto-Execution

#### `auto_trigger.enabled` (Required)
- **Type**: boolean
- **Purpose**: Can this skill auto-execute?
- **Default**: `true`
- **Note**: Set `false` for destructive operations

#### `auto_trigger.confidence_threshold` (Required)
- **Type**: float
- **Range**: 0.0 - 1.0
- **Purpose**: Minimum confidence for auto-execution
- **Recommended**: 0.85 for high confidence
- **Examples**:
  ```yaml
  confidence_threshold: 0.90  # Very high confidence
  confidence_threshold: 0.85  # High confidence (recommended)
  confidence_threshold: 0.70  # Medium confidence (suggest only)
  ```

#### `auto_trigger.confirm_before_execution` (Required)
- **Type**: boolean
- **Purpose**: Show confirmation UI before executing?
- **Recommended**: `true` for all skills
- **Examples**:
  ```yaml
  confirm_before_execution: true   # Safe: always confirm
  confirm_before_execution: false  # Dangerous: auto-execute silently
  ```

#### `auto_trigger.safety_checks` (Optional)
- **Type**: array of skill names
- **Purpose**: Pre-execution validation skills
- **Examples**:
  ```yaml
  safety_checks:
    - confidence-check           # Verify confidence ≥90%
    - architecture-compliance    # Check tech stack alignment
    - duplicate-detection        # No duplicate implementations
  ```

### Dependencies

#### `mcp_servers` (Optional)
- **Type**: array of strings
- **Purpose**: Required MCP servers
- **Examples**:
  ```yaml
  mcp_servers:
    - context7        # Official documentation
    - sequential      # Token-efficient reasoning
    - tavily          # Web research
    - serena          # Session persistence
  ```

#### `personas` (Optional)
- **Type**: array of strings
- **Purpose**: Personas to activate
- **Examples**:
  ```yaml
  personas:
    - architect       # System design
    - frontend        # UI implementation
    - backend         # API development
    - devops          # Infrastructure
  ```

#### `requires_skills` (Optional)
- **Type**: array of skill names
- **Purpose**: Prerequisite skills that must run first
- **Examples**:
  ```yaml
  requires_skills:
    - confidence-check  # Must check confidence first
  ```

#### `optional_skills` (Optional)
- **Type**: array of skill names
- **Purpose**: Enhancement skills that can improve results
- **Examples**:
  ```yaml
  optional_skills:
    - architecture-compliance  # Recommended but not required
  ```

## Complete Examples

### Example 1: Implement Skill

```yaml
---
name: implement
display_name: "Feature Implementation"
description: "Implement features with intelligent persona activation"
version: 1.0.0
category: workflow
complexity: standard

intents:
  primary:
    - "implement {feature}"
    - "create {component}"
    - "build {functionality}"
  keywords:
    - implement, create, build, develop, code, add
  patterns:
    - "^(implement|create|build) (a |an )?(?P<feature>.+)$"
    - "^add (?P<feature>.+) (feature|functionality)$"
  contexts:
    - component_development
    - feature_implementation

arguments:
  - name: feature
    type: string
    required: true
    description: "Feature to implement"
    infer_from: user_query

  - name: type
    type: enum
    values: [component, api, service, feature]
    required: false
    description: "Implementation type"
    infer_from: user_query
    default: auto-detect

  - name: framework
    type: enum
    values: [react, vue, angular, express, fastapi]
    required: false
    description: "Target framework"
    infer_from: project_context
    default: null

auto_trigger:
  enabled: true
  confidence_threshold: 0.85
  confirm_before_execution: true
  safety_checks:
    - confidence-check

mcp_servers:
  - context7
  - sequential
  - magic

personas:
  - architect
  - frontend
  - backend

requires_skills: []
optional_skills: [confidence-check]
---
```

### Example 2: Troubleshoot Skill

```yaml
---
name: troubleshoot
display_name: "Bug Troubleshooting"
description: "Diagnose and resolve issues with systematic debugging"
version: 1.0.0
category: workflow
complexity: enhanced

intents:
  primary:
    - "fix {issue}"
    - "troubleshoot {problem}"
    - "debug {bug}"
    - "resolve {error}"
  keywords:
    - fix, debug, troubleshoot, resolve, diagnose, error, bug, issue
  patterns:
    - "^(fix|debug|troubleshoot) (?P<issue>.+)$"
    - "^(?P<issue>.+) (not working|broken|failing)$"
    - "^why (is|does) (?P<issue>.+)$"
  contexts:
    - debugging
    - error_resolution

arguments:
  - name: issue
    type: string
    required: true
    description: "Issue to troubleshoot"
    infer_from: user_query

  - name: type
    type: enum
    values: [bug, performance, security, logic]
    required: false
    description: "Issue type"
    infer_from: user_query
    default: bug

  - name: depth
    type: enum
    values: [quick, standard, deep]
    required: false
    description: "Investigation depth"
    infer_from: learning
    default: standard

auto_trigger:
  enabled: true
  confidence_threshold: 0.85
  confirm_before_execution: true
  safety_checks: []

mcp_servers:
  - sequential
  - context7

personas:
  - debugger
  - analyst

requires_skills: []
optional_skills: []
---
```

### Example 3: PM Skill (High Complexity)

```yaml
---
name: pm
display_name: "PM Agent"
description: "Project Manager with intelligent optimization and validation"
version: 1.0.0
category: special
complexity: high

intents:
  primary:
    - "manage {task}"
    - "orchestrate {workflow}"
    - "plan {project}"
  keywords:
    - manage, orchestrate, plan, coordinate, pm, project
  patterns:
    - "^(manage|orchestrate|plan) (?P<task>.+)$"
  contexts:
    - project_management
    - workflow_orchestration

arguments:
  - name: task
    type: string
    required: true
    description: "Task to manage"
    infer_from: user_query

auto_trigger:
  enabled: true
  confidence_threshold: 0.90
  confirm_before_execution: true
  safety_checks:
    - confidence-check
    - architecture-compliance

mcp_servers:
  - sequential
  - serena
  - context7

personas:
  - pm
  - architect

requires_skills: []
optional_skills: [confidence-check]
---
```

## Validation Rules

### Required Fields
All skills MUST have:
- `name`
- `display_name`
- `description`
- `version`
- `category`
- `complexity`
- `intents.primary`
- `intents.keywords`
- `intents.patterns`
- `auto_trigger.enabled`
- `auto_trigger.confidence_threshold`
- `auto_trigger.confirm_before_execution`

### Validation Constraints

1. **name**: Must be kebab-case, unique, 3-30 characters
2. **version**: Must follow semantic versioning (X.Y.Z)
3. **category**: Must be one of defined values
4. **complexity**: Must be one of defined values
5. **intents.primary**: Must have at least 1 pattern
6. **intents.keywords**: Must have at least 2 keywords
7. **intents.patterns**: Must be valid Python regex
8. **confidence_threshold**: Must be 0.0-1.0
9. **arguments[].type**: If enum, must have `values`
10. **arguments[].infer_from**: Must be valid inference source

## Tooling

### Validation Tool

Use `src/superclaude/skills/validator.py` to validate skill metadata:

```bash
# Validate single skill
uv run python -m superclaude.skills.validator skills/implement/SKILL.md

# Validate all skills
uv run python -m superclaude.skills.validator skills/*/SKILL.md

# Auto-fix common issues
uv run python -m superclaude.skills.validator --fix skills/implement/SKILL.md
```

### Schema Linter

Use `src/superclaude/skills/linter.py` for best practices:

```bash
# Lint skill for best practices
uv run python -m superclaude.skills.linter skills/implement/SKILL.md

# Check all skills
uv run python -m superclaude.skills.linter skills/*/SKILL.md
```

## Migration Guide

### From Command to Skill

1. **Copy command markdown**: `cp plugins/superclaude/commands/implement.md skills/implement/SKILL.md`
2. **Add extended frontmatter**: Use schema above
3. **Define intent patterns**: Add primary, keywords, patterns
4. **Define arguments**: Specify schema for each argument
5. **Configure auto-trigger**: Set thresholds and safety checks
6. **Validate**: Run validator tool
7. **Test**: Verify intent detection works

### Testing Intent Detection

```python
from superclaude.intent import IntentClassifier

classifier = IntentClassifier(skills_dir="skills/")
matches = classifier.classify("implement user authentication")

assert matches[0].skill_name == "implement"
assert matches[0].confidence >= 0.85
assert matches[0].extracted_args["feature"] == "user authentication"
```

## Best Practices

### Intent Patterns

1. **Be specific**: "implement {feature}" better than "do {something}"
2. **Cover variations**: Include synonyms (create, build, develop)
3. **Use named groups**: `(?P<param>...)` for extraction
4. **Test patterns**: Validate with real user queries

### Keywords

1. **Be comprehensive**: Include all relevant synonyms
2. **Use lowercase**: Keywords are case-insensitive
3. **Avoid stopwords**: Skip "the", "a", "an"
4. **Order by importance**: Most important first

### Arguments

1. **Minimal required**: Only mark truly mandatory arguments as required
2. **Smart defaults**: Provide sensible defaults
3. **Inference sources**: Use most reliable source
4. **Validation**: Add regex patterns for critical arguments

### Confidence Thresholds

1. **Start high**: 0.90 for testing, lower gradually
2. **Monitor false positives**: Adjust based on feedback
3. **Context-specific**: Different thresholds per skill
4. **Safety-critical**: Higher thresholds for destructive operations

## Versioning

### Version Updates

- **MAJOR** (1.0.0 → 2.0.0): Breaking changes to schema or behavior
- **MINOR** (1.0.0 → 1.1.0): New features, backward-compatible
- **PATCH** (1.0.0 → 1.0.1): Bug fixes, documentation updates

### Compatibility

Skills must maintain backward compatibility within the same MAJOR version.

---

**Last Updated**: 2025-11-14
**Schema Version**: 1.0.0
**Maintainer**: SuperClaude Framework Team
