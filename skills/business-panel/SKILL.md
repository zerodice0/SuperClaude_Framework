---
name: business-panel
display_name: "Business Analysis"
description: "Multi-expert business analysis with adaptive interaction modes"
version: 1.0.0
category: workflow
complexity: enhanced

# Intent Detection
intents:
  primary: ["business analysis {doc}"]
  keywords: [business, panel, analysis, expert, strategic]
  patterns: ["^business (analysis|panel)( (?P<doc>.+))?$"]
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
personas: [analyzer, architect, mentor]
requires_skills: []
optional_skills: []
author: "SuperClaude Framework"
tags: []
---

# /sc:business-panel - Business Analysis

(Migrated from command - full documentation to be enhanced in Phase B)

