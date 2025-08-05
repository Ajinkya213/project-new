# Firebase-Integrated Agents System

## 🎯 Overview

Your application now has a complete Firebase-integrated agent system that combines:
- **Firebase Auth** - User authentication
- **Firestore** - Chat data and user interactions
- **Local Storage** - File management
- **RAG System** - Document processing and retrieval
- **Multiple Agents** - Specialized AI agents for different tasks

## ✅ What's Integrated

### 🔐 **Authentication & User Management**
- Firebase Auth for secure user authentication
- User-specific agent sessions
- Personalized agent interactions

### 🤖 **Agent Types**
1. **Lightweight Agent** - Fast general-purpose assistant
2. **Multimodal Agent** - Document analysis + web search
3. **Document Agent** - Specialized document analysis
4. **Research Agent** - Web research and information gathering
5. **Chat Agent** - Conversational assistant

### 📁 **File Management**
- Local file storage with user isolation
- Document processing for RAG system
- Secure file access with Firebase Auth

### 💬 **Chat Integration**
- Real-time chat with agents
- Chat history stored in Firestore
- Agent responses integrated into chat sessions

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd backend && pip install -r requirements.txt
cd frontend && npm install
```

### 2. Set Up Firebase Project
1. Create Firebase project
2. Enable Authentication (Email/Password)
3. Enable Firestore Database
4. Download service account key

### 3. Configure Environment
```env
# Backend (.env)
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_SERVICE_ACCOUNT_PATH=./serviceAccountKey.json

# Frontend (.env)
VITE_FIREBASE_API_KEY=your-api-key
VITE_FIREBASE_AUTH_DOMAIN=your-project-id.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
```

### 4. Test the System
```bash
# Start backend
cd backend && python app.py

# Start frontend
cd frontend && npm run dev
```

## 🛠️ API Endpoints

### Agent Queries
- `POST /agent/query` - Process query with any agent
- `POST /agent/chat/{session_id}/query` - Process query in chat session
- `POST /agent/auto-select` - Auto-select best agent for query

### Agent Management
- `GET /agent/agents` - Get available agents for user
- `GET /agent/agents/{type}/status` - Get specific agent status
- `GET /agent/agents/status` - Get all agent status
- `GET /agent/history` - Get user's agent interaction history
- `GET /agent/analytics` - Get agent usage analytics
- `GET /agent/health` - Agent system health check

### Chat Integration
- `GET /chat/sessions` - Get user's chat sessions
- `POST /chat/sessions` - Create new chat session
- `GET /chat/sessions/{id}` - Get specific chat session
- `POST /chat/sessions/{id}/messages` - Add message to chat

### File Management
- `POST /api/upload` - Upload file to local storage
- `GET /api/documents` - Get user's documents
- `GET /api/documents/{id}/download` - Download file
- `DELETE /api/documents/{id}` - Delete file

## 🎨 Frontend Integration

### Agent Query Component
```typescript
const handleAgentQuery = async (query: string, agentType?: string) => {
  try {
    const result = await apiService.processQuery(query, agentType);
    console.log('Agent response:', result);
  } catch (error) {
    console.error('Query failed:', error);
  }
};
```

### Chat with Agent
```typescript
const handleChatQuery = async (sessionId: string, query: string) => {
  try {
    const result = await apiService.processChatQuery(sessionId, query);
    console.log('Chat response:', result);
  } catch (error) {
    console.error('Chat query failed:', error);
  }
};
```

### Auto-Select Agent
```typescript
const handleAutoSelect = async (query: string) => {
  try {
    const reasoning = await apiService.autoSelectAgent(query);
    console.log('Selected agent:', reasoning.selected_agent);
    console.log('Reasoning:', reasoning);
  } catch (error) {
    console.error('Auto-select failed:', error);
  }
};
```

## 🔧 Agent Selection Logic

### Automatic Agent Selection
The system automatically selects the best agent based on:

1. **Keywords Analysis** - Detects relevant keywords in the query
2. **Pattern Matching** - Uses regex patterns to identify intent
3. **Context Awareness** - Considers user's uploaded documents
4. **Agent Capabilities** - Matches query to agent specialties

### Agent Specialties
- **Lightweight**: General questions, quick answers
- **Multimodal**: Document analysis + web search
- **Document**: Document analysis, summarization, insights
- **Research**: Web research, current information
- **Chat**: Conversational, casual chat

## 📊 Analytics & Monitoring

### User Analytics
- Agent usage patterns
- Query success rates
- Response times
- Document usage statistics

### Agent Performance
- Success rates per agent
- Average response times
- Error tracking
- Usage statistics

## 🔒 Security Features

### Authentication
- Firebase Auth for all requests
- User-specific data isolation
- Secure token verification

### File Security
- User-specific file folders
- Access control through Firebase Auth
- File type validation
- Size limits enforced

### Agent Security
- User-specific agent sessions
- Query logging and monitoring
- Rate limiting (can be implemented)

## 🎯 Use Cases

### Document Analysis
1. User uploads PDF documents
2. Documents are processed by RAG system
3. User asks questions about documents
4. Multimodal/Document agent provides answers

### Research Tasks
1. User asks research questions
2. Research agent searches web
3. Provides comprehensive answers with sources

### Chat Conversations
1. User starts casual conversation
2. Chat agent provides friendly responses
3. Conversation history stored in Firestore

### File Management
1. User uploads files through secure interface
2. Files stored in user-specific folders
3. Files can be downloaded or deleted
4. File metadata stored in Firestore

## 🚨 Troubleshooting

### Common Issues

1. **Agent not responding**
   ```bash
   # Check agent health
   curl http://localhost:8000/agent/health
   
   # Check agent status
   curl http://localhost:8000/agent/agents/status
   ```

2. **File upload issues**
   ```bash
   # Check upload folder permissions
   ls -la backend/uploads/
   
   # Check file size limits
   cat backend/.env | grep MAX_CONTENT_LENGTH
   ```

3. **Authentication errors**
   ```bash
   # Check Firebase configuration
   curl http://localhost:8000/health
   
   # Verify service account
   ls backend/serviceAccountKey.json
   ```

### Debug Commands

```bash
# Check all services
curl http://localhost:8000/health

# Test agent query
curl -X POST http://localhost:8000/agent/query \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "Hello, how are you?"}'

# Check user documents
curl -X GET http://localhost:8000/api/documents \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 📈 Performance Optimization

### Agent Loading
- Lazy loading for heavy agents
- Agent caching for frequently used agents
- Background initialization

### File Processing
- Asynchronous document processing
- Progress tracking for large files
- Efficient storage management

### Query Processing
- Intelligent agent selection
- Context-aware responses
- Caching for repeated queries

## 🔄 Migration Guide

### From Old System
1. **Update authentication** - Use Firebase Auth
2. **Migrate file storage** - Move to local storage
3. **Update agent calls** - Use new Firebase-integrated endpoints
4. **Update frontend** - Use new API service methods

### To Production
1. **Set up proper Firebase project**
2. **Configure security rules**
3. **Set up monitoring**
4. **Implement rate limiting**
5. **Add error handling**

## 🎉 Success!

Your application now has:
- ✅ **Firebase-integrated agents** - Secure and scalable
- ✅ **Intelligent agent selection** - Automatic best agent choice
- ✅ **Document processing** - RAG system with local storage
- ✅ **Real-time chat** - Integrated with agents
- ✅ **User analytics** - Track usage and performance
- ✅ **Production ready** - Secure and monitored

The system is now fully integrated and ready for production use! 