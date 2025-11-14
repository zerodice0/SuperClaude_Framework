---
name: analyze
display_name: "Code Analysis and Quality Assessment"
description: "Comprehensive code analysis across quality, security, performance, and architecture domains"
version: 1.0.0
category: utility
complexity: basic

# Intent Detection
intents:
  primary: ["analyze {target}", "assess {code}", "review {codebase}", "audit {system}"]
  keywords: [
    # English
    analyze, assess, review, audit, quality, security, performance, architecture,
    # 한국어 (Korean) - 기본 키워드
    분석, 평가, 검토, 감사, 품질, 보안, 성능, 아키텍처,
    # 한국어 (Korean) - 자연어 표현
    분석하다, 분석해, 분석해주세요, 검토하다, 검토해, 검토해주세요, 확인하다, 확인해,
    # 日本語 (Japanese) - 基本キーワード
    分析, 評価, レビュー, 監査, 品質, セキュリティ, パフォーマンス, アーキテクチャ,
    # 日本語 (Japanese) - 自然な表現
    分析する, 分析して, 確認する, 確認して, チェック
  ]
  patterns: ["^(analyze|assess|review|audit) (?P<target>.+)?$", "^code (analysis|assessment|review)( of)?( (?P<target>.+))?$"]
  contexts: [code_analysis, quality_assessment, security_audit, performance_review]

# Arguments
arguments:
  - name: target
    type: string
    required: false
    description: "Target to analyze (default: entire project)"
    infer_from: user_query
    default: "."

  - name: focus
    type: enum
    values: [quality, security, performance, architecture, all]
    required: false
    description: "Analysis focus area"
    infer_from: user_query
    default: all

  - name: depth
    type: enum
    values: [quick, normal, deep]
    required: false
    description: "Analysis depth"
    infer_from: user_query
    default: normal

  - name: format
    type: enum
    values: [text, json, report, html]
    required: false
    description: "Output format"
    infer_from: user_query
    default: text

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
tags: [analysis, quality, security, performance, architecture]
---

# /sc:analyze - Code Analysis and Quality Assessment

## Triggers

- Code quality assessment requests for projects or specific components
- Security vulnerability scanning and compliance validation needs
- Performance bottleneck identification and optimization planning
- Architecture review and technical debt assessment requirements

## Usage

```
/sc:analyze [target] [--focus quality|security|performance|architecture] [--depth quick|deep] [--format text|json|report]
```

## Behavioral Flow

1. **Discover**: Categorize source files using language detection and project analysis
2. **Scan**: Apply domain-specific analysis techniques and pattern matching
3. **Evaluate**: Generate prioritized findings with severity ratings and impact assessment
4. **Recommend**: Create actionable recommendations with implementation guidance
5. **Report**: Present comprehensive analysis with metrics and improvement roadmap

Key behaviors:
- Multi-domain analysis combining static analysis and heuristic evaluation
- Intelligent file discovery and language-specific pattern recognition
- Severity-based prioritization of findings and recommendations
- Comprehensive reporting with metrics, trends, and actionable insights

## Tool Coordination

- **Glob**: File discovery and project structure analysis
- **Grep**: Pattern analysis and code search operations
- **Read**: Source code inspection and configuration analysis
- **Bash**: External analysis tool execution and validation
- **Write**: Report generation and metrics documentation

## Key Patterns

- **Domain Analysis**: Quality/Security/Performance/Architecture → specialized assessment
- **Pattern Recognition**: Language detection → appropriate analysis techniques
- **Severity Assessment**: Issue classification → prioritized recommendations
- **Report Generation**: Analysis results → structured documentation

## Examples

### Comprehensive Project Analysis

```
/sc:analyze
# Multi-domain analysis of entire project
# Generates comprehensive report with key findings and roadmap
```

### Focused Security Assessment

```
/sc:analyze src/auth --focus security --depth deep
# Deep security analysis of authentication components
# Vulnerability assessment with detailed remediation guidance
```

### Performance Optimization Analysis

```
/sc:analyze --focus performance --format report
# Performance bottleneck identification
# Generates HTML report with optimization recommendations
```

### Quick Quality Check

```
/sc:analyze src/components --focus quality --depth quick
# Rapid quality assessment of component directory
# Identifies code smells and maintainability issues
```

## Boundaries

**Will:**
- Perform comprehensive static code analysis across multiple domains
- Generate severity-rated findings with actionable recommendations
- Provide detailed reports with metrics and improvement guidance

**Will Not:**
- Execute dynamic analysis requiring code compilation or runtime
- Modify source code or apply fixes without explicit user consent
- Analyze external dependencies beyond import and usage patterns
