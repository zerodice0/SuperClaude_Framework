# Phase D: MCP Integration & Cross-Session Persistence

**Status**: 📋 Planning
**Target Version**: SuperClaude v5.0
**Dependencies**: Phase C (Auto-Execution & Learning)
**Estimated Effort**: 3-4 weeks

## Overview

Phase D integrates the Serena MCP server for cross-session persistence and context sharing, enabling SuperClaude to maintain learning data, project context, and execution history across sessions and projects.

## Goals

### Primary Goals

1. **Serena MCP Integration**
   - Store learning data in Serena instead of local JSON
   - Enable cross-session context sharing
   - Support project-specific learning patterns

2. **Cross-Session Persistence**
   - Maintain skill usage patterns across sessions
   - Share learning data between team members
   - Project-specific vs global learning

3. **Enhanced Context Awareness**
   - Use Serena's analysis capabilities for richer context
   - Multi-project context correlation
   - Historical pattern analysis

### Secondary Goals

4. **MCP Server Health Monitoring**
   - Validate MCP server availability before execution
   - Graceful degradation when servers unavailable
   - Connection pooling and retry logic

5. **Advanced Learning Features**
   - Team-wide usage patterns
   - Project-specific preferences
   - Failure pattern recognition

## Architecture

### Current State (Phase C)

```
ExecutionRouter
    ├─ SkillMatcher (Phase B)
    ├─ SafetyValidator
    └─ LearningSystem
           └─ JSON file (~/.superclaude/learning.json)
```

### Target State (Phase D)

```
ExecutionRouter
    ├─ SkillMatcher (Phase B)
    ├─ SafetyValidator (enhanced with MCP checks)
    └─ LearningSystem
           ├─ Local Cache (JSON)
           └─ Serena MCP Backend
                  ├─ Project Context
                  ├─ Team Learning
                  ├─ Execution History
                  └─ Failure Patterns
```

## Implementation Plan

### Week 1: Serena MCP Foundation

**Tasks**:
1. Create SerenaClient wrapper for MCP operations
2. Implement connection management and retry logic
3. Add health check integration to SafetyValidator
4. Design Serena data schema for learning data

**Deliverables**:
- `src/superclaude/mcp/serena_client.py`
- `src/superclaude/mcp/connection_manager.py`
- Updated `SafetyValidator` with MCP dependency checks
- Schema documentation

**Success Criteria**:
- SerenaClient can connect and perform basic operations
- Connection pooling works correctly
- Graceful degradation when Serena unavailable

### Week 2: Learning Data Migration

**Tasks**:
1. Extend LearningSystem to support dual backends (JSON + Serena)
2. Implement data synchronization logic
3. Add project context to learning data
4. Create migration tool for existing JSON data

**Deliverables**:
- Updated `LearningSystem` with Serena backend
- `SerenaLearningBackend` class
- Migration script: `scripts/migrate_learning_to_serena.py`
- Sync strategy documentation

**Success Criteria**:
- Learning data stored in both local and Serena
- Existing JSON data can be migrated
- Sync conflicts handled gracefully

### Week 3: Cross-Session Features

**Tasks**:
1. Implement session tracking and correlation
2. Add project-specific learning isolation
3. Create team learning aggregation
4. Build historical pattern analysis

**Deliverables**:
- `SessionManager` class
- Project isolation logic
- Team learning aggregation queries
- Pattern analysis utilities

**Success Criteria**:
- Sessions tracked across multiple invocations
- Project learning isolated from global
- Team patterns visible and actionable

### Week 4: Testing & Integration

**Tasks**:
1. Write integration tests for Serena backend
2. Add MCP server mocking for tests
3. Update demo scripts with Serena features
4. Performance optimization and caching

**Deliverables**:
- `tests/mcp/test_serena_client.py`
- `tests/mcp/test_learning_backend.py`
- Updated demo scripts
- Performance benchmarks

**Success Criteria**:
- 80% test coverage for MCP code
- All demos work with and without Serena
- Performance <100ms for Serena operations

## Data Schema Design

### Serena Storage Structure

```python
# Project Context Storage
{
    "project_id": "hash_of_cwd",
    "project_name": "SuperClaude_Framework",
    "project_type": "python",
    "last_updated": "2025-11-14T12:00:00Z",
    "git_info": {
        "current_branch": "feature/phase-d",
        "recent_branches": ["main", "integration", "feature/phase-c"],
        "repo_url": "https://github.com/user/repo"
    },
    "dependencies": {...},
    "testing": {...}
}

# Learning Data Storage
{
    "project_id": "hash_of_cwd",
    "scope": "project",  # or "global", "team"
    "skill_usage": {
        "troubleshoot": {
            "count": 42,
            "success_count": 38,
            "last_used": "2025-11-14T11:30:00Z",
            "avg_execution_time_ms": 125.5
        }
    },
    "argument_patterns": {
        "troubleshoot.issue": {
            "login error": 15,
            "network timeout": 8,
            "database connection": 5
        }
    },
    "query_patterns": {
        "troubleshoot": [
            "troubleshoot login error",
            "troubleshoot auth issue",
            ...
        ]
    },
    "recent_skills": ["troubleshoot", "implement", "test"],
    "failure_patterns": [
        {
            "skill": "cleanup",
            "error": "Permission denied",
            "context": {"branch": "main"},
            "count": 3
        }
    ]
}

# Session History
{
    "session_id": "uuid",
    "project_id": "hash_of_cwd",
    "started_at": "2025-11-14T10:00:00Z",
    "ended_at": "2025-11-14T12:00:00Z",
    "queries": [
        {
            "query": "troubleshoot login error",
            "skill_used": "troubleshoot",
            "executed": true,
            "success": true,
            "execution_time_ms": 125,
            "timestamp": "2025-11-14T10:15:00Z"
        }
    ],
    "git_branch": "feature/test",
    "total_executions": 12
}
```

