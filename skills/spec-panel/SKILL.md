---
name: spec-panel
display_name: "Specification Review"
description: "Multi-expert specification review and improvement using renowned experts"
version: 1.0.0
category: workflow
complexity: enhanced

# Intent Detection
intents:
  primary: ["review spec {doc}"]
  keywords: [spec, specification, review, panel, expert, quality]
  patterns: ["^(review|analyze) spec( (?P<doc>.+))?$"]
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
mcp_servers: [sequential, context7]
personas: [technical-writer, system-architect, quality-engineer]
requires_skills: []
optional_skills: []
author: "SuperClaude Framework"
tags: []
---

# /sc:spec-panel - Specification Review

(Migrated from command - full documentation to be enhanced in Phase B)

