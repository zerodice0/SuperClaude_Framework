---
name: workflow
display_name: "Implementation Workflow Generator"
description: "Generate structured implementation workflows from PRDs and feature requirements"
version: 1.0.0
category: orchestration
complexity: advanced

# Intent Detection
intents:
  primary: ["workflow {target}", "generate workflow {feature}", "create implementation plan {prd}", "plan {feature} workflow"]
  keywords: [
    # English
    workflow, generate, plan, implementation, prd, feature, specification, orchestration, systematic,
    # 한국어 (Korean)
    워크플로우, 생성, 계획, 구현, PRD, 기능, 명세, 오케스트레이션, 체계적,
    # 日本語 (Japanese)
    ワークフロー, 生成, 計画, 実装, PRD, 機能, 仕様, オーケストレーション, 体系的
  ]
  patterns: ["^(workflow|generate workflow|plan) (?P<target>.+)$", "^create (implementation|execution) (plan|workflow) (for |from )?(?P<target>.+)$", "^(?P<target>.+\\.md) (workflow|implementation)$"]
  contexts: [prd_analysis, workflow_generation, implementation_planning, multi_domain_coordination]

# Arguments
arguments:
  - name: target
    type: string
    required: true
    description: "PRD file or feature description"
    infer_from: user_query

  - name: strategy
    type: enum
    values: [systematic, agile, enterprise]
    required: false
    description: "Workflow generation strategy"
    infer_from: user_query
    default: systematic

  - name: depth
    type: enum
    values: [shallow, normal, deep]
    required: false
    description: "Analysis depth level"
    infer_from: user_query
    default: normal

  - name: parallel
    type: bool
    required: false
    description: "Enable parallel task coordination"
    infer_from: user_query
    default: false

  - name: validate
    type: bool
    required: false
    description: "Enable comprehensive validation"
    infer_from: user_query
    default: true

# Auto-Execution
auto_trigger:
  enabled: true
  confidence_threshold: 0.87
  confirm_before_execution: true
  safety_checks: [confidence-check]

# Dependencies
mcp_servers: [sequential, context7, magic, playwright, morphllm, serena]
personas: [architect, analyzer, frontend, backend, security, devops, project-manager]
requires_skills: []
optional_skills: [confidence-check]
author: "SuperClaude Framework"
tags: [workflow, prd, planning, orchestration, implementation]
---

# /sc:workflow - Implementation Workflow Generator

## Triggers

- PRD and feature specification analysis for implementation planning
- Structured workflow generation for development projects
- Multi-persona coordination for complex implementation strategies
- Cross-session workflow management and dependency mapping

## Usage

```
/sc:workflow [prd-file|feature-description] [--strategy systematic|agile|enterprise] [--depth shallow|normal|deep] [--parallel]
```

## Behavioral Flow

1. **Analyze**: Parse PRD and feature specifications to understand implementation requirements
2. **Plan**: Generate comprehensive workflow structure with dependency mapping and task orchestration
3. **Coordinate**: Activate multiple personas for domain expertise and implementation strategy
4. **Execute**: Create structured step-by-step workflows with automated task coordination
5. **Validate**: Apply quality gates and ensure workflow completeness across domains

Key behaviors:
- Multi-persona orchestration across architecture, frontend, backend, security, and devops domains
- Advanced MCP coordination with intelligent routing for specialized workflow analysis
- Systematic execution with progressive workflow enhancement and parallel processing
- Cross-session workflow management with comprehensive dependency tracking

## MCP Integration

- **Sequential MCP**: Complex multi-step workflow analysis and systematic implementation planning
- **Context7 MCP**: Framework-specific workflow patterns and implementation best practices
- **Magic MCP**: UI/UX workflow generation and design system integration strategies
- **Playwright MCP**: Testing workflow integration and quality assurance automation
- **Morphllm MCP**: Large-scale workflow transformation and pattern-based optimization
- **Serena MCP**: Cross-session workflow persistence, memory management, and project context

## Tool Coordination

- **Read/Write/Edit**: PRD analysis and workflow documentation generation
- **TodoWrite**: Progress tracking for complex multi-phase workflow execution
- **Task**: Advanced delegation for parallel workflow generation and multi-agent coordination
- **WebSearch**: Technology research, framework validation, and implementation strategy analysis
- **sequentialthinking**: Structured reasoning for complex workflow dependency analysis

## Key Patterns

- **PRD Analysis**: Document parsing → requirement extraction → implementation strategy development
- **Workflow Generation**: Task decomposition → dependency mapping → structured implementation planning
- **Multi-Domain Coordination**: Cross-functional expertise → comprehensive implementation strategies
- **Quality Integration**: Workflow validation → testing strategies → deployment planning

## Examples

### Systematic PRD Workflow

```
/sc:workflow docs/PRD/feature-spec.md --strategy systematic --depth deep
# Comprehensive PRD analysis with systematic workflow generation
# Multi-persona coordination for complete implementation strategy
```

### Agile Feature Workflow

```
/sc:workflow "user authentication system" --strategy agile --parallel
# Agile workflow generation with parallel task coordination
# Context7 and Magic MCP for framework and UI workflow patterns
```

### Enterprise Implementation Planning

```
/sc:workflow enterprise-prd.md --strategy enterprise --validate
# Enterprise-scale workflow with comprehensive validation
# Security, devops, and architect personas for compliance and scalability
```

### Cross-Session Workflow Management

```
/sc:workflow project-brief.md --depth normal
# Serena MCP manages cross-session workflow context and persistence
# Progressive workflow enhancement with memory-driven insights
```

## Boundaries

**Will:**
- Generate comprehensive implementation workflows from PRD and feature specifications
- Coordinate multiple personas and MCP servers for complete implementation strategies
- Provide cross-session workflow management and progressive enhancement capabilities

**Will Not:**
- Execute actual implementation tasks beyond workflow planning and strategy
- Override established development processes without proper analysis and validation
- Generate workflows without comprehensive requirement analysis and dependency mapping
