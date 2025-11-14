---
name: research
display_name: "Deep Research"
description: "Deep web research with adaptive planning and intelligent search"
version: 1.0.0
category: research
complexity: advanced

# Intent Detection
intents:
  primary: ["research {query}", "find information about {topic}", "search for {subject}", "investigate {question}", "look up {topic}"]
  keywords: [research, search, find, investigate, information, query, data, analysis, web, tavily, current, latest, recent, study, explore]
  patterns: ["^(research|search|find|investigate|look up) (?P<query>.+)$", "^(what|who|where|when|why|how) (is|are|does|did) (?P<query>.+)$"]
  contexts: [research, information_gathering, web_search, knowledge_discovery]

# Arguments
arguments:
  - name: query
    type: string
    required: true
    description: "Research query or question"
    infer_from: user_query

  - name: depth
    type: enum
    values: [quick, standard, deep, exhaustive]
    required: false
    description: "Research depth level"
    infer_from: user_query
    default: standard

  - name: strategy
    type: enum
    values: [planning, intent, unified]
    required: false
    description: "Research strategy"
    infer_from: user_query
    default: unified

# Auto-Execution
auto_trigger:
  enabled: true
  confidence_threshold: 0.85
  confirm_before_execution: true
  safety_checks: []

# Dependencies
mcp_servers: [tavily, sequential, playwright, serena]
personas: [deep-research-agent]
requires_skills: []
optional_skills: []
author: "SuperClaude Framework"
tags: [research, search, information, web, tavily]
---

# /sc:research - Deep Research Command

## Triggers

- Research questions beyond knowledge cutoff
- Complex research questions
- Current events and real-time information
- Academic or technical research requirements
- Market analysis and competitive intelligence

## Usage

```
/sc:research "[query]" [--depth quick|standard|deep|exhaustive] [--strategy planning|intent|unified]
```

## Behavioral Flow

### 1. Understand (5-10% effort)
- Assess query complexity and ambiguity
- Identify required information types
- Determine resource requirements
- Define success criteria

### 2. Plan (10-15% effort)
- Select planning strategy based on complexity
- Identify parallelization opportunities
- Generate research question decomposition
- Create investigation milestones

### 3. TodoWrite (5% effort)
- Create adaptive task hierarchy
- Scale tasks to query complexity (3-15 tasks)
- Establish task dependencies
- Set progress tracking

### 4. Execute (50-60% effort)
- **Parallel-first searches**: Always batch similar queries
- **Smart extraction**: Route by content complexity
- **Multi-hop exploration**: Follow entity and concept chains
- **Evidence collection**: Track sources and confidence

### 5. Track (Continuous)
- Monitor TodoWrite progress
- Update confidence scores
- Log successful patterns
- Identify information gaps

### 6. Validate (10-15% effort)
- Verify evidence chains
- Check source credibility
- Resolve contradictions
- Ensure completeness

## Key Patterns

### Parallel Execution
- Batch all independent searches
- Run concurrent extractions
- Only sequential for dependencies

### Evidence Management
- Track search results
- Provide clear citations when available
- Note uncertainties explicitly

### Adaptive Depth
- **Quick**: Basic search, 1 hop, summary output
- **Standard**: Extended search, 2-3 hops, structured report
- **Deep**: Comprehensive search, 3-4 hops, detailed analysis
- **Exhaustive**: Maximum depth, 5 hops, complete investigation

## MCP Integration

- **Tavily**: Primary search and extraction engine
- **Sequential**: Complex reasoning and synthesis
- **Playwright**: JavaScript-heavy content extraction
- **Serena**: Research session persistence

## Output Standards

- Save reports to `claudedocs/research_[topic]_[timestamp].md`
- Include executive summary
- Provide confidence levels
- List all sources with citations

## Examples

```
/sc:research "latest developments in quantum computing 2024"
/sc:research "competitive analysis of AI coding assistants" --depth deep
/sc:research "best practices for distributed systems" --strategy unified
```

## Boundaries

**Will:**
- Current information, intelligent search, evidence-based analysis

**Will Not:**
- Make claims without sources, skip validation, access restricted content
