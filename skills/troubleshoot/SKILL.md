---
name: troubleshoot
display_name: "Issue Diagnosis and Resolution"
description: "Diagnose and resolve issues in code, builds, deployments, and system behavior"
version: 1.0.0
category: utility
complexity: basic

# Intent Detection
intents:
  primary: ["troubleshoot {issue}", "fix {problem}", "debug {error}", "resolve {bug}", "diagnose {issue}"]
  keywords: [
    # English
    troubleshoot, fix, debug, resolve, diagnose, error, bug, issue, problem, failure,
    # 한국어 (Korean) - 기본 키워드
    문제해결, 수정, 디버그, 해결, 진단, 오류, 버그, 문제, 실패,
    # 한국어 (Korean) - 자연어 표현
    고치다, 고쳐, 고쳐주세요, 해결하다, 해결해, 해결해주세요, 안되다, 안돼, 작동안함,
    # 日本語 (Japanese) - 基本キーワード
    トラブルシュート, 修正, デバッグ, 解決, 診断, エラー, バグ, 問題, 失敗,
    # 日本語 (Japanese) - 自然な表現
    直す, 直して, 直したい, 動かない, 動きません
  ]
  patterns: ["^(troubleshoot|fix|debug|resolve|diagnose) (?P<issue>.+)$", "^(?P<issue>.+) (not working|broken|failing|error)$", "^why (is|does) (?P<issue>.+)$"]
  contexts: [debugging, error_resolution, bug_fixing, issue_diagnosis]

# Arguments
arguments:
  - name: issue
    type: string
    required: true
    description: "Issue to troubleshoot"
    infer_from: user_query

  - name: type
    type: enum
    values: [bug, build, performance, deployment]
    required: false
    description: "Issue type"
    infer_from: user_query
    default: bug

  - name: trace
    type: bool
    required: false
    description: "Include detailed trace analysis"
    infer_from: user_query
    default: false

  - name: fix
    type: bool
    required: false
    description: "Auto-apply safe fixes"
    infer_from: user_query
    default: false

# Auto-Execution
auto_trigger:
  enabled: true
  confidence_threshold: 0.85
  confirm_before_execution: true
  safety_checks: [confidence-check]

# Dependencies
mcp_servers: []
personas: []
requires_skills: []
optional_skills: [confidence-check]
author: "SuperClaude Framework"
tags: [troubleshooting, debugging, diagnosis, resolution]
---

# /sc:troubleshoot - Issue Diagnosis and Resolution

## Triggers

- Code defects and runtime error investigation requests
- Build failure analysis and resolution needs
- Performance issue diagnosis and optimization requirements
- Deployment problem analysis and system behavior debugging

## Usage

```
/sc:troubleshoot [issue] [--type bug|build|performance|deployment] [--trace] [--fix]
```

## Behavioral Flow

1. **Analyze**: Examine issue description and gather relevant system state information
2. **Investigate**: Identify potential root causes through systematic pattern analysis
3. **Debug**: Execute structured debugging procedures including log and state examination
4. **Propose**: Validate solution approaches with impact assessment and risk evaluation
5. **Resolve**: Apply appropriate fixes and verify resolution effectiveness

Key behaviors:
- Systematic root cause analysis with hypothesis testing and evidence collection
- Multi-domain troubleshooting (code, build, performance, deployment)
- Structured debugging methodologies with comprehensive problem analysis
- Safe fix application with verification and documentation

## Tool Coordination

- **Read**: Log analysis and system state examination
- **Bash**: Diagnostic command execution and system investigation
- **Grep**: Error pattern detection and log analysis
- **Write**: Diagnostic reports and resolution documentation

## Key Patterns

- **Bug Investigation**: Error analysis → stack trace examination → code inspection → fix validation
- **Build Troubleshooting**: Build log analysis → dependency checking → configuration validation
- **Performance Diagnosis**: Metrics analysis → bottleneck identification → optimization recommendations
- **Deployment Issues**: Environment analysis → configuration verification → service validation

## Examples

### Code Bug Investigation

```
/sc:troubleshoot "Null pointer exception in user service" --type bug --trace
# Systematic analysis of error context and stack traces
# Identifies root cause and provides targeted fix recommendations
```

### Build Failure Analysis

```
/sc:troubleshoot "TypeScript compilation errors" --type build --fix
# Analyzes build logs and TypeScript configuration
# Automatically applies safe fixes for common compilation issues
```

### Performance Issue Diagnosis

```
/sc:troubleshoot "API response times degraded" --type performance
# Performance metrics analysis and bottleneck identification
# Provides optimization recommendations and monitoring guidance
```

### Deployment Problem Resolution

```
/sc:troubleshoot "Service not starting in production" --type deployment --trace
# Environment and configuration analysis
# Systematic verification of deployment requirements and dependencies
```

## Boundaries

**Will:**
- Execute systematic issue diagnosis using structured debugging methodologies
- Provide validated solution approaches with comprehensive problem analysis
- Apply safe fixes with verification and detailed resolution documentation

**Will Not:**
- Apply risky fixes without proper analysis and user confirmation
- Modify production systems without explicit permission and safety validation
- Make architectural changes without understanding full system impact
