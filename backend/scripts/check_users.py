#!/usr/bin/env python3
"""
Check existing users in the database
"""

from app import create_app
from models.database import db
from models.user import User

def check_users():
    """Check all users in the database"""
    app = create_app()
    
    with app.app_context():
        users = User.query.all()
        
        print(f"📊 Found {len(users)} users in database:")
        print("=" * 50)
        
        for user in users:
            print(f"ID: {user.id}")
            print(f"Username: {user.username}")
            print(f"Email: {user.email}")
            print(f"Active: {user.is_active}")
            print(f"Created: {user.created_at}")
            print("-" * 30)
        
        if not users:
            print("No users found in database")
        
        return users

def test_user_login(username, password):
    """Test login for a specific user"""
    app = create_app()
    
    with app.app_context():
        user = User.find_by_username(username)
        if not user:
            user = User.find_by_email(username)
        
        if user:
            print(f"✅ User found: {user.username}")
            if user.check_password(password):
                print("✅ Password is correct")
                return True
            else:
                print("❌ Password is incorrect")
                return False
        else:
            print(f"❌ User not found: {username}")
            return False

if __name__ == "__main__":
    print("🔍 Checking database users...")
    users = check_users()
    
    if users:
        print("\n🔑 Testing login for first user...")
        first_user = users[0]
        test_user_login(first_user.username, "TestPass123!")
    else:
        print("\n💡 No users found. You can create a test user manually.") 