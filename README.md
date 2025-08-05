# AI-Powered Document Processing and Chat Application

A comprehensive AI-powered application that combines document processing, intelligent agent orchestration, and real-time chat capabilities. Built with Flask, React, and CrewAI.

## 🚀 Features

### Core Functionality
- **Document Processing**: Upload and analyze PDF documents with AI
- **Intelligent Agent System**: Multi-agent orchestration with CrewAI
- **Real-time Chat**: Interactive chat with document context
- **RAG Integration**: Advanced retrieval-augmented generation
- **Multi-modal Support**: Text and image processing capabilities

### Agent Types
- **Lightweight Agent**: Fast responses for general queries
- **Document Agent**: Specialized document analysis and retrieval
- **Web Search Agent**: Current information retrieval from the web
- **Multimodal Agent**: Text and image processing
- **Research Agent**: Comprehensive research and analysis

### Technical Stack
- **Backend**: Flask, Python 3.9+
- **Frontend**: React, TypeScript, Vite
- **AI/ML**: CrewAI, Gemini, Qdrant Vector Database
- **Authentication**: Firebase Auth
- **Storage**: Firebase Firestore & Storage
- **PDF Processing**: Poppler, PyMuPDF

## 📋 Prerequisites

### System Requirements
- Python 3.9 or higher
- Node.js 16 or higher
- Poppler (for PDF processing)
- Git

### API Keys Required
- Firebase Project (for authentication and storage)
- Google Gemini API Key (for AI processing)
- Tavily API Key (for web search - optional)

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/ai-document-chat-app.git
cd ai-document-chat-app
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with your API configuration
```

### 4. Database Setup
```bash
cd backend
python setup_database.py
```

## ⚙️ Configuration

### Environment Variables

#### Backend (.env)
```bash
# Firebase Configuration
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_PRIVATE_KEY=your-private-key
FIREBASE_CLIENT_EMAIL=your-client-email
FIREBASE_CLIENT_ID=your-client-id
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
FIREBASE_AUTH_PROVIDER_X509_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
FIREBASE_CLIENT_X509_CERT_URL=your-cert-url

# AI Configuration
GEMINI_API_KEY=your-gemini-api-key
TAVILY_API_KEY=your-tavily-api-key

# Database Configuration
QDRANT_URL=http://localhost:6333
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Application Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

#### Frontend (.env.local)
```bash
VITE_API_URL=http://localhost:8000
VITE_FIREBASE_API_KEY=your-firebase-api-key
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
VITE_FIREBASE_APP_ID=your-app-id
```

## 🚀 Running the Application

### Development Mode

#### 1. Start Backend
```bash
cd backend
python run.py
```
The backend will be available at `http://localhost:8000`

#### 2. Start Frontend
```bash
cd frontend
npm run dev
```
The frontend will be available at `http://localhost:3000`

### Production Mode

#### 1. Build Frontend
```bash
cd frontend
npm run build
```

#### 2. Start Production Backend
```bash
cd backend
python start_backend.py
```

## 📁 Project Structure

```
project-new/
├── backend/                 # Flask backend
│   ├── api/                # API routes (v2)
│   ├── agents/             # AI agent orchestration
│   ├── config/             # Configuration files
│   ├── core/               # Core RAG and utility functions
│   ├── models/             # Database models
│   ├── routes/             # Legacy routes
│   ├── services/           # Business logic services
│   └── utils/              # Utility functions
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── contexts/       # React contexts
│   │   ├── features/       # Feature modules
│   │   ├── hooks/          # Custom React hooks
│   │   ├── lib/            # Service libraries
│   │   ├── routes/         # Routing configuration
│   │   └── utils/          # Utility functions
│   └── public/             # Static assets
├── docs/                   # Documentation
├── tests/                  # Test files
└── data/                   # Data storage
```

## 🔧 API Endpoints

### Core Endpoints
- `GET /health` - Health check
- `POST /api/v2/upload/` - Document upload
- `POST /api/v2/query/` - Query processing
- `GET /api/v2/agents/` - Available agents
- `GET /api/v2/tools/` - Available tools
- `GET /api/v2/documents/` - Indexed documents

### Authentication Endpoints
- `POST /auth/signup` - User registration
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout

### Chat Endpoints
- `GET /chat/sessions` - Get chat sessions
- `POST /chat/sessions` - Create new session
- `GET /chat/sessions/{id}/messages` - Get session messages
- `POST /chat/sessions/{id}/messages` - Send message

## 🤖 Agent System

### Agent Types and Capabilities

#### Lightweight Agent
- **Purpose**: Fast responses for general queries
- **Tools**: Basic text analysis, calculations
- **Use Case**: Quick questions, simple tasks

#### Document Agent
- **Purpose**: Document analysis and retrieval
- **Tools**: Document retrieval, text analysis
- **Use Case**: Questions about uploaded documents

#### Web Search Agent
- **Purpose**: Current information retrieval
- **Tools**: Web search, research tools
- **Use Case**: Latest news, current events

#### Multimodal Agent
- **Purpose**: Text and image processing
- **Tools**: Image analysis, text processing
- **Use Case**: Visual content analysis

#### Research Agent
- **Purpose**: Comprehensive research
- **Tools**: Web search, analysis tools
- **Use Case**: Detailed research tasks

## 🔄 Data Flow

### Document Upload Flow
```
Frontend Upload → API Layer → Service Layer → Document Processing → RAG Indexing → Success Response
```

### Query Processing Flow
```
Frontend Query → API Layer → Service Layer → Agent Selection → Agent Execution → RAG Search → Response Generation
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
python -m pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Integration Tests
```bash
python tests/test_integration.py
```

## 🚀 Deployment

### Docker Deployment
```bash
# Build and run with Docker
docker-compose up --build
```

### Manual Deployment
1. Set up production environment variables
2. Build frontend: `npm run build`
3. Start backend: `python start_backend.py`
4. Configure reverse proxy (nginx)

## 📊 Monitoring

### Health Checks
- Backend: `GET /health`
- Agents: `GET /api/v2/agents/`
- RAG System: `GET /api/v2/documents/`

### Logs
- Backend logs: `backend/logs/`
- Frontend logs: Browser console
- Error tracking: Firebase Crashlytics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Add tests for new functionality
5. Commit your changes: `git commit -m 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Common Issues

#### Upload Failed: Failed to fetch
- Check backend server is running
- Verify API endpoint is correct
- Check authentication token

#### Agent Not Available
- Verify agent is properly initialized
- Check agent dependencies
- Review agent configuration

#### Document Processing Failed
- Check PDF converter installation
- Verify file format support
- Review error logs

### Getting Help
- Check the [Troubleshooting Guide](TROUBLESHOOTING.md)
- Review the [Complete Dataflow Documentation](docs/COMPLETE_DATAFLOW.md)
- Open an issue on GitHub

## 🔄 Changelog

### Version 2.0.0
- Complete dataflow implementation
- Multi-agent orchestration
- Enhanced error handling
- Comprehensive API layer
- Production-ready architecture

### Version 1.0.0
- Initial release
- Basic document processing
- Simple chat functionality
- Firebase integration

## 🙏 Acknowledgments

- [CrewAI](https://github.com/joaomdmoura/crewAI) for agent orchestration
- [Firebase](https://firebase.google.com/) for authentication and storage
- [Qdrant](https://qdrant.tech/) for vector database
- [React](https://reactjs.org/) for frontend framework
- [Flask](https://flask.palletsprojects.com/) for backend framework 