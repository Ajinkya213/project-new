#!/usr/bin/env python3
"""
Setup script for AI Document Chat Application
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, cwd=None):
    """Run a command and return success status"""
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, check=True, capture_output=True, text=True)
        print(f"✅ {command}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {command}")
        print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 9):
        print("❌ Python 3.9 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def check_node_version():
    """Check if Node.js version is compatible"""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        version = result.stdout.strip()
        major_version = int(version.split('.')[0].replace('v', ''))
        if major_version < 16:
            print("❌ Node.js 16 or higher is required")
            return False
        print(f"✅ {version}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Node.js not found")
        return False

def setup_backend():
    """Setup backend environment"""
    print("\n🔧 Setting up backend...")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return False
    
    # Create virtual environment
    if not run_command("python -m venv venv", cwd=backend_dir):
        return False
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", cwd=backend_dir):
        return False
    
    # Copy environment example
    env_example = backend_dir / "env.example"
    env_file = backend_dir / ".env"
    if env_example.exists() and not env_file.exists():
        shutil.copy(env_example, env_file)
        print("✅ Created .env file from example")
    
    return True

def setup_frontend():
    """Setup frontend environment"""
    print("\n🔧 Setting up frontend...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    # Install dependencies
    if not run_command("npm install", cwd=frontend_dir):
        return False
    
    # Copy environment example
    env_example = frontend_dir / "env.example"
    env_file = frontend_dir / ".env.local"
    if env_example.exists() and not env_file.exists():
        shutil.copy(env_example, env_file)
        print("✅ Created .env.local file from example")
    
    return True

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    
    directories = [
        "backend/uploads",
        "backend/logs",
        "backend/data",
        "backend/instance",
        "data/pdf_images",
        "data/documents"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created {directory}")

def main():
    """Main setup function"""
    print("🚀 Setting up AI Document Chat Application")
    print("=" * 50)
    
    # Check prerequisites
    print("\n📋 Checking prerequisites...")
    if not check_python_version():
        return False
    
    if not check_node_version():
        return False
    
    # Create directories
    create_directories()
    
    # Setup backend
    if not setup_backend():
        print("❌ Backend setup failed")
        return False
    
    # Setup frontend
    if not setup_frontend():
        print("❌ Frontend setup failed")
        return False
    
    print("\n🎉 Setup completed successfully!")
    print("\n📝 Next steps:")
    print("1. Configure your environment variables:")
    print("   - Backend: Edit backend/.env")
    print("   - Frontend: Edit frontend/.env.local")
    print("2. Start the backend: cd backend && python run.py")
    print("3. Start the frontend: cd frontend && npm run dev")
    print("4. Open http://localhost:3000 in your browser")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 