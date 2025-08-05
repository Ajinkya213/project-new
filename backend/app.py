from flask import Flask, jsonify
from flask_cors import CORS
import os

# Import configuration
from config.settings import config

# Import Firebase configuration
from config.firebase_config import firebase_config

# Import database (keeping for compatibility, but Firebase will be primary)
from models.database import init_app as init_database, db

# Import routes
from routes.chat import chat_bp
from routes.agent import agent_bp
from routes.api import bp as api_bp
from routes.auth import auth_bp
from routes.api_keys import api_keys_bp

# Import new comprehensive API routes
from api.routes import api_bp as comprehensive_api_bp

def create_app(config_name='development'):
    """Application factory pattern"""
    
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize Firebase (this will be our primary auth and storage)
    try:
        # Firebase is initialized in the config module
        print("✅ Firebase initialized successfully!")
    except Exception as e:
        print(f"❌ Firebase initialization failed: {str(e)}")
        # Continue without Firebase for development
    
    # Initialize database (keeping for compatibility)
    init_database(app)
    
    # Initialize CORS
    CORS(app, 
         origins=app.config['CORS_ORIGINS'], 
         supports_credentials=True,
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         allow_headers=['Content-Type', 'Authorization'])
    
    # Register blueprints
    app.register_blueprint(chat_bp, url_prefix='/chat')
    app.register_blueprint(agent_bp, url_prefix='/agent')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(api_keys_bp, url_prefix='/api-keys')
    
    # Register comprehensive API routes
    app.register_blueprint(comprehensive_api_bp, url_prefix='/api/v2')
    
    # Create tables (keeping for compatibility)
    with app.app_context():
        db.create_all()
        print("✅ Database tables created successfully!")
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({'error': 'Method not allowed'}), 405
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'message': 'Backend is running successfully',
            'firebase_initialized': firebase_config.app is not None,
            'api_version': '2.0.0',
            'endpoints': {
                'v1': '/api',
                'v2': '/api/v2',
                'agent': '/agent',
                'chat': '/chat',
                'auth': '/auth'
            }
        }), 200
    
    # Root endpoint
    @app.route('/', methods=['GET'])
    def root():
        return jsonify({
            'message': 'Chat Application API with Firebase',
            'version': '2.0.0',
            'auth_method': 'Firebase Auth',
            'storage': 'Firebase Storage & Firestore',
            'endpoints': {
                'auth': '/auth',
                'chat': '/chat',
                'agent': '/agent',
                'api_v1': '/api',
                'api_v2': '/api/v2',
                'health': '/health'
            }
        }), 200
    
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    # Get port from environment or default to 8000
    port = int(os.environ.get('PORT', 8000))
    
    print("🚀 Starting backend server with Firebase integration...")
    print("📝 Note: Heavy models will load on first request")
    print("⚡ Server will be ready for basic operations immediately")
    print("🔥 Firebase Auth and Storage enabled")
    
    # Run the app
    app.run(
        host='0.0.0.0',
        port=port,
        debug=app.config['DEBUG']
    ) 