from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import os

# Import configuration
from config.settings import config

# Import database
from models.database import init_app as init_database

# Import routes
from routes.auth import auth_bp
from routes.chat import chat_bp
from routes.agent import agent_bp

def create_app(config_name='development'):
    """Application factory pattern"""
    
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    init_database(app)
    
    # Initialize JWT
    jwt = JWTManager(app)
    
    # Initialize CORS
    CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(agent_bp)
    
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
            'message': 'Backend is running successfully'
        }), 200
    
    # Root endpoint
    @app.route('/', methods=['GET'])
    def root():
        return jsonify({
            'message': 'Chat Application API',
            'version': '1.0.0',
            'endpoints': {
                'auth': '/auth',
                'chat': '/chat',
                'agent': '/agent',
                'health': '/health'
            }
        }), 200
    
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    # Get port from environment or default to 8000
    port = int(os.environ.get('PORT', 8000))
    
    # Run the app
    app.run(
        host='0.0.0.0',
        port=port,
        debug=app.config['DEBUG']
    ) 