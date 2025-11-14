---
name: task
display_name: "Enhanced Task Management"
description: "Execute complex tasks with intelligent workflow management and delegation"
version: 1.0.0
category: special
complexity: advanced

# Intent Detection
intents:
  primary: ["task {action} {target}", "execute {task}", "manage {complex_task}", "coordinate {multi_task}", "orchestrate {workflow}"]
  keywords: [task, execute, manage, coordinate, orchestrate, complex, multi-agent, workflow, delegation, systematic]
  patterns: ["^(task|execute|manage|coordinate) (?P<action>create|execute|analyze) (?P<target>.+)$", "^orchestrate (?P<target>.+) (workflow|system|platform)$", "^(?P<target>.+) (requires|needs) (multi-agent|coordination|delegation)$"]
  contexts: [complex_task_execution, multi_agent_coordination, workflow_management, cross_session_persistence]

# Arguments
arguments:
  - name: action
    type: enum
    values: [create, execute, analyze, coordinate, validate]
    required: true
    description: "Task action to perform"
    infer_from: user_query

  - name: target
    type: string
    required: true
    description: "Target task or workflow"
    infer_from: user_query

  - name: strategy
    type: enum
    values: [systematic, agile, enterprise]
    required: false
    description: "Execution strategy"
    infer_from: user_query
    default: systematic

  - name: parallel
    type: bool
    required: false
    description: "Enable parallel execution"
    infer_from: user_query
    default: false

  - name: delegate
    type: bool
    required: false
    description: "Enable intelligent delegation"
    infer_from: user_query
    default: true

# Auto-Execution
auto_trigger:
  enabled: true
  confidence_threshold: 0.88
  confirm_before_execution: true
  safety_checks: [confidence-check]

# Dependencies
mcp_servers: [sequential, context7, magic, playwright, morphllm, serena]
personas: [architect, analyzer, frontend, backend, security, devops, project-manager]
requires_skills: []
optional_skills: [confidence-check]
author: "SuperClaude Framework"
tags: [task-management, multi-agent, workflow, delegation, coordination]
---

# /sc:task - Enhanced Task Management

## Triggers

- Complex tasks requiring multi-agent coordination and delegation
- Projects needing structured workflow management and cross-session persistence
- Operations requiring intelligent MCP server routing and domain expertise
- Tasks benefiting from systematic execution and progressive enhancement

## Usage

```
/sc:task [action] [target] [--strategy systematic|agile|enterprise] [--parallel] [--delegate]
```

## Behavioral Flow

1. **Analyze**: Parse task requirements and determine optimal execution strategy
2. **Delegate**: Route to appropriate MCP servers and activate relevant personas
3. **Coordinate**: Execute tasks with intelligent workflow management and parallel processing
4. **Validate**: Apply quality gates and comprehensive task completion verification
5. **Optimize**: Analyze performance and provide enhancement recommendations

Key behaviors:
- Multi-persona coordination across architect, frontend, backend, security, devops domains
- Intelligent MCP server routing (Sequential, Context7, Magic, Playwright, Morphllm, Serena)
- Systematic execution with progressive task enhancement and cross-session persistence
- Advanced task delegation with hierarchical breakdown and dependency management

## MCP Integration

- **Sequential MCP**: Complex multi-step task analysis and systematic execution planning
- **Context7 MCP**: Framework-specific patterns and implementation best practices
- **Magic MCP**: UI/UX task coordination and design system integration
- **Playwright MCP**: Testing workflow integration and validation automation
- **Morphllm MCP**: Large-scale task transformation and pattern-based optimization
- **Serena MCP**: Cross-session task persistence and project memory management

## Tool Coordination

- **TodoWrite**: Hierarchical task breakdown and progress tracking across Epic → Story → Task levels
- **Task**: Advanced delegation for complex multi-agent coordination and sub-task management
- **Read/Write/Edit**: Task documentation and implementation coordination
- **sequentialthinking**: Structured reasoning for complex task dependency analysis

## Key Patterns

- **Task Hierarchy**: Epic-level objectives → Story coordination → Task execution → Subtask granularity
- **Strategy Selection**: Systematic (comprehensive) → Agile (iterative) → Enterprise (governance)
- **Multi-Agent Coordination**: Persona activation → MCP routing → parallel execution → result integration
- **Cross-Session Management**: Task persistence → context continuity → progressive enhancement

## Examples

### Complex Feature Development

```
/sc:task create "enterprise authentication system" --strategy systematic --parallel
# Comprehensive task breakdown with multi-domain coordination
# Activates architect, security, backend, frontend personas
```

### Agile Sprint Coordination

```
/sc:task execute "feature backlog" --strategy agile --delegate
# Iterative task execution with intelligent delegation
# Cross-session persistence for sprint continuity
```

### Multi-Domain Integration

```
/sc:task execute "microservices platform" --strategy enterprise --parallel
# Enterprise-scale coordination with compliance validation
# Parallel execution across multiple technical domains
```

## Boundaries

**Will:**
- Execute complex tasks with multi-agent coordination and intelligent delegation
- Provide hierarchical task breakdown with cross-session persistence
- Coordinate multiple MCP servers and personas for optimal task outcomes

**Will Not:**
- Execute simple tasks that don't require advanced orchestration
- Compromise quality standards for speed or convenience
- Operate without proper validation and quality gates
