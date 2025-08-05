#!/usr/bin/env python3
"""
Quick start script for AI Document Chat Application
"""

import os
import sys
import subprocess
import time
import signal
import threading
from pathlib import Path

# Global variables to track processes
backend_process = None
frontend_process = None

def signal_handler(signum, frame):
    """Handle Ctrl+C to gracefully shutdown"""
    print("\n🛑 Shutting down...")
    if backend_process:
        backend_process.terminate()
    if frontend_process:
        frontend_process.terminate()
    sys.exit(0)

def run_backend():
    """Run the backend server"""
    global backend_process
    backend_dir = Path("backend")
    
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return False
    
    print("🚀 Starting backend server...")
    try:
        backend_process = subprocess.Popen(
            ["python", "run.py"],
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a moment for server to start
        time.sleep(3)
        
        if backend_process.poll() is None:
            print("✅ Backend server started at http://localhost:8000")
            return True
        else:
            stdout, stderr = backend_process.communicate()
            print(f"❌ Backend failed to start: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return False

def run_frontend():
    """Run the frontend development server"""
    global frontend_process
    frontend_dir = Path("frontend")
    
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    print("🚀 Starting frontend server...")
    try:
        frontend_process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a moment for server to start
        time.sleep(5)
        
        if frontend_process.poll() is None:
            print("✅ Frontend server started at http://localhost:3000")
            return True
        else:
            stdout, stderr = frontend_process.communicate()
            print(f"❌ Frontend failed to start: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return False

def check_dependencies():
    """Check if all dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    # Check backend dependencies
    backend_dir = Path("backend")
    if backend_dir.exists():
        requirements_file = backend_dir / "requirements.txt"
        if requirements_file.exists():
            print("✅ Backend requirements found")
        else:
            print("❌ Backend requirements.txt not found")
            return False
    
    # Check frontend dependencies
    frontend_dir = Path("frontend")
    if frontend_dir.exists():
        package_file = frontend_dir / "package.json"
        if package_file.exists():
            print("✅ Frontend package.json found")
        else:
            print("❌ Frontend package.json not found")
            return False
    
    return True

def main():
    """Main function"""
    print("🚀 Starting AI Document Chat Application")
    print("=" * 50)
    
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Dependencies check failed")
        return False
    
    # Start backend
    if not run_backend():
        print("❌ Failed to start backend")
        return False
    
    # Start frontend
    if not run_frontend():
        print("❌ Failed to start frontend")
        return False
    
    print("\n🎉 Application started successfully!")
    print("📱 Frontend: http://localhost:3000")
    print("🔧 Backend: http://localhost:8000")
    print("📊 Health Check: http://localhost:8000/health")
    print("\nPress Ctrl+C to stop the application")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 