## Component Design

### 1. SerenaClient

```python
class SerenaClient:
    """Wrapper for Serena MCP operations."""

    def __init__(self, connection_manager: ConnectionManager):
        self.connection = connection_manager

    async def store_learning_data(
        self,
        project_id: str,
        scope: str,
        data: LearningData
    ) -> bool:
        """Store learning data to Serena."""

    async def retrieve_learning_data(
        self,
        project_id: str,
        scope: str = "project"
    ) -> Optional[LearningData]:
        """Retrieve learning data from Serena."""

    async def store_session(
        self,
        session: SessionData
    ) -> bool:
        """Store session data."""

    async def get_team_patterns(
        self,
        project_id: str,
        skill_name: str
    ) -> Dict[str, Any]:
        """Get team-wide usage patterns."""

    async def health_check(self) -> bool:
        """Check if Serena is available."""
```

### 2. Dual-Backend LearningSystem

```python
class LearningSystem:
    """Learning system with local + Serena backends."""

    def __init__(
        self,
        local_path: Optional[Path] = None,
        serena_client: Optional[SerenaClient] = None,
        sync_strategy: str = "local_first"
    ):
        self.local_backend = LocalLearningBackend(local_path)
        self.serena_backend = SerenaLearningBackend(serena_client) if serena_client else None
        self.sync_strategy = sync_strategy

    def track_execution(
        self,
        query: str,
        match: SkillMatch,
        result: ExecutionResult
    ) -> None:
        """Track to both backends based on strategy."""

        # Always track locally (fast)
        self.local_backend.track_execution(query, match, result)

        # Async sync to Serena
        if self.serena_backend:
            asyncio.create_task(
                self.serena_backend.track_execution(query, match, result)
            )

    def calculate_learning_boost(
        self,
        skill_name: str,
        query: str,
        include_team: bool = True
    ) -> float:
        """Calculate boost from local + team learning."""

        # Local boost (fast)
        local_boost = self.local_backend.calculate_boost(skill_name, query)

        # Team boost (if Serena available)
        team_boost = 0.0
        if include_team and self.serena_backend:
            team_patterns = await self.serena_backend.get_team_patterns(skill_name)
            team_boost = self._calculate_team_boost(query, team_patterns)

        return min(local_boost + team_boost, 0.15)  # Cap at 0.15 for team learning
```

### 3. Enhanced SafetyValidator

```python
class SafetyValidator:
    """Enhanced with MCP server health checks."""

    def __init__(
        self,
        serena_client: Optional[SerenaClient] = None,
        mcp_manager: Optional[MCPServerManager] = None
    ):
        self.serena_client = serena_client
        self.mcp_manager = mcp_manager

    async def validate(
        self,
        match: SkillMatch,
        context: ProjectContext
    ) -> SafetyResult:
        """Validate with MCP health checks."""

        # ... existing checks ...

        # Check MCP server availability
        if match.skill.mcp_servers:
            unavailable = await self._check_mcp_availability(
                match.skill.mcp_servers
            )
            if unavailable:
                return SafetyResult(
                    safe=False,
                    warning=f"Required MCP servers unavailable: {', '.join(unavailable)}"
                )

        return SafetyResult(safe=True)

    async def _check_mcp_availability(
        self,
        servers: List[str]
    ) -> List[str]:
        """Check which MCP servers are unavailable."""

        if not self.mcp_manager:
            return []  # No checking if manager not available

        unavailable = []
        for server in servers:
            if not await self.mcp_manager.is_available(server):
                unavailable.append(server)

        return unavailable
```

## Migration Strategy

### Phase 1: Opt-in Serena (v5.0-alpha)

- Serena backend optional
- CLI flag: `--use-serena`
- Fallback to local JSON if Serena unavailable

### Phase 2: Default with Fallback (v5.0-beta)

- Serena enabled by default
- Automatic fallback to local if unavailable
- Warning message when using local-only

### Phase 3: Serena Required (v5.0)

- Serena required for full feature set
- Local JSON deprecated (read-only for migration)
- Clear migration path and documentation

## Performance Targets

| Operation | Target | Strategy |
|-----------|--------|----------|
| Serena store | <50ms | Async, non-blocking |
| Serena retrieve | <100ms | Cache locally, TTL 5min |
| Health check | <20ms | Connection pooling |
| Sync conflict resolution | <200ms | Last-write-wins |
| Team pattern aggregation | <500ms | Pre-computed, cached |

