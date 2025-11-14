---
name: agent
display_name: "SC Agent"
description: "Session controller that orchestrates investigation, implementation, and review"
version: 1.0.0
category: orchestration
complexity: advanced

# Intent Detection
intents:
  primary: ["agent"]
  keywords: [agent, session, controller, orchestrate]
  patterns: ["^agent$"]
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

# /sc:agent - SC Agent

(Migrated from command - full documentation to be enhanced in Phase B)

