# Troubleshooting Guide

## Issues Fixed

### 1. Chat Messages Disappearing on Refresh

**Problem**: Chat messages were not being persisted and would disappear when the page was refreshed.

**Solution**: 
- Added local storage fallback in `ChatContext.tsx`
- Messages are now saved to localStorage when backend is not available
- Sessions and messages persist across page refreshes

### 2. Backend Connection Errors

**Problem**: "Failed to fetch" errors when backend server is not running.

**Solution**:
- Added graceful fallback to local storage mode
- Frontend now works even when backend is offline
- Messages are saved locally and can be synced when backend comes back online

### 3. Fast Refresh Issues

**Problem**: React Fast Refresh was incompatible with the `useChat` export.

**Solution**:
- Fixed the `useChat` hook to have explicit return type
- Removed duplicate ReactNode imports

## How to Start the Application

### Option 1: Start Backend First (Recommended)

1. **Start the backend server** (with dependency handling):
   ```bash
   python start_backend_simple.py
   ```
   
   Or if you have missing dependencies:
   ```bash
   pip install cachecontrol firebase-admin flask flask-cors
   python start_backend.py
   ```
   
   Or manually:
   ```bash
   cd backend
   python run.py
   ```

2. **Start the frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

### Option 2: Frontend Only (Local Storage Mode)

If you don't want to run the backend, the frontend will work in local storage mode:

1. **Start only the frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

2. **Features available in local storage mode**:
   - Chat messages are saved locally
   - Sessions persist across refreshes
   - Basic AI responses (fallback mode)
   - All UI functionality works

### Option 3: Minimal Backend (No Firebase Dependencies)

If you're having issues with Firebase dependencies:

1. **Start the minimal backend**:
   ```bash
   cd backend
   python app_minimal.py
   ```

2. **Features available in minimal mode**:
   - Basic chat functionality
   - Session management
   - Simple AI responses
   - No Firebase dependencies required

## Current Status

✅ **Fixed Issues**:
- Chat persistence with localStorage fallback
- Backend connection error handling
- Fast Refresh compatibility
- Graceful degradation when backend is offline

⚠️ **Known Limitations**:
- AI responses are limited when backend is offline
- No real-time sync between devices in local storage mode
- Document processing requires backend

## Testing the Fix

1. **Test persistence**: Send a message, refresh the page, verify the message is still there
2. **Test offline mode**: Stop the backend server, send messages, verify they're saved locally
3. **Test online mode**: Start the backend, verify messages sync properly

## File Changes Made

- `frontend/src/contexts/ChatContext.tsx`: Added localStorage persistence
- `frontend/src/components/userboard/MainContent.tsx`: Improved error handling
- `frontend/src/utils/backendHealth.ts`: Added health check utility
- `start_backend.py`: Created backend startup script
- `start_backend_simple.py`: Created dependency-aware startup script
- `backend/app_minimal.py`: Created minimal backend without Firebase
- `backend/requirements.txt`: Added missing cachecontrol dependency

The application should now work reliably with or without the backend server running. 