## Testing Strategy

### Unit Tests

- SerenaClient operations
- Connection management
- Data serialization/deserialization
- Sync conflict resolution

### Integration Tests

- End-to-end with mock Serena server
- Dual-backend synchronization
- Graceful degradation scenarios
- Performance benchmarks

### Manual Testing

- Real Serena MCP server connection
- Multi-project scenarios
- Team collaboration workflows
- Migration from JSON to Serena

## Risks & Mitigation

### Risk 1: Serena MCP Availability

**Impact**: High
**Probability**: Medium
**Mitigation**:
- Dual-backend strategy (local + Serena)
- Automatic fallback to local
- Clear error messages and guidance

### Risk 2: Data Sync Conflicts

**Impact**: Medium
**Probability**: High (multi-user environments)
**Mitigation**:
- Last-write-wins strategy
- Conflict detection and logging
- Manual resolution tools

### Risk 3: Performance Degradation

**Impact**: Medium
**Probability**: Low
**Mitigation**:
- Async operations for Serena
- Local caching with TTL
- Performance monitoring

### Risk 4: Migration Complexity

**Impact**: Low
**Probability**: Medium
**Mitigation**:
- Automated migration script
- Dry-run mode
- Rollback capability

## Success Metrics

1. **Adoption Rate**: 50% of users enable Serena within 3 months
2. **Performance**: <100ms average for Serena operations
3. **Reliability**: 99% uptime with graceful degradation
4. **Learning Improvement**: 20% increase in confidence boost accuracy
5. **Team Collaboration**: 30% of users share learning data

## Timeline

```
Week 1: Serena Foundation      [=============>        ]
Week 2: Learning Migration     [             >        ]
Week 3: Cross-Session Features [              >       ]
Week 4: Testing & Integration  [               >      ]
                               └─────────────────────┘
                               Month 1: Phase D Complete
```

## Dependencies

### External

- **Serena MCP Server**: Must be installed and configured
- **airis-mcp-gateway**: For MCP communication
- **asyncio**: For async operations

### Internal

- Phase B: Intent Detection (for context)
- Phase C: Auto-Execution (for learning data)

## Documentation Requirements

1. **User Guide**: Setting up Serena MCP
2. **Migration Guide**: JSON to Serena migration
3. **API Reference**: SerenaClient and backends
4. **Troubleshooting**: Common Serena issues

## Future Enhancements (Post-v5.0)

1. **Multi-Tenant Support**: Organization-level learning
2. **Advanced Analytics**: Usage dashboards, trends
3. **Collaborative Features**: Shared skill templates
4. **AI-Powered Insights**: Pattern recommendations
5. **Integration with Other MCPs**: Tavily, Context7 learning

## Open Questions

1. **Data Privacy**: How to handle sensitive project data in Serena?
   - Proposed: Opt-in sharing, encryption for sensitive fields

2. **Conflict Resolution**: Beyond last-write-wins?
   - Proposed: Start with LWW, add CRDT support in v5.1

3. **Team Boundaries**: How to define "team" for shared learning?
   - Proposed: Git repository URL or explicit team ID

4. **Retention Policy**: How long to keep session history?
   - Proposed: 90 days default, configurable

5. **Cost/Quotas**: Any Serena storage limits to consider?
   - Proposed: Monitor during alpha, add compression if needed

## Appendix A: Serena MCP Operations

```typescript
// Serena MCP tool calls (pseudo-code)

// Store learning data
await mcp.tool("serena", "store", {
    collection: "superclaude_learning",
    id: `${project_id}_${scope}`,
    data: learningDataJSON
});

// Retrieve learning data
const result = await mcp.tool("serena", "retrieve", {
    collection: "superclaude_learning",
    id: `${project_id}_${scope}`
});

// Query team patterns
const patterns = await mcp.tool("serena", "query", {
    collection: "superclaude_learning",
    filter: {
        project_id: project_id,
        scope: "team"
    },
    aggregate: {
        skill_usage: "sum",
        argument_patterns: "merge"
    }
});
```

## Appendix B: Configuration File

```yaml
# ~/.superclaude/config.yaml

mcp:
  serena:
    enabled: true
    connection:
      timeout_ms: 5000
      retry_attempts: 3
      retry_delay_ms: 1000

learning:
  backends:
    - type: local
      path: ~/.superclaude/learning.json
      priority: 1  # Fastest, always available

    - type: serena
      priority: 2  # Sync to Serena
      sync_strategy: async
      cache_ttl_seconds: 300

  scopes:
    - name: project
      enabled: true
      share_with_team: false

    - name: global
      enabled: true
      share_with_team: false

    - name: team
      enabled: false  # Opt-in
      share_with_team: true

safety:
  mcp_health_checks: true
  require_mcp_servers: false  # Warn but don't block
```

---

**Next Review**: Before Phase D implementation begins
**Owner**: TBD
**Status**: 📋 Planning - Ready for review
