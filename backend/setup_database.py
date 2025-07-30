#!/usr/bin/env python3
"""
Database Setup Script
Creates MySQL database and tables
"""

import pymysql
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def create_database():
    """Create MySQL database if it doesn't exist"""
    
    # Get database configuration
    host = os.getenv('MYSQL_HOST', 'localhost')
    port = int(os.getenv('MYSQL_PORT', 3306))
    user = os.getenv('MYSQL_USER', 'root')
    password = os.getenv('MYSQL_PASSWORD', '')
    database = os.getenv('MYSQL_DATABASE', 'chat_app')
    
    try:
        # Connect to MySQL server (without specifying database)
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            charset='utf8mb4'
        )
        
        cursor = connection.cursor()
        
        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"✅ Database '{database}' created/verified successfully!")
        
        # Use the database
        cursor.execute(f"USE {database}")
        
        # Create tables
        create_tables(cursor)
        
        connection.commit()
        connection.close()
        
        print("✅ Database setup completed successfully!")
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        print("Please check your MySQL configuration in .env file")

def create_tables(cursor):
    """Create database tables"""
    
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id VARCHAR(255) PRIMARY KEY,
            username VARCHAR(80) UNIQUE NOT NULL,
            email VARCHAR(120) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE,
            is_verified BOOLEAN DEFAULT FALSE,
            INDEX idx_username (username),
            INDEX idx_email (email)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """)
    
    # Chat sessions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            user_id VARCHAR(255) NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_user_id (user_id),
            INDEX idx_created_at (created_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """)
    
    # Messages table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            text TEXT NOT NULL,
            sender VARCHAR(10) NOT NULL,
            session_id INT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            is_deleted BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE,
            INDEX idx_session_id (session_id),
            INDEX idx_created_at (created_at),
            INDEX idx_sender (sender)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """)
    
    # Documents table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INT AUTO_INCREMENT PRIMARY KEY,
            filename VARCHAR(255) NOT NULL,
            original_filename VARCHAR(255) NOT NULL,
            file_path VARCHAR(500) NOT NULL,
            file_size INT NOT NULL,
            file_type VARCHAR(100) NOT NULL,
            user_id VARCHAR(255) NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_user_id (user_id),
            INDEX idx_created_at (created_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """)
    
    print("✅ Database tables created successfully!")

if __name__ == "__main__":
    print("🔧 Setting up database...")
    create_database() 