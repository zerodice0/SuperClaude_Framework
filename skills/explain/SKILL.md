---
name: explain
display_name: "Code and Concept Explanation"
description: "Provide clear explanations of code, concepts, and system behavior with educational clarity"
version: 1.0.0
category: workflow
complexity: standard

# Intent Detection
intents:
  primary: ["explain {target}", "what is {concept}", "how does {code} work", "describe {system}", "clarify {topic}"]
  keywords: [explain, describe, clarify, how, what, why, works, understand, learn, educate, teach, breakdown]
  patterns: ["^(explain|describe|clarify|breakdown) (?P<target>.+)$", "^(what is|how does|why does) (?P<target>.+)( work)?$"]
  contexts: [learning, education, understanding, documentation]

# Arguments
arguments:
  - name: target
    type: string
    required: true
    description: "Code, concept, or system to explain"
    infer_from: user_query

  - name: level
    type: enum
    values: [basic, intermediate, advanced]
    required: false
    description: "Explanation depth level"
    infer_from: user_query
    default: basic

  - name: format
    type: enum
    values: [text, examples, interactive]
    required: false
    description: "Explanation format"
    infer_from: user_query
    default: text

  - name: context
    type: string
    required: false
    description: "Domain context for targeted explanation"
    infer_from: user_query

# Auto-Execution
auto_trigger:
  enabled: true
  confidence_threshold: 0.85
  confirm_before_execution: true
  safety_checks: []

# Dependencies
mcp_servers: [sequential, context7]
personas: [educator, architect, security]
requires_skills: []
optional_skills: []
author: "SuperClaude Framework"
tags: [explanation, education, learning, documentation]
---

# /sc:explain - Code and Concept Explanation

## Triggers

- Code understanding and documentation requests for complex functionality
- System behavior explanation needs for architectural components
- Educational content generation for knowledge transfer
- Framework-specific concept clarification requirements

## Usage

```
/sc:explain [target] [--level basic|intermediate|advanced] [--format text|examples|interactive] [--context domain]
```

## Behavioral Flow

1. **Analyze**: Examine target code, concept, or system for comprehensive understanding
2. **Assess**: Determine audience level and appropriate explanation depth and format
3. **Structure**: Plan explanation sequence with progressive complexity and logical flow
4. **Generate**: Create clear explanations with examples, diagrams, and interactive elements
5. **Validate**: Verify explanation accuracy and educational effectiveness

Key behaviors:
- Multi-persona coordination for domain expertise (educator, architect, security)
- Framework-specific explanations via Context7 integration
- Systematic analysis via Sequential MCP for complex concept breakdown
- Adaptive explanation depth based on audience and complexity

## MCP Integration

- **Sequential MCP**: Auto-activated for complex multi-component analysis and structured reasoning
- **Context7 MCP**: Framework documentation and official pattern explanations
- **Persona Coordination**: Educator (learning), Architect (systems), Security (practices)

## Tool Coordination

- **Read/Grep/Glob**: Code analysis and pattern identification for explanation content
- **TodoWrite**: Progress tracking for complex multi-part explanations
- **Task**: Delegation for comprehensive explanation workflows requiring systematic breakdown

## Key Patterns

- **Progressive Learning**: Basic concepts → intermediate details → advanced implementation
- **Framework Integration**: Context7 documentation → accurate official patterns and practices
- **Multi-Domain Analysis**: Technical accuracy + educational clarity + security awareness
- **Interactive Explanation**: Static content → examples → interactive exploration

## Examples

### Basic Code Explanation

```
/sc:explain authentication.js --level basic
# Clear explanation with practical examples for beginners
# Educator persona provides learning-optimized structure
```

### Framework Concept Explanation

```
/sc:explain react-hooks --level intermediate --context react
# Context7 integration for official React documentation patterns
# Structured explanation with progressive complexity
```

### System Architecture Explanation

```
/sc:explain microservices-system --level advanced --format interactive
# Architect persona explains system design and patterns
# Interactive exploration with Sequential analysis breakdown
```

### Security Concept Explanation

```
/sc:explain jwt-authentication --context security --level basic
# Security persona explains authentication concepts and best practices
# Framework-agnostic security principles with practical examples
```

## Boundaries

**Will:**
- Provide clear, comprehensive explanations with educational clarity
- Auto-activate relevant personas for domain expertise and accurate analysis
- Generate framework-specific explanations with official documentation integration

**Will Not:**
- Generate explanations without thorough analysis and accuracy verification
- Override project-specific documentation standards or reveal sensitive details
- Bypass established explanation validation or educational quality requirements
