#!/usr/bin/env python3
"""
Create a test user with known credentials
"""

from app import create_app
from models.database import db
from models.user import User

def create_test_user():
    """Create a test user"""
    app = create_app()
    
    with app.app_context():
        # Check if test user already exists
        existing_user = User.find_by_username("testuser")
        if existing_user:
            print("✅ Test user already exists")
            return existing_user
        
        # Create new test user
        test_user = User(
            username="testuser",
            email="testuser@example.com",
            password="TestPass123!"
        )
        
        try:
            db.session.add(test_user)
            db.session.commit()
            print("✅ Test user created successfully")
            print(f"Username: {test_user.username}")
            print(f"Email: {test_user.email}")
            print(f"ID: {test_user.id}")
            return test_user
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating test user: {e}")
            return None

def test_login():
    """Test login with the test user"""
    app = create_app()
    
    with app.app_context():
        user = User.find_by_username("testuser")
        if user:
            print(f"✅ Found user: {user.username}")
            if user.check_password("TestPass123!"):
                print("✅ Password check successful")
                return True
            else:
                print("❌ Password check failed")
                return False
        else:
            print("❌ Test user not found")
            return False

if __name__ == "__main__":
    print("🔧 Creating test user...")
    user = create_test_user()
    
    if user:
        print("\n🔑 Testing login...")
        success = test_login()
        if success:
            print("🎉 Test user is ready for login!")
        else:
            print("⚠️ Login test failed")
    else:
        print("❌ Could not create test user") 