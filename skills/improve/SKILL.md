---
name: improve
display_name: "Code Improvement"
description: "Apply systematic improvements to code quality, performance, and maintainability"
version: 1.0.0
category: workflow
complexity: standard

# Intent Detection
intents:
  primary: ["improve {target}", "optimize {code}", "refactor {module}", "enhance {quality}"]
  keywords: [
    # English
    improve, optimize, refactor, enhance, quality, performance, maintainability, cleanup,
    # 한국어 (Korean)
    개선, 최적화, 리팩토링, 향상, 품질, 성능, 유지보수성, 정리,
    # 日本語 (Japanese)
    改善, 最適化, リファクタリング, 強化, 品質, パフォーマンス, 保守性, クリーンアップ
  ]
  patterns: ["^(improve|optimize|refactor|enhance) (?P<target>.+)$", "^make (?P<target>.+) (better|faster|cleaner)$"]
  contexts: [code_improvement, performance_optimization, refactoring, quality_enhancement]

# Arguments
arguments:
  - name: target
    type: string
    required: true
    description: "Target code or module to improve"
    infer_from: user_query

  - name: type
    type: enum
    values: [quality, performance, maintainability, style, security]
    required: false
    description: "Improvement type"
    infer_from: user_query
    default: quality

  - name: safe
    type: bool
    required: false
    description: "Safe mode with rollback capabilities"
    infer_from: user_query
    default: true

  - name: interactive
    type: bool
    required: false
    description: "Interactive mode for complex decisions"
    infer_from: user_query
    default: false

# Auto-Execution
auto_trigger:
  enabled: true
  confidence_threshold: 0.85
  confirm_before_execution: true
  safety_checks: [confidence-check]

# Dependencies
mcp_servers: [sequential, context7]
personas: [architect, performance, quality, security]
requires_skills: []
optional_skills: [confidence-check]
author: "SuperClaude Framework"
tags: [improvement, optimization, refactoring, quality]
---

# /sc:improve - Code Improvement

## Triggers

- Code quality enhancement and refactoring requests
- Performance optimization and bottleneck resolution needs
- Maintainability improvements and technical debt reduction
- Best practices application and coding standards enforcement

## Usage

```
/sc:improve [target] [--type quality|performance|maintainability|style] [--safe] [--interactive]
```

## Behavioral Flow

1. **Analyze**: Examine codebase for improvement opportunities and quality issues
2. **Plan**: Choose improvement approach and activate relevant personas for expertise
3. **Execute**: Apply systematic improvements with domain-specific best practices
4. **Validate**: Ensure improvements preserve functionality and meet quality standards
5. **Document**: Generate improvement summary and recommendations for future work

Key behaviors:
- Multi-persona coordination (architect, performance, quality, security) based on improvement type
- Framework-specific optimization via Context7 integration for best practices
- Systematic analysis via Sequential MCP for complex multi-component improvements
- Safe refactoring with comprehensive validation and rollback capabilities

## MCP Integration

- **Sequential MCP**: Auto-activated for complex multi-step improvement analysis and planning
- **Context7 MCP**: Framework-specific best practices and optimization patterns
- **Persona Coordination**: Architect (structure), Performance (speed), Quality (maintainability), Security (safety)

## Tool Coordination

- **Read/Grep/Glob**: Code analysis and improvement opportunity identification
- **Edit/MultiEdit**: Safe code modification and systematic refactoring
- **TodoWrite**: Progress tracking for complex multi-file improvement operations
- **Task**: Delegation for large-scale improvement workflows requiring systematic coordination

## Key Patterns

- **Quality Improvement**: Code analysis → technical debt identification → refactoring application
- **Performance Optimization**: Profiling analysis → bottleneck identification → optimization implementation
- **Maintainability Enhancement**: Structure analysis → complexity reduction → documentation improvement
- **Security Hardening**: Vulnerability analysis → security pattern application → validation verification

## Examples

### Code Quality Enhancement

```
/sc:improve src/ --type quality --safe
# Systematic quality analysis with safe refactoring application
# Improves code structure, reduces technical debt, enhances readability
```

### Performance Optimization

```
/sc:improve api-endpoints --type performance --interactive
# Performance persona analyzes bottlenecks and optimization opportunities
# Interactive guidance for complex performance improvement decisions
```

### Maintainability Improvements

```
/sc:improve legacy-modules --type maintainability --preview
# Architect persona analyzes structure and suggests maintainability improvements
# Preview mode shows changes before application for review
```

### Security Hardening

```
/sc:improve auth-service --type security --validate
# Security persona identifies vulnerabilities and applies security patterns
# Comprehensive validation ensures security improvements are effective
```

## Boundaries

**Will:**
- Apply systematic improvements with domain-specific expertise and validation
- Provide comprehensive analysis with multi-persona coordination and best practices
- Execute safe refactoring with rollback capabilities and quality preservation

**Will Not:**
- Apply risky improvements without proper analysis and user confirmation
- Make architectural changes without understanding full system impact
- Override established coding standards or project-specific conventions
