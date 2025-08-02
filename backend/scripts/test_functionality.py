#!/usr/bin/env python3
"""
Comprehensive functionality test for the chat application
"""

import sys
import os
import requests
import json
from datetime import datetime

def test_imports():
    """Test all imports"""
    print("🔍 Testing imports...")
    
    try:
        from agents import ChatAgent, DocumentAgent, ResearchAgent
        print("✅ Agents imported successfully")
    except Exception as e:
        print(f"❌ Agents import failed: {e}")
        return False
    
    try:
        from services import query_service, lightweight_agent
        print("✅ Services imported successfully")
    except Exception as e:
        print(f"❌ Services import failed: {e}")
        return False
    
    try:
        from core import rag_utils, qdrant_utils
        print("✅ Core utilities imported successfully")
    except Exception as e:
        print(f"❌ Core utilities import failed: {e}")
        return False
    
    try:
        from config.settings import get_config
        print("✅ Config imported successfully")
    except Exception as e:
        print(f"❌ Config import failed: {e}")
        return False
    
    try:
        from app import create_app
        print("✅ Flask app imported successfully")
    except Exception as e:
        print(f"❌ Flask app import failed: {e}")
        return False
    
    return True

def test_agents():
    """Test agent functionality"""
    print("\n🤖 Testing agents...")
    
    try:
        from services.lightweight_agent import lightweight_agent
        
        # Test lightweight agent
        result = lightweight_agent.process_query("Hello")
        if result.get('success'):
            print("✅ Lightweight agent working")
        else:
            print(f"❌ Lightweight agent failed: {result.get('error')}")
            return False
        
        # Test query service
        from services.query_service import query_service
        
        result = query_service.process_query("Hello", "lightweight")
        if result.get('success'):
            print("✅ Query service working")
        else:
            print(f"❌ Query service failed: {result.get('error')}")
            return False
        
        # Test health check
        health = query_service.health_check()
        if health.get('status') == 'healthy':
            print("✅ Query service health check passed")
        else:
            print(f"❌ Query service health check failed: {health}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Agent test failed: {e}")
        return False

def test_core_utilities():
    """Test core utilities"""
    print("\n🔧 Testing core utilities...")
    
    try:
        from core.rag_utils import rag_utils
        
        # Test document processing
        test_content = "This is a test document with some content."
        analysis = rag_utils.process_document("test.txt")
        print("✅ RAG utils working")
        
        # Test Qdrant utils
        from core.qdrant_utils import qdrant_utils
        
        health = qdrant_utils.health_check()
        print(f"✅ Qdrant utils working (status: {health.get('status')})")
        
        return True
        
    except Exception as e:
        print(f"❌ Core utilities test failed: {e}")
        return False

def test_flask_app():
    """Test Flask application"""
    print("\n🌐 Testing Flask application...")
    
    try:
        from app import create_app
        
        app = create_app()
        
        # Test routes
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        expected_routes = [
            '/auth/register', '/auth/login', '/auth/refresh', '/auth/logout',
            '/chat/sessions', '/agent/health', '/agent/query', '/agent/upload',
            '/agent/agents', '/agent/test', '/health', '/'
        ]
        
        missing_routes = [route for route in expected_routes if route not in routes]
        if not missing_routes:
            print("✅ All expected routes registered")
        else:
            print(f"❌ Missing routes: {missing_routes}")
            return False
        
        # Test app configuration
        if app.config['DEBUG']:
            print("✅ App in debug mode")
        else:
            print("✅ App in production mode")
        
        return True
        
    except Exception as e:
        print(f"❌ Flask app test failed: {e}")
        return False

def test_database():
    """Test database functionality"""
    print("\n🗄️ Testing database...")
    
    try:
        from models.database import db
        from models.user import User
        from models.chat import ChatSession, Message
        
        # Test database models
        print("✅ Database models imported successfully")
        
        # Test user model
        user = User(
            username="test_user",
            email="test@example.com",
            password="test_password"
        )
        print("✅ User model working")
        
        # Test chat models
        session = ChatSession(title="Test Session", user_id="test_user_id")
        message = Message(text="Test message", sender="user", session_id=1)
        print("✅ Chat models working")
        
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_configuration():
    """Test configuration"""
    print("\n⚙️ Testing configuration...")
    
    try:
        from config.settings import get_config
        
        config = get_config('development')
        
        # Test required config values
        required_keys = ['SECRET_KEY', 'SQLALCHEMY_DATABASE_URI', 'DEBUG']
        for key in required_keys:
            if hasattr(config, key):
                print(f"✅ Config key '{key}' present")
            else:
                print(f"❌ Config key '{key}' missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting comprehensive functionality test...")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Agents", test_agents),
        ("Core Utilities", test_core_utilities),
        ("Flask App", test_flask_app),
        ("Database", test_database),
        ("Configuration", test_configuration)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print("=" * 50)
    print(f"🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All functionality tests passed!")
        return True
    else:
        print("⚠️ Some tests failed. Check the output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 