# Firebase Integration Setup Guide

## 🚀 Overview

This guide will help you set up Firebase for authentication, storage, and chat functionality in your application.

## 📋 Prerequisites

1. **Firebase Account**: Create a Firebase account at [console.firebase.google.com](https://console.firebase.google.com)
2. **Node.js & npm**: For frontend dependencies
3. **Python**: For backend dependencies

## 🔧 Step 1: Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Click "Create a project" or "Add project"
3. Enter your project name (e.g., "chat-app-firebase")
4. Choose whether to enable Google Analytics (optional)
5. Click "Create project"

## 🔧 Step 2: Enable Firebase Services

### Authentication
1. In Firebase Console, go to "Authentication" → "Sign-in method"
2. Enable "Email/Password" authentication
3. Optionally enable other providers (Google, GitHub, etc.)

### Firestore Database
1. Go to "Firestore Database" → "Create database"
2. Choose "Start in test mode" (for development)
3. Select a location for your database

### Storage
1. Go to "Storage" → "Get started"
2. Choose "Start in test mode" (for development)
3. Select a location for your storage

## 🔧 Step 3: Get Firebase Configuration

### For Frontend (Web App)
1. In Firebase Console, go to "Project Settings" → "General"
2. Scroll down to "Your apps" section
3. Click the web icon (</>) to add a web app
4. Register your app with a nickname (e.g., "chat-app-web")
5. Copy the configuration object

### For Backend (Service Account)
1. Go to "Project Settings" → "Service accounts"
2. Click "Generate new private key"
3. Download the JSON file (save as `serviceAccountKey.json`)

## 🔧 Step 4: Configure Environment Variables

### Backend Configuration
Create a `.env` file in the `backend/` directory:

```env
# Firebase Configuration
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
FIREBASE_SERVICE_ACCOUNT_PATH=./serviceAccountKey.json

# Flask Configuration
FLASK_ENV=development
DEBUG=True
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]

# Other Configuration
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216
```

### Frontend Configuration
Create a `.env` file in the `frontend/` directory:

```env
# Firebase Configuration
VITE_FIREBASE_API_KEY=your-api-key
VITE_FIREBASE_AUTH_DOMAIN=your-project-id.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
VITE_FIREBASE_APP_ID=your-app-id
```

## 🔧 Step 5: Install Dependencies

### Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Frontend Dependencies
```bash
cd frontend
npm install
```

## 🔧 Step 6: Place Service Account Key

1. Copy your downloaded `serviceAccountKey.json` to the `backend/` directory
2. Update the path in your `.env` file if needed

## 🔧 Step 7: Test the Setup

### Backend Test
```bash
cd backend
python app.py
```

Visit `http://localhost:8000/health` to check if Firebase is initialized.

### Frontend Test
```bash
cd frontend
npm run dev
```

Visit `http://localhost:5173` and try to sign up/login.

## 🔧 Step 8: Security Rules (Production)

### Firestore Rules
Go to Firestore → Rules and update:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can only access their own data
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Chat sessions
    match /chat_sessions/{sessionId} {
      allow read, write: if request.auth != null && 
        request.auth.uid == resource.data.user_id;
    }
    
    // Messages
    match /messages/{messageId} {
      allow read, write: if request.auth != null && 
        request.auth.uid == get(/databases/$(database)/documents/chat_sessions/$(resource.data.session_id)).data.user_id;
    }
    
    // Documents
    match /documents/{documentId} {
      allow read, write: if request.auth != null && 
        request.auth.uid == resource.data.user_id;
    }
  }
}
```

### Storage Rules
Go to Storage → Rules and update:

```javascript
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    match /uploads/{userId}/{allPaths=**} {
      allow read, write: if request.auth != null && 
        request.auth.uid == userId;
    }
  }
}
```

## 🎯 Features Implemented

### ✅ Authentication
- User registration with email/password
- User login/logout
- Password reset (Firebase handles this)
- Email verification
- Persistent sessions

### ✅ Storage
- File upload to Firebase Storage
- File download with signed URLs
- User-specific file organization
- File metadata storage in Firestore

### ✅ Chat System
- Real-time chat sessions
- Message storage in Firestore
- User-specific chat history
- Message editing and deletion

### ✅ Security
- Firebase Auth handles authentication
- Firestore security rules
- Storage security rules
- User data isolation

## 🚨 Troubleshooting

### Common Issues

1. **Firebase not initialized**
   - Check service account path in `.env`
   - Verify project ID and bucket name

2. **CORS errors**
   - Update CORS_ORIGINS in backend `.env`
   - Add your frontend URL to Firebase Auth authorized domains

3. **Permission denied**
   - Check Firestore and Storage security rules
   - Ensure user is authenticated

4. **Frontend build errors**
   - Run `npm install` to install Firebase dependencies
   - Check environment variables are properly set

### Debug Commands

```bash
# Check Firebase initialization
curl http://localhost:8000/health

# Check environment variables
echo $FIREBASE_PROJECT_ID

# Test Firebase connection
python -c "from config.firebase_config import firebase_config; print('Firebase OK')"
```

## 📚 Next Steps

1. **Customize UI**: Update the frontend components to match your design
2. **Add Features**: Implement additional Firebase features like:
   - Real-time chat updates
   - File sharing
   - User profiles
   - Push notifications
3. **Production**: Set up proper security rules and monitoring
4. **Deployment**: Deploy to your preferred hosting platform

## 🔗 Useful Links

- [Firebase Documentation](https://firebase.google.com/docs)
- [Firebase Console](https://console.firebase.google.com)
- [Firebase Security Rules](https://firebase.google.com/docs/rules)
- [Firebase Admin SDK](https://firebase.google.com/docs/admin) 