---
name: brainstorm
display_name: "Interactive Requirements Discovery"
description: "Interactive requirements discovery through Socratic dialogue and systematic exploration"
version: 1.0.0
category: orchestration
complexity: advanced

# Intent Detection
intents:
  primary: ["brainstorm {topic}", "explore {idea}", "discover requirements {feature}", "validate {concept}", "ideate {project}"]
  keywords: [brainstorm, explore, discover, ideate, validate, requirements, concept, idea, feasibility, exploration, discovery, socratic]
  patterns: ["^(brainstorm|explore|discover|ideate|validate) (?P<topic>.+)$", "^requirements (discovery|exploration|validation) for (?P<topic>.+)$"]
  contexts: [brainstorming, requirements_discovery, concept_validation, ideation]

# Arguments
arguments:
  - name: topic
    type: string
    required: true
    description: "Topic or idea to brainstorm"
    infer_from: user_query

  - name: strategy
    type: enum
    values: [systematic, agile, enterprise]
    required: false
    description: "Brainstorming strategy"
    infer_from: user_query
    default: systematic

  - name: depth
    type: enum
    values: [shallow, normal, deep]
    required: false
    description: "Exploration depth"
    infer_from: user_query
    default: normal

  - name: parallel
    type: bool
    required: false
    description: "Enable parallel exploration paths"
    infer_from: user_query
    default: false

# Auto-Execution
auto_trigger:
  enabled: true
  confidence_threshold: 0.87
  confirm_before_execution: true
  safety_checks: []

# Dependencies
mcp_servers: [sequential, context7, magic, playwright, morphllm, serena]
personas: [architect, analyzer, frontend, backend, security, devops, project-manager]
requires_skills: []
optional_skills: []
author: "SuperClaude Framework"
tags: [brainstorming, discovery, exploration, requirements, ideation]
---

# /sc:brainstorm - Interactive Requirements Discovery

## Triggers

- Ambiguous project ideas requiring structured exploration
- Requirements discovery and specification development needs
- Concept validation and feasibility assessment requests
- Cross-session brainstorming and iterative refinement scenarios

## Usage

```
/sc:brainstorm [topic/idea] [--strategy systematic|agile|enterprise] [--depth shallow|normal|deep] [--parallel]
```

## Behavioral Flow

1. **Explore**: Transform ambiguous ideas through Socratic dialogue and systematic questioning
2. **Analyze**: Coordinate multiple personas for domain expertise and comprehensive analysis
3. **Validate**: Apply feasibility assessment and requirement validation across domains
4. **Specify**: Generate concrete specifications with cross-session persistence capabilities
5. **Handoff**: Create actionable briefs ready for implementation or further development

Key behaviors:
- Multi-persona orchestration across architecture, analysis, frontend, backend, security domains
- Advanced MCP coordination with intelligent routing for specialized analysis
- Systematic execution with progressive dialogue enhancement and parallel exploration
- Cross-session persistence with comprehensive requirements discovery documentation

## MCP Integration

- **Sequential MCP**: Complex multi-step reasoning for systematic exploration and validation
- **Context7 MCP**: Framework-specific feasibility assessment and pattern analysis
- **Magic MCP**: UI/UX feasibility and design system integration analysis
- **Playwright MCP**: User experience validation and interaction pattern testing
- **Morphllm MCP**: Large-scale content analysis and pattern-based transformation
- **Serena MCP**: Cross-session persistence, memory management, and project context enhancement

## Tool Coordination

- **Read/Write/Edit**: Requirements documentation and specification generation
- **TodoWrite**: Progress tracking for complex multi-phase exploration
- **Task**: Advanced delegation for parallel exploration paths and multi-agent coordination
- **WebSearch**: Market research, competitive analysis, and technology validation
- **sequentialthinking**: Structured reasoning for complex requirements analysis

## Key Patterns

- **Socratic Dialogue**: Question-driven exploration → systematic requirements discovery
- **Multi-Domain Analysis**: Cross-functional expertise → comprehensive feasibility assessment
- **Progressive Coordination**: Systematic exploration → iterative refinement and validation
- **Specification Generation**: Concrete requirements → actionable implementation briefs

## Examples

### Systematic Product Discovery

```
/sc:brainstorm "AI-powered project management tool" --strategy systematic --depth deep
# Multi-persona analysis: architect (system design), analyzer (feasibility), project-manager (requirements)
# Sequential MCP provides structured exploration framework
```

### Agile Feature Exploration

```
/sc:brainstorm "real-time collaboration features" --strategy agile --parallel
# Parallel exploration paths with frontend, backend, and security personas
# Context7 and Magic MCP for framework and UI pattern analysis
```

### Enterprise Solution Validation

```
/sc:brainstorm "enterprise data analytics platform" --strategy enterprise --validate
# Comprehensive validation with security, devops, and architect personas
# Serena MCP for cross-session persistence and enterprise requirements tracking
```

### Cross-Session Refinement

```
/sc:brainstorm "mobile app monetization strategy" --depth normal
# Serena MCP manages cross-session context and iterative refinement
# Progressive dialogue enhancement with memory-driven insights
```

## Boundaries

**Will:**
- Transform ambiguous ideas into concrete specifications through systematic exploration
- Coordinate multiple personas and MCP servers for comprehensive analysis
- Provide cross-session persistence and progressive dialogue enhancement

**Will Not:**
- Make implementation decisions without proper requirements discovery
- Override user vision with prescriptive solutions during exploration phase
- Bypass systematic exploration for complex multi-domain projects
