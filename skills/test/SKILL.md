---
name: test
display_name: "Testing and Quality Assurance"
description: "Execute tests with coverage analysis and automated quality reporting"
version: 1.0.0
category: utility
complexity: enhanced

# Intent Detection
intents:
  primary: ["test {target}", "run tests", "execute tests", "test coverage", "run test suite"]
  keywords: [
    # English
    test, tests, testing, coverage, quality, qa, validate, verify, unit, integration, e2e, spec, runner, jest, vitest, mocha,
    # 한국어 (Korean)
    테스트, 커버리지, 품질, QA, 검증, 확인, 유닛, 통합, E2E, 스펙, 러너,
    # 日本語 (Japanese)
    テスト, カバレッジ, 品質, QA, 検証, 確認, ユニット, 統合, E2E, スペック, ランナー
  ]
  patterns: ["^(test|run tests|execute tests)( (?P<target>.+))?$", "^(run|execute) (unit|integration|e2e|all) tests?$"]
  contexts: [testing, quality_assurance, validation, coverage]

# Arguments
arguments:
  - name: target
    type: string
    required: false
    description: "Target directory or file to test"
    infer_from: user_query

  - name: type
    type: enum
    values: [unit, integration, e2e, all]
    required: false
    description: "Test type to execute"
    infer_from: user_query
    default: all

  - name: coverage
    type: bool
    required: false
    description: "Generate coverage report"
    infer_from: user_query
    default: false

  - name: watch
    type: bool
    required: false
    description: "Watch mode for continuous testing"
    infer_from: user_query
    default: false

  - name: fix
    type: bool
    required: false
    description: "Auto-fix simple test failures"
    infer_from: user_query
    default: false

# Auto-Execution
auto_trigger:
  enabled: true
  confidence_threshold: 0.85
  confirm_before_execution: true
  safety_checks: []

# Dependencies
mcp_servers: [playwright]
personas: [qa-specialist]
requires_skills: []
optional_skills: []
author: "SuperClaude Framework"
tags: [testing, quality, coverage, validation, qa]
---

# /sc:test - Testing and Quality Assurance

## Triggers

- Test execution requests for unit, integration, or e2e tests
- Coverage analysis and quality gate validation needs
- Continuous testing and watch mode scenarios
- Test failure analysis and debugging requirements

## Usage

```
/sc:test [target] [--type unit|integration|e2e|all] [--coverage] [--watch] [--fix]
```

## Behavioral Flow

1. **Discover**: Categorize available tests using runner patterns and conventions
2. **Configure**: Set up appropriate test environment and execution parameters
3. **Execute**: Run tests with monitoring and real-time progress tracking
4. **Analyze**: Generate coverage reports and failure diagnostics
5. **Report**: Provide actionable recommendations and quality metrics

Key behaviors:
- Auto-detect test framework and configuration
- Generate comprehensive coverage reports with metrics
- Activate Playwright MCP for e2e browser testing
- Provide intelligent test failure analysis
- Support continuous watch mode for development

## MCP Integration

- **Playwright MCP**: Auto-activated for `--type e2e` browser testing
- **QA Specialist Persona**: Activated for test analysis and quality assessment
- **Enhanced Capabilities**: Cross-browser testing, visual validation, performance metrics

## Tool Coordination

- **Bash**: Test runner execution and environment management
- **Glob**: Test discovery and file pattern matching
- **Grep**: Result parsing and failure analysis
- **Write**: Coverage reports and test summaries

## Key Patterns

- **Test Discovery**: Pattern-based categorization → appropriate runner selection
- **Coverage Analysis**: Execution metrics → comprehensive coverage reporting
- **E2E Testing**: Browser automation → cross-platform validation
- **Watch Mode**: File monitoring → continuous test execution

## Examples

### Basic Test Execution

```
/sc:test
# Discovers and runs all tests with standard configuration
# Generates pass/fail summary and basic coverage
```

### Targeted Coverage Analysis

```
/sc:test src/components --type unit --coverage
# Unit tests for specific directory with detailed coverage metrics
```

### Browser Testing

```
/sc:test --type e2e
# Activates Playwright MCP for comprehensive browser testing
# Cross-browser compatibility and visual validation
```

### Development Watch Mode

```
/sc:test --watch --fix
# Continuous testing with automatic simple failure fixes
# Real-time feedback during development
```

## Boundaries

**Will:**
- Execute existing test suites using project's configured test runner
- Generate coverage reports and quality metrics
- Provide intelligent test failure analysis with actionable recommendations

**Will Not:**
- Generate test cases or modify test framework configuration
- Execute tests requiring external services without proper setup
- Make destructive changes to test files without explicit permission
