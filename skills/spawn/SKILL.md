---
name: spawn
display_name: "Meta-System Orchestration"
description: "Meta-system task orchestration with intelligent breakdown and delegation"
version: 1.0.0
category: special
complexity: high

# Intent Detection
intents:
  primary: ["spawn {task}"]
  keywords: [spawn, orchestrate, breakdown, delegate, meta-system]
  patterns: ["^spawn( (?P<task>.+))?$"]
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

# /sc:spawn - Meta-System Orchestration

(Migrated from command - full documentation to be enhanced in Phase B)

