# Chat Application Backend - Complete System

## 🚀 **Overview**

A modular Flask backend with JWT authentication, MySQL database, and comprehensive chat functionality. Built with clean architecture principles and security best practices.

## 📋 **Features**

### **✅ Authentication System**
- User registration with validation
- JWT-based login/logout
- Token refresh mechanism
- Profile management
- Password strength validation
- Input sanitization

### **✅ Chat System**
- Chat session management (create, read, update, delete)
- Message handling (send, retrieve, update, delete)
- Pagination support for sessions and messages
- Real-time message updates
- Session ownership validation

### **✅ Security Features**
- JWT token authentication
- Password hashing with Werkzeug
- Input validation and sanitization
- CORS protection
- SQL injection prevention

### **✅ Database**
- MySQL with PyMySQL
- Optimized table structure
- Foreign key relationships
- Indexed queries for performance

## 🏗️ **Project Structure**

```
backend/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── setup_env.py          # Environment setup script
├── setup_database.py     # Database setup script
├── test_chat.py          # Chat system test script
├── models/
│   ├── __init__.py
│   ├── database.py       # Database connection
│   ├── user.py          # User model
│   └── chat.py          # Chat models
├── routes/
│   ├── __init__.py
│   ├── auth.py          # Authentication routes
│   └── chat.py          # Chat routes
└── utils/
    ├── __init__.py
    ├── auth_utils.py    # JWT utilities
    └── validators.py    # Input validation
```

## 🔧 **Setup Instructions**

### **1. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **2. Configure Environment**
```bash
python setup_env.py
```
Then edit the `.env` file with your MySQL credentials.

### **3. Setup Database**
```bash
python setup_database.py
```

### **4. Run the Application**
```bash
python app.py
```

### **5. Test the System**
```bash
python test_chat.py
```

## 📚 **API Endpoints**

### **Authentication Endpoints**

#### **Register User**
```http
POST /auth/register
Content-Type: application/json

{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePass123"
}
```

#### **Login User**
```http
POST /auth/login
Content-Type: application/json

{
    "username": "john_doe",
    "password": "SecurePass123"
}
```

#### **Refresh Token**
```http
POST /auth/refresh
Authorization: Bearer <refresh_token>
```

#### **Get Profile**
```http
GET /auth/profile
Authorization: Bearer <access_token>
```

#### **Update Profile**
```http
PUT /auth/profile
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "username": "new_username",
    "email": "newemail@example.com",
    "password": "NewSecurePass123"
}
```

### **Chat Endpoints**

#### **Create Chat Session**
```http
POST /chat/sessions
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "title": "My Chat Session"
}
```

#### **Get User's Chat Sessions**
```http
GET /chat/sessions?page=1&per_page=20
Authorization: Bearer <access_token>
```

#### **Get Specific Session with Messages**
```http
GET /chat/sessions/{session_id}
Authorization: Bearer <access_token>
```

#### **Update Session Title**
```http
PUT /chat/sessions/{session_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "title": "Updated Session Title"
}
```

#### **Delete Session**
```http
DELETE /chat/sessions/{session_id}
Authorization: Bearer <access_token>
```

#### **Send Message**
```http
POST /chat/sessions/{session_id}/messages
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "text": "Hello, this is a message!",
    "sender": "user"
}
```

#### **Get Messages**
```http
GET /chat/sessions/{session_id}/messages?page=1&per_page=50
Authorization: Bearer <access_token>
```

#### **Update Message**
```http
PUT /chat/sessions/{session_id}/messages/{message_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "text": "Updated message text"
}
```

#### **Delete Message**
```http
DELETE /chat/sessions/{session_id}/messages/{message_id}
Authorization: Bearer <access_token>
```

#### **Clear All Messages**
```http
DELETE /chat/sessions/{session_id}/messages
Authorization: Bearer <access_token>
```

## 🔒 **Security Features**

### **Password Requirements**
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number

### **Username Requirements**
- 3-80 characters
- Alphanumeric and underscores only
- Unique across the system

### **Message Validation**
- Maximum 5000 characters
- Content sanitization
- XSS protection

### **Session Validation**
- Maximum 255 characters for title
- Ownership verification
- Soft delete functionality

## 🗄️ **Database Schema**

### **Users Table**
```sql
CREATE TABLE users (
    id VARCHAR(255) PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE
);
```

### **Chat Sessions Table**
```sql
CREATE TABLE chat_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### **Messages Table**
```sql
CREATE TABLE messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    text TEXT NOT NULL,
    sender VARCHAR(10) NOT NULL,
    session_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
);
```

## 🧪 **Testing**

### **Automated Testing**
```bash
python test_chat.py
```

### **Manual Testing with curl**

#### **Register and Login:**
```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "TestPass123"
  }'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "TestPass123"
  }'
```

#### **Chat Operations:**
```bash
# Create session
curl -X POST http://localhost:8000/chat/sessions \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Session"}'

# Send message
curl -X POST http://localhost:8000/chat/sessions/1/messages \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello!", "sender": "user"}'

# Get messages
curl -X GET http://localhost:8000/chat/sessions/1/messages \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## ⚙️ **Configuration**

### **Environment Variables**
```env
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=true
SECRET_KEY=your-secret-key

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key

# MySQL Database
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your-password
MYSQL_DATABASE=chat_app

# Server
PORT=8000
```

## 🚨 **Error Handling**

### **Common Error Responses**

#### **Validation Errors (400)**
```json
{
    "error": "Validation failed",
    "details": ["Username is required", "Email is required"]
}
```

#### **Authentication Errors (401)**
```json
{
    "error": "Invalid username or password"
}
```

#### **Authorization Errors (403)**
```json
{
    "error": "Access denied"
}
```

#### **Resource Not Found (404)**
```json
{
    "error": "Session not found"
}
```

#### **Conflict Errors (409)**
```json
{
    "error": "Username already exists"
}
```

## 🔄 **Next Steps**

The complete chat system is now ready! Next steps:

1. **Add File Upload** - Document management
2. **Implement Real-time** - WebSocket integration
3. **Add Testing** - Unit and integration tests
4. **Deployment** - Production configuration
5. **Frontend Integration** - Connect with React frontend

## 📞 **Support**

For issues or questions:
1. Check the error logs
2. Verify database connection
3. Ensure all environment variables are set
4. Run the test script: `python test_chat.py`
5. Test with the provided curl commands

---

**Status**: ✅ Complete Chat System Ready
**Version**: 2.0.0
**Last Updated**: January 2024 