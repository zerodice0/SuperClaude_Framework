---
name: design
display_name: "System and Component Design"
description: "Design system architecture, APIs, and component interfaces with comprehensive specifications"
version: 1.0.0
category: utility
complexity: basic

# Intent Detection
intents:
  primary: ["design {target}", "create design {component}", "architect {system}", "plan {architecture}", "specify {interface}"]
  keywords: [
    # English
    design, architecture, api, interface, component, database, schema, system, specification, blueprint, structure,
    # 한국어 (Korean)
    디자인, 설계, 아키텍처, API, 인터페이스, 컴포넌트, 데이터베이스, 스키마, 시스템, 명세, 청사진, 구조,
    # 日本語 (Japanese)
    デザイン, 設計, アーキテクチャ, API, インターフェース, コンポーネント, データベース, スキーマ, システム, 仕様, 設計図, 構造
  ]
  patterns: ["^(design|architect|plan|specify) (?P<target>.+)$", "^create (design|architecture|spec) for (?P<target>.+)$"]
  contexts: [design, architecture, planning, specification]

# Arguments
arguments:
  - name: target
    type: string
    required: true
    description: "System, component, or interface to design"
    infer_from: user_query

  - name: type
    type: enum
    values: [architecture, api, component, database]
    required: false
    description: "Design type"
    infer_from: user_query
    default: architecture

  - name: format
    type: enum
    values: [diagram, spec, code]
    required: false
    description: "Output format"
    infer_from: user_query
    default: spec

# Auto-Execution
auto_trigger:
  enabled: true
  confidence_threshold: 0.85
  confirm_before_execution: true
  safety_checks: []

# Dependencies
mcp_servers: []
personas: []
requires_skills: []
optional_skills: []
author: "SuperClaude Framework"
tags: [design, architecture, api, specification, planning]
---

# /sc:design - System and Component Design

## Triggers

- Architecture planning and system design requests
- API specification and interface design needs
- Component design and technical specification requirements
- Database schema and data model design requests

## Usage

```
/sc:design [target] [--type architecture|api|component|database] [--format diagram|spec|code]
```

## Behavioral Flow

1. **Analyze**: Examine target requirements and existing system context
2. **Plan**: Define design approach and structure based on type and format
3. **Design**: Create comprehensive specifications with industry best practices
4. **Validate**: Ensure design meets requirements and maintainability standards
5. **Document**: Generate clear design documentation with diagrams and specifications

Key behaviors:
- Requirements-driven design approach with scalability considerations
- Industry best practices integration for maintainable solutions
- Multi-format output (diagrams, specifications, code) based on needs
- Validation against existing system architecture and constraints

## Tool Coordination

- **Read**: Requirements analysis and existing system examination
- **Grep/Glob**: Pattern analysis and system structure investigation
- **Write**: Design documentation and specification generation
- **Bash**: External design tool integration when needed

## Key Patterns

- **Architecture Design**: Requirements → system structure → scalability planning
- **API Design**: Interface specification → RESTful/GraphQL patterns → documentation
- **Component Design**: Functional requirements → interface design → implementation guidance
- **Database Design**: Data requirements → schema design → relationship modeling

## Examples

### System Architecture Design

```
/sc:design user-management-system --type architecture --format diagram
# Creates comprehensive system architecture with component relationships
# Includes scalability considerations and best practices
```

### API Specification Design

```
/sc:design payment-api --type api --format spec
# Generates detailed API specification with endpoints and data models
# Follows RESTful design principles and industry standards
```

### Component Interface Design

```
/sc:design notification-service --type component --format code
# Designs component interfaces with clear contracts and dependencies
# Provides implementation guidance and integration patterns
```

### Database Schema Design

```
/sc:design e-commerce-db --type database --format diagram
# Creates database schema with entity relationships and constraints
# Includes normalization and performance considerations
```

## Boundaries

**Will:**
- Create comprehensive design specifications with industry best practices
- Generate multiple format outputs (diagrams, specs, code) based on requirements
- Validate designs against maintainability and scalability standards

**Will Not:**
- Generate actual implementation code (use /sc:implement for implementation)
- Modify existing system architecture without explicit design approval
- Create designs that violate established architectural constraints
