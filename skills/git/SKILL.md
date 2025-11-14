---
name: git
display_name: "Git Operations"
description: "Git operations with intelligent commit messages and workflow optimization"
version: 1.0.0
category: utility
complexity: basic

# Intent Detection
intents:
  primary: ["git {operation}", "commit {changes}", "push {branch}", "pull {updates}", "{operation} git"]
  keywords: [
    # English
    git, commit, push, pull, branch, merge, status, diff, log, checkout, clone, fetch, rebase, stash,
    # 한국어 (Korean)
    깃, 커밋, 푸시, 풀, 브랜치, 병합, 상태, 차이, 로그, 체크아웃, 클론, 페치, 리베이스, 스태시,
    # 日本語 (Japanese)
    ギット, コミット, プッシュ, プル, ブランチ, マージ, ステータス, 差分, ログ, チェックアウト, クローン, フェッチ, リベース, スタッシュ
  ]
  patterns: ["^git (status|commit|push|pull|branch|merge|diff|log|checkout|clone|fetch|rebase|stash).*$", "^(commit|push|pull) (?P<target>.+)$"]
  contexts: [version_control, repository, workflow, commit_message]

# Arguments
arguments:
  - name: operation
    type: enum
    values: [status, commit, push, pull, branch, merge, diff, log, checkout, clone, fetch, rebase, stash]
    required: false
    description: "Git operation to execute"
    infer_from: user_query
    default: status

  - name: args
    type: string
    required: false
    description: "Additional operation arguments"
    infer_from: user_query

  - name: smart_commit
    type: bool
    required: false
    description: "Generate intelligent commit messages"
    infer_from: user_query
    default: false

  - name: interactive
    type: bool
    required: false
    description: "Interactive mode for complex operations"
    infer_from: user_query
    default: false

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
tags: [git, version-control, commit, workflow]
---

# /sc:git - Git Operations

## Triggers

- Git repository operations: status, add, commit, push, pull, branch
- Need for intelligent commit message generation
- Repository workflow optimization requests
- Branch management and merge operations

## Usage

```
/sc:git [operation] [args] [--smart-commit] [--interactive]
```

## Behavioral Flow

1. **Analyze**: Check repository state and working directory changes
2. **Validate**: Ensure operation is appropriate for current Git context
3. **Execute**: Run Git command with intelligent automation
4. **Optimize**: Apply smart commit messages and workflow patterns
5. **Report**: Provide status and next steps guidance

Key behaviors:
- Generate conventional commit messages based on change analysis
- Apply consistent branch naming conventions
- Handle merge conflicts with guided resolution
- Provide clear status summaries and workflow recommendations

## Tool Coordination

- **Bash**: Git command execution and repository operations
- **Read**: Repository state analysis and configuration review
- **Grep**: Log parsing and status analysis
- **Write**: Commit message generation and documentation

## Key Patterns

- **Smart Commits**: Analyze changes → generate conventional commit message
- **Status Analysis**: Repository state → actionable recommendations
- **Branch Strategy**: Consistent naming and workflow enforcement
- **Error Recovery**: Conflict resolution and state restoration guidance

## Examples

### Smart Status Analysis

```
/sc:git status
# Analyzes repository state with change summary
# Provides next steps and workflow recommendations
```

### Intelligent Commit

```
/sc:git commit --smart-commit
# Generates conventional commit message from change analysis
# Applies best practices and consistent formatting
```

### Interactive Operations

```
/sc:git merge feature-branch --interactive
# Guided merge with conflict resolution assistance
```

## Boundaries

**Will:**
- Execute Git operations with intelligent automation
- Generate conventional commit messages from change analysis
- Provide workflow optimization and best practice guidance

**Will Not:**
- Modify repository configuration without explicit authorization
- Execute destructive operations without confirmation
- Handle complex merges requiring manual intervention
