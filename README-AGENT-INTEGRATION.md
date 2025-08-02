# Agent Integration Documentation

## Overview

This document describes the agent integration features implemented in the chat application. The system now supports multiple AI agents with different capabilities and provides comprehensive status tracking and performance monitoring.

## Features Implemented

### 1. Multiple Agent Types

The system supports five different agent types:

- **Multimodal Agent**: Handles documents and web search with visual understanding
- **Chat Agent**: General conversation and help
- **Document Agent**: Analyzes and extracts insights from documents
- **Research Agent**: Conducts comprehensive research with web search
- **Lightweight Agent**: Quick and simple responses (default)

### 2. Agent Status Tracking

Each agent tracks:
- Current status (online/offline/processing)
- Total queries processed
- Successful vs failed queries
- Success rate percentage
- Average response time
- Last activity timestamp

### 3. Performance Monitoring

The system provides:
- Real-time agent health monitoring
- Response time tracking
- Success rate calculations
- Detailed statistics per agent

### 4. Frontend Integration

#### Agent Status Component
- Shows current agent status with visual indicators
- Displays detailed statistics when expanded
- Auto-refreshes every 30 seconds
- Manual refresh capability

#### Agent Selector Component
- Allows users to switch between different agents
- Shows agent descriptions and capabilities
- Displays real-time status for each agent
- Shows performance metrics for each agent

#### Enhanced Chat Interface
- Shows which agent is currently active
- Integrates with agent service for responses
- Provides fallback responses if agent is unavailable

## Backend API Endpoints

### Agent Health
```
GET /agent/health
```
Returns overall agent service health and available agents.

### Agent Status
```
GET /agent/status?agent_type={type}
```
Returns detailed status and statistics for agents.

### Agent Statistics
```
GET /agent/stats?agent_type={type}
```
Returns comprehensive performance metrics.

### Agent Query
```
POST /agent/query
{
  "query": "user message",
  "agent_type": "lightweight"
}
```
Processes a query using the specified agent.

### Agent Upload
```
POST /agent/upload
```
Uploads and processes documents for agent use.

## Frontend Components

### AgentStatus.tsx
```typescript
interface AgentStatusProps {
  className?: string;
  showDetails?: boolean;
}
```

### AgentSelector.tsx
```typescript
interface AgentSelectorProps {
  onAgentChange: (agentType: string) => void;
  selectedAgent?: string;
  className?: string;
}
```

## Configuration

### Environment Variables
- `GEMINI_API_KEY`: Required for agent functionality
- `TAVILY_API_KEY`: Required for web search capabilities
- `QDRANT_URL`: For document retrieval (optional)
- `QDRANT_API_KEY`: For document retrieval (optional)

### Agent Configuration
Agents are configured in `backend/agents/agents.py` with:
- Role definitions
- Goals and backstories
- Tool assignments
- LLM model specifications

## Usage

### Starting the Application

1. Start the backend:
```bash
cd backend
python app.py
```

2. Start the frontend:
```bash
cd frontend
npm run dev
```

### Testing Agent Integration

Run the test script:
```bash
cd backend
python scripts/test_agent_integration.py
```

### Using Different Agents

1. Open the chat interface
2. Use the sidebar to select different agents
3. Send messages to see agent-specific responses
4. Monitor agent status and performance

## Agent Capabilities

### Lightweight Agent
- Fast responses
- Basic conversation
- No external dependencies
- Always available

### Multimodal Agent
- Document analysis
- Web search integration
- Visual understanding
- Comprehensive responses

### Chat Agent
- General conversation
- Helpful responses
- Context awareness
- Friendly interaction

### Document Agent
- Document analysis
- Information extraction
- Summary generation
- Insight discovery

### Research Agent
- Web search capabilities
- Comprehensive research
- Information synthesis
- Detailed analysis

## Performance Monitoring

The system tracks:
- Query success rates
- Response times
- Agent availability
- Error rates
- Usage patterns

## Error Handling

- Graceful fallbacks when agents are unavailable
- User-friendly error messages
- Automatic retry mechanisms
- Detailed logging for debugging

## Future Enhancements

- Agent-specific UI themes
- Advanced performance analytics
- Agent learning and improvement
- Custom agent creation
- Multi-agent collaboration

## Troubleshooting

### Common Issues

1. **Agent not responding**: Check API keys and network connectivity
2. **Slow responses**: Monitor agent performance metrics
3. **Authentication errors**: Verify JWT token validity
4. **Document upload failures**: Check file format and size limits

### Debug Commands

```bash
# Check agent health
curl http://localhost:8000/agent/health

# Get agent status
curl http://localhost:8000/agent/status

# Test agent query
curl -X POST http://localhost:8000/agent/query \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "agent_type": "lightweight"}'
```

## Contributing

When adding new agents:
1. Define the agent in `backend/agents/agents.py`
2. Add appropriate tools in `backend/agents/tools.py`
3. Update the frontend descriptions
4. Add tests for the new agent
5. Update documentation

## License

This agent integration is part of the chat application project. 