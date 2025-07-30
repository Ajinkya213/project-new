from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import MetaData

# Create SQLAlchemy instance
db = SQLAlchemy()

# Create Migrate instance
migrate = Migrate()

# Naming convention for constraints
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

def init_database(app):
    """Initialize database with the Flask app"""
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Import models to register them with SQLAlchemy
    from .user import User
    from .chat import ChatSession, Message
    
    # Create tables
    with app.app_context():
        db.create_all()
        print("✅ Database tables created successfully!")

def get_db():
    """Get database instance"""
    return db

def close_db(e=None):
    """Close database connection"""
    db.session.remove()

def init_app(app):
    """Initialize database with app"""
    init_database(app)
    
    # Register close_db function to be called when app context ends
    app.teardown_appcontext(close_db) 