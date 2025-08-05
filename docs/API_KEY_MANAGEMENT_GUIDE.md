# 🔑 API Key Management Guide

## 🎯 Overview

Your application now includes a secure API key management system that allows users to:
- **Store their own API keys** securely encrypted in Firestore
- **Use personal API keys** for agent operations
- **Fallback to default keys** when user keys aren't available
- **Validate API keys** before storing them
- **Manage key access** per agent type

## 🔐 Security Features

### **Encryption**
- All API keys are encrypted using Fernet (AES-128-CBC)
- Encryption key is stored locally and never transmitted
- Keys are decrypted only when needed for agent operations

### **User Isolation**
- Each user's API keys are isolated in Firestore
- Users can only access their own keys
- Firebase Auth ensures secure access

### **Key Validation**
- API keys are validated before storage
- Real-time validation with actual API calls
- Invalid keys are rejected immediately

## 🛠️ API Endpoints

### **Get User's API Keys**
```bash
GET /api-keys/keys
Authorization: Bearer <firebase_token>
```

### **Get Key Status**
```bash
GET /api-keys/keys/status
Authorization: Bearer <firebase_token>
```

### **Get Available API Keys**
```bash
GET /api-keys/keys/available
Authorization: Bearer <firebase_token>
```

### **Store API Key**
```bash
POST /api-keys/keys
Authorization: Bearer <firebase_token>
Content-Type: application/json

{
  "key_name": "GEMINI_API_KEY",
  "api_key": "your_api_key_here",
  "validate": true
}
```

### **Delete API Key**
```bash
DELETE /api-keys/keys/GEMINI_API_KEY
Authorization: Bearer <firebase_token>
```

### **Validate API Key**
```bash
POST /api-keys/keys/GEMINI_API_KEY/validate
Authorization: Bearer <firebase_token>
Content-Type: application/json

{
  "api_key": "your_api_key_here"
}
```

### **Test API Key (without storing)**
```bash
POST /api-keys/keys/test
Authorization: Bearer <firebase_token>
Content-Type: application/json

{
  "key_name": "GEMINI_API_KEY",
  "api_key": "your_api_key_here"
}
```

## 🤖 Agent Key Requirements

### **Lightweight Agent**
- **Required**: `GEMINI_API_KEY`
- **Purpose**: General AI responses

### **Multimodal Agent**
- **Required**: `GEMINI_API_KEY`, `TAVILY_API_KEY`
- **Purpose**: Document analysis + web search

### **Document Agent**
- **Required**: `GEMINI_API_KEY`
- **Purpose**: Document analysis and insights

### **Research Agent**
- **Required**: `TAVILY_API_KEY`
- **Purpose**: Web research and information gathering

### **Chat Agent**
- **Required**: `GEMINI_API_KEY`
- **Purpose**: Conversational responses

## 📊 Key Status Response

```json
{
  "success": true,
  "status": {
    "GEMINI_API_KEY": {
      "name": "Google Gemini API",
      "description": "Required for AI text generation and document analysis",
      "url": "https://makersuite.google.com/app/apikey",
      "required_for": ["multimodal", "document", "lightweight", "chat"],
      "user_has_key": true,
      "is_valid": true
    },
    "TAVILY_API_KEY": {
      "name": "Tavily Search API",
      "description": "Required for web search and research",
      "url": "https://tavily.com/",
      "required_for": ["multimodal", "research"],
      "user_has_key": false,
      "is_valid": false
    }
  }
}
```

## 🎨 Frontend Integration

### **Get User's API Keys**
```typescript
const getUserKeys = async () => {
  try {
    const response = await apiService.getUserApiKeys();
    console.log('User API keys:', response.keys);
  } catch (error) {
    console.error('Failed to get API keys:', error);
  }
};
```

### **Store API Key**
```typescript
const storeApiKey = async (keyName: string, apiKey: string) => {
  try {
    const response = await apiService.storeApiKey(keyName, apiKey);
    console.log('API key stored:', response.message);
  } catch (error) {
    console.error('Failed to store API key:', error);
  }
};
```

