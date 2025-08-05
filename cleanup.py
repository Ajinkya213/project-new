#!/usr/bin/env python3
"""
Cleanup script to prepare codebase for GitHub
"""

import os
import shutil
import glob
from pathlib import Path

def remove_temp_files():
    """Remove temporary files and directories"""
    print("🧹 Cleaning up temporary files...")
    
    # Files to remove
    temp_files = [
        "*.pyc",
        "*.pyo",
        "*.pyd",
        "__pycache__",
        "*.log",
        "*.tmp",
        "*.temp",
        ".DS_Store",
        "Thumbs.db",
        "*.swp",
        "*.swo",
        "*~"
    ]
    
    # Directories to remove
    temp_dirs = [
        "__pycache__",
        ".pytest_cache",
        ".coverage",
        "htmlcov",
        "dist",
        "build",
        "node_modules",
        ".venv",
        "venv",
        "env",
        "temp",
        "tmp"
    ]
    
    # Remove temp files
    for pattern in temp_files:
        for file_path in glob.glob(pattern, recursive=True):
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"✅ Removed file: {file_path}")
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                    print(f"✅ Removed directory: {file_path}")
            except Exception as e:
                print(f"⚠️  Could not remove {file_path}: {e}")
    
    # Remove temp directories
    for dir_name in temp_dirs:
        for dir_path in glob.glob(f"**/{dir_name}", recursive=True):
            try:
                if os.path.isdir(dir_path):
                    shutil.rmtree(dir_path)
                    print(f"✅ Removed directory: {dir_path}")
            except Exception as e:
                print(f"⚠️  Could not remove {dir_path}: {e}")

def clean_backend():
    """Clean backend directory"""
    print("🧹 Cleaning backend...")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        return
    
    # Remove specific backend temp files
    backend_temp_files = [
        "backend/instance/*",
        "backend/uploads/*",
        "backend/logs/*",
        "backend/*.pyc",
        "backend/__pycache__",
        "backend/.env",
        "backend/serviceAccountKey.json"
    ]
    
    for pattern in backend_temp_files:
        for file_path in glob.glob(pattern):
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"✅ Removed: {file_path}")
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                    print(f"✅ Removed: {file_path}")
            except Exception as e:
                print(f"⚠️  Could not remove {file_path}: {e}")

def clean_frontend():
    """Clean frontend directory"""
    print("🧹 Cleaning frontend...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        return
    
    # Remove specific frontend temp files
    frontend_temp_files = [
        "frontend/dist",
        "frontend/build",
        "frontend/node_modules",
        "frontend/.env.local",
        "frontend/*.log"
    ]
    
    for pattern in frontend_temp_files:
        for file_path in glob.glob(pattern):
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"✅ Removed: {file_path}")
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                    print(f"✅ Removed: {file_path}")
            except Exception as e:
                print(f"⚠️  Could not remove {file_path}: {e}")

def create_gitignore():
    """Ensure .gitignore is properly set up"""
    print("📝 Checking .gitignore...")
    
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/
cover/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
.pybuilder/
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# pipenv
Pipfile.lock

# poetry
poetry.lock

# pdm
.pdm.toml

# PEP 582
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# pytype static type analyzer
.pytype/

# Cython debug symbols
cython_debug/

# PyCharm
.idea/

# VS Code
.vscode/

# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# React/Vite
dist/
build/

# Environment variables
.env.local
.env.development.local
.env.test.local
.env.production.local

# Firebase
serviceAccountKey.json
firebase-debug.log
firebase-debug.*.log

# Model cache
model_cache/
models/

# Uploads and data
uploads/
data/pdf_images/
data/documents/

# Instance data
instance/

# Temporary files
*.tmp
*.temp
temp/

# Logs
*.log
logs/

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Windows
*.lnk

# Application specific
backend/instance/
backend/uploads/
backend/model_cache/
frontend/dist/
frontend/build/
frontend/.env.local

# API keys and secrets
*.key
*.pem
*.p12
*.pfx
secrets.json
config.json

# Database files
*.db
*.sqlite
*.sqlite3

# Cache directories
.cache/
cache/

# Test files
test_*.py
*_test.py
tests/temp/

# Documentation build
docs/build/
docs/_build/

# Coverage reports
htmlcov/
.coverage
.coverage.*

# Backup files
*.bak
*.backup
*~

# IDE files
.vscode/
.idea/
*.swp
*.swo
*~

# OS specific
.DS_Store
Thumbs.db
"""
    
    with open(".gitignore", "w") as f:
        f.write(gitignore_content)
    
    print("✅ .gitignore updated")

def main():
    """Main cleanup function"""
    print("🧹 Cleaning up codebase for GitHub...")
    print("=" * 50)
    
    # Remove temporary files
    remove_temp_files()
    
    # Clean backend
    clean_backend()
    
    # Clean frontend
    clean_frontend()
    
    # Update .gitignore
    create_gitignore()
    
    print("\n✅ Cleanup completed!")
    print("\n📝 Ready for GitHub:")
    print("1. Review the changes")
    print("2. Add files: git add .")
    print("3. Commit: git commit -m 'Initial commit'")
    print("4. Push: git push origin main")

if __name__ == "__main__":
    main() 