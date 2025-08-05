# Hybrid Storage Setup Guide

## 🎯 Overview

This setup uses a hybrid approach:
- **Firebase Auth** - For user authentication
- **Firestore** - For chat data and user metadata
- **Local Storage** - For file uploads (no Firebase Storage needed)

## ✅ Benefits

- ✅ **No Firebase Storage costs** - Files stored locally
- ✅ **Firebase Auth** - Secure authentication
- ✅ **Firestore** - Real-time chat data
- ✅ **Local file storage** - Unlimited storage
- ✅ **Production ready** - Scalable architecture

## 🚀 Quick Setup

### 1. Install Dependencies

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### 2. Firebase Project Setup

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Create a new project
3. Enable **Authentication** (Email/Password)
4. Enable **Firestore Database**
5. **Skip Firebase Storage** - We're using local storage

### 3. Environment Variables

**Backend** (`.env` in `backend/`):
```env
# Firebase Configuration (Auth + Firestore only)
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_SERVICE_ACCOUNT_PATH=./serviceAccountKey.json

# Flask Configuration
FLASK_ENV=development
DEBUG=True
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]

# Local Storage Configuration
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216
```

**Frontend** (`.env` in `frontend/`):
```env
# Firebase Configuration (Auth + Firestore only)
VITE_FIREBASE_API_KEY=your-api-key
VITE_FIREBASE_AUTH_DOMAIN=your-project-id.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
VITE_FIREBASE_APP_ID=your-app-id

# API Configuration
VITE_API_URL=http://localhost:8000
```

### 4. Download Service Account Key

1. In Firebase Console → Project Settings → Service Accounts
2. Generate new private key
3. Save as `serviceAccountKey.json` in `backend/` directory

### 5. Test the Setup

```bash
# Start backend
cd backend
python app.py

# Start frontend (in new terminal)
cd frontend
npm run dev
```

Visit `http://localhost:5173` and test:
- User registration/login
- File upload
- Chat functionality

## 📁 File Structure

```
backend/
├── uploads/                    # Local file storage
│   └── {user_id}/             # User-specific folders
│       └── {files}            # User's uploaded files
├── services/
│   ├── firebase_auth_service.py    # Firebase Auth
│   ├── firebase_chat_service.py    # Firestore chat
│   └── local_storage_service.py    # Local file storage
└── routes/
    ├── auth.py                     # Firebase Auth routes
    ├── chat.py                     # Firestore chat routes
    └── api.py                      # Local storage routes
```

## 🔧 Key Features

### Authentication Flow
1. User signs up/logs in with Firebase Auth
2. Firebase handles token management
3. Backend verifies Firebase ID tokens
4. Secure API access with Bearer tokens

### File Upload Flow
1. User uploads file through frontend
2. File sent to backend with Firebase token
3. Backend saves file to local storage (`uploads/{user_id}/`)
4. File metadata stored in Firestore
5. User can download files directly

### Chat Flow
1. User creates chat session
2. Messages stored in Firestore
3. Real-time updates possible
4. User-specific chat isolation

## 🔒 Security Features

### Backend Security
- Firebase ID token verification
- User-specific file access
- Secure file uploads with validation
- CORS protection

### File Security
- Files stored in user-specific folders
- Access control through Firebase Auth
- File type validation
- Size limits enforced

### Database Security
- Firestore security rules
- User-specific collections
- Data validation

## 🛠️ API Endpoints

### Authentication
- `POST /auth/signup` - Create user account
- `POST /auth/verify-token` - Verify Firebase token
- `GET /auth/profile` - Get user profile
- `PUT /auth/profile` - Update profile
- `DELETE /auth/delete-account` - Delete account

### Chat
- `GET /chat/sessions` - Get user's chat sessions
- `POST /chat/sessions` - Create new chat session
- `GET /chat/sessions/{id}` - Get specific chat session
- `PUT /chat/sessions/{id}` - Update chat session
- `DELETE /chat/sessions/{id}` - Delete chat session
- `POST /chat/sessions/{id}/messages` - Add message
- `PUT /chat/messages/{id}` - Update message
- `DELETE /chat/messages/{id}` - Delete message

### Files (Local Storage)
- `POST /api/upload` - Upload file to local storage
- `GET /api/documents` - Get user's documents
- `GET /api/documents/{id}` - Get specific document
- `GET /api/documents/{id}/download` - Download file
- `DELETE /api/documents/{id}` - Delete file
- `GET /api/uploads/{user_id}/{filename}` - Serve file

## 🎨 Frontend Integration

### File Upload Component
```typescript
const handleFileUpload = async (file: File) => {
  try {
    const result = await apiService.uploadFile(file);
    console.log('File uploaded:', result);
  } catch (error) {
    console.error('Upload failed:', error);
  }
};
```

### File Download Component
```typescript
const handleFileDownload = async (documentId: string) => {
  try {
    await apiService.downloadFile(documentId);
  } catch (error) {
    console.error('Download failed:', error);
  }
};
```

## 🚨 Troubleshooting

### Common Issues

1. **Upload folder not created**
   ```bash
   # Check if uploads folder exists
   ls backend/uploads
   
   # Create manually if needed
   mkdir -p backend/uploads
   ```

2. **Permission denied for file uploads**
   ```bash
   # Check folder permissions
   chmod 755 backend/uploads
   ```

3. **File size too large**
   - Update `MAX_CONTENT_LENGTH` in backend `.env`
   - Check frontend file size validation

4. **CORS errors**
   - Update `CORS_ORIGINS` in backend `.env`
   - Add frontend URL to Firebase Auth authorized domains

### Debug Commands

```bash
# Check upload folder
ls -la backend/uploads/

# Check file permissions
ls -la backend/uploads/*/

# Test file upload
curl -X POST http://localhost:8000/api/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test.pdf"

# Check health
curl http://localhost:8000/health
```

## 📈 Production Considerations

### File Storage
- **Development**: Local storage in `uploads/` folder
- **Production**: Consider cloud storage (AWS S3, Google Cloud Storage)
- **Backup**: Regular backups of upload folder
- **Cleanup**: Implement file cleanup for old/unused files

### Security
- **File validation**: Check file types and sizes
- **Virus scanning**: Implement virus scanning for uploads
- **Access control**: Ensure users can only access their files
- **Rate limiting**: Prevent abuse of upload endpoints

### Performance
- **File compression**: Compress large files
- **CDN**: Use CDN for file serving in production
- **Caching**: Implement file caching
- **Monitoring**: Monitor disk usage and performance

## 🔄 Migration from Firebase Storage

If you were previously using Firebase Storage:

1. **Export existing files** from Firebase Storage
2. **Update file references** in your database
3. **Migrate to local storage** using the new service
4. **Update frontend** to use new download methods

## 🎉 Success!

Your application now has:
- ✅ **Free Firebase Auth** - No storage costs
- ✅ **Free Firestore** - For chat and metadata
- ✅ **Unlimited local storage** - No file size limits
- ✅ **Production ready** - Scalable architecture
- ✅ **Cost effective** - No Firebase Storage fees

The hybrid approach gives you the best of both worlds: Firebase's excellent auth and database services with unlimited local file storage! 