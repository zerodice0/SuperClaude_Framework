---
name: index-repo
display_name: "Repository Indexing"
description: "Repository indexing for 94% token reduction (58K → 3K)"
version: 1.0.0
category: special
complexity: standard

# Intent Detection
intents:
  primary: ["index repo"]
  keywords: [index, repository, indexing, optimization, tokens]
  patterns: ["^index (repo|repository)$"]
  contexts: []

# Arguments
arguments: []

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
tags: []
---

# /sc:index-repo - Repository Indexing

(Migrated from command - full documentation to be enhanced in Phase B)

