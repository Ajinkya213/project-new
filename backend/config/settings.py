#!/usr/bin/env python3
"""
Application settings and configuration
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration class"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = False
    TESTING = False
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///chat_app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT settings
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24 hours (increased from 1 hour)
    JWT_REFRESH_TOKEN_EXPIRES = 2592000  # 30 days
    
    # CORS settings
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5173,http://localhost:4173,http://127.0.0.1:3000,http://127.0.0.1:5173,http://127.0.0.1:4173').split(',')
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}
    
    # Agent settings
    AGENT_TIMEOUT = 30  # seconds
    MAX_QUERY_LENGTH = 1000
    
    # API Keys
    TAVILY_API_KEY = os.environ.get('TAVILY_API_KEY')
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    QDRANT_URL = os.environ.get('QDRANT_URL', 'http://localhost:6333')
    QDRANT_API_KEY = os.environ.get('QDRANT_API_KEY', '')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///chat_app.db'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # Production security settings
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(config_name=None):
    """Get configuration by name"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    return config.get(config_name, config['default']) 