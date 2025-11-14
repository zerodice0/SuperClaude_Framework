---
name: recommend
display_name: "Command Recommender"
description: "Ultra-intelligent command recommendation engine for user requests"
version: 1.0.0
category: utility
complexity: enhanced

# Intent Detection
intents:
  primary: ["recommend {request}"]
  keywords: [recommend, suggestion, command, intelligent, guidance]
  patterns: ["^recommend( (?P<request>.+))?$"]
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
personas: [analyzer, mentor]
requires_skills: []
optional_skills: []
author: "SuperClaude Framework"
tags: []
---

# /sc:recommend - Command Recommender

(Migrated from command - full documentation to be enhanced in Phase B)