### **Test API Key**
```typescript
const testApiKey = async (keyName: string, apiKey: string) => {
  try {
    const response = await apiService.testApiKey(keyName, apiKey);
    console.log('Key valid:', response.is_valid);
  } catch (error) {
    console.error('Failed to test API key:', error);
  }
};
```

### **Get Agent Availability**
```typescript
const getAgentAvailability = async () => {
  try {
    const response = await apiService.getAvailableAgents();
    console.log('Available agents:', response.agents);
    console.log('Key status:', response.key_status);
  } catch (error) {
    console.error('Failed to get agents:', error);
  }
};
```

## 🔄 Key Management Flow

### **1. User Registration**
1. User signs up with Firebase Auth
2. User gets access to agent system
3. System checks for user's API keys

### **2. Agent Selection**
1. User queries agent system
2. System auto-selects best agent
3. System checks required API keys for agent
4. If user has keys → use user's keys
5. If no user keys → fallback to default keys
6. If no keys available → return error

### **3. Key Storage**
1. User provides API key
2. System validates key with actual API call
3. If valid → encrypt and store in Firestore
4. If invalid → return error

### **4. Key Usage**
1. Agent needs API key
2. System retrieves user's encrypted key
3. System decrypts key temporarily
4. System uses key for API call
5. Key is cleared from memory

## 🚨 Error Handling

### **Missing API Keys**
```json
{
  "success": false,
  "error": "Missing required API keys: GEMINI_API_KEY, TAVILY_API_KEY",
  "agent_type": "multimodal",
  "missing_keys": ["GEMINI_API_KEY", "TAVILY_API_KEY"],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### **Invalid API Key**
```json
{
  "success": false,
  "error": "Invalid API key for GEMINI_API_KEY",
  "key_name": "GEMINI_API_KEY",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### **Agent Unavailable**
```json
{
  "success": false,
  "error": "Agent 'multimodal' is not available. Required API keys: GEMINI_API_KEY, TAVILY_API_KEY",
  "agent_type": "multimodal",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 🔧 Setup Instructions

### **1. Install Dependencies**
```bash
cd backend && pip install -r requirements.txt
```

### **2. Set Up Default Keys (Optional)**
```env
# .env file
GEMINI_API_KEY=your_default_gemini_key
TAVILY_API_KEY=your_default_tavily_key
QDRANT_API_KEY=your_default_qdrant_key
QDRANT_URL=http://localhost:6333
```

### **3. Start the Application**
```bash
# Backend
cd backend && python app.py

# Frontend
cd frontend && npm run dev
```

### **4. Test API Key Management**
```bash
# Test storing a key
curl -X POST http://localhost:8000/api-keys/keys \
  -H "Authorization: Bearer YOUR_FIREBASE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "key_name": "GEMINI_API_KEY",
    "api_key": "your_gemini_key",
    "validate": true
  }'

# Test getting key status
curl -X GET http://localhost:8000/api-keys/keys/status \
  -H "Authorization: Bearer YOUR_FIREBASE_TOKEN"
```

## 📈 Benefits

### **For Users**
- **Privacy**: Own API keys, own usage
- **Control**: Manage which agents are available
- **Cost Control**: Use personal API quotas
- **Security**: Encrypted key storage

### **For Developers**
- **Flexibility**: Users can provide their own keys
- **Fallback**: System works with default keys
- **Scalability**: No shared API key limits
- **Security**: Encrypted storage in Firestore

### **For System**
- **Reliability**: Multiple key sources
- **Performance**: User-specific key caching
- **Monitoring**: Track key usage per user
- **Compliance**: Secure key handling

## 🎉 Success!

Your application now supports:
- ✅ **Secure API key storage** with encryption
- ✅ **User-specific key management** in Firestore
- ✅ **Automatic key validation** before storage
- ✅ **Agent-specific key requirements** checking
- ✅ **Fallback to default keys** when needed
- ✅ **Real-time key status** monitoring
- ✅ **Frontend integration** for key management

Users can now provide their own API keys and have full control over their agent usage! 