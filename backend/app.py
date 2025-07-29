# C:\Users\Ajinkya\Desktop\project\backend\app.py

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime, timezone
from passlib.context import CryptContext
import os
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta # To set token expiry

# Load environment variables from .env file
load_dotenv()

# --- Flask App Configuration ---
app = Flask(__name__)

# MySQL connection string using pymysql
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("MYSQL_DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "a-very-random-secret-key-that-you-must-change-in-prod")
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY") # ADD THIS LINE
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1) # ADD THIS LINE (Token valid for 1 hour)

db = SQLAlchemy(app)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

jwt = JWTManager(app) # ADD THIS LINE

# --- Database Model (User) ---
class User(db.Model):
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    hashed_password = Column(String(128), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<User {self.username}>'

    def verify_password(self, password: str):
        return pwd_context.verify(password, self.hashed_password)

    def hash_password(self, password: str):
        return pwd_context.hash(password)

# C:\Users\Ajinkya\Desktop\project\backend\app.py
# ... (Your existing User model code) ...

# --- ChatSession Model ---
class ChatSession(db.Model):
    __tablename__ = "chat_sessions"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    owner_id = Column(Integer, db.ForeignKey("user.id"), nullable=False)

    # Relationships
    owner = db.relationship("User", backref=db.backref("chat_sessions", lazy=True, cascade="all, delete-orphan"))
    # This defines the one-to-many: a session has many messages.
    # When a session is deleted, its messages will also be deleted (delete-orphan).
    messages = db.relationship("ChatMessage", backref="session_obj", lazy=True, cascade="all, delete-orphan") # Renamed backref to avoid clash

    def __repr__(self):
        return f'<ChatSession {self.title}>'

# --- ChatMessage Model ---
class ChatMessage(db.Model):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String(4096), nullable=False)
    is_user_message = Column(Boolean, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Foreign Key to ChatSession
    session_id = Column(Integer, db.ForeignKey("chat_sessions.id"), nullable=False)

    # The 'session_obj' backref is automatically created on ChatMessage by ChatSession's 'messages' relationship.
    # You do NOT need a db.relationship line here for 'session_obj' or 'session'.

    def __repr__(self):
        return f'<ChatMessage {self.id}>'

# --- Database Initialization (This block remains the same) ---
with app.app_context():
    print("Attempting to create/check database tables...")
    db.create_all() # This will now create ChatSession, ChatMessage, and Document tables
    print("Database tables created/checked.")

# ... (Rest of your app.py code, including routes) ...

# --- Database Initialization ---
with app.app_context():
    print("Attempting to create/check database tables...")
    db.create_all()
    print("Database tables created/checked.")

# --- API Endpoints ---

@app.route("/")
def home():
    return jsonify({"message": "Hello from Simple Flask & MySQL Backend! Try POST to /users."})

@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not all([username, email, password]):
        return jsonify({"error": "Username, email, and password are required"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 409
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 409

    hashed_password = pwd_context.hash(password)

    new_user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        is_active=True,
        is_superuser=False
    )

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
            "is_active": new_user.is_active,
            "created_at": new_user.created_at.isoformat()
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating user: {e}")
        return jsonify({"error": "Could not create user", "details": str(e)}), 500

@app.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    users_list = []
    for user in users:
        users_list.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat()
        })
    return jsonify(users_list), 200

# ... (existing / and /users routes)

@app.route("/login", methods=["POST"])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400

    user = User.query.filter_by(username=username).first()

    if not user or not user.verify_password(password):
        return jsonify({"msg": "Bad username or password"}), 401 # 401 Unauthorized

        # --- ADD THESE DEBUG PRINTS ---
    #print(f"DEBUG: user.id type: {type(user.id)}")
    #print(f"DEBUG: user.id value: {user.id}")
    # --- END DEBUG PRINTS ---

    # Identity can be anything that identifies the user (e.g., user.id, user.username)
    access_token = create_access_token(identity=str(user.id))
    return jsonify(access_token=access_token), 200

# --- Add a Sample Protected Route ---
@app.route("/protected", methods=["GET"])
@jwt_required() # This decorator protects the route
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user_id = get_jwt_identity()
    user = user = db.session.get(User, current_user_id) # Retrieve the user object if needed
    if not user:
        return jsonify({"msg": "User not found"}), 404
    return jsonify(logged_in_as=user.username, message="You accessed a protected route!"), 200

# ... (rest of your app.py)

# --- Chat Session Endpoints ---

@app.route("/chat_sessions", methods=["POST"])
@jwt_required() # Requires a valid JWT to access
def create_chat_session():
    #print("DEBUG: Inside create_chat_session function.")
    try:
        current_user_id = get_jwt_identity()
        #print(f"DEBUG: JWT Identity (current_user_id): {current_user_id}, Type: {type(current_user_id)}")

        if current_user_id is None:
            #print("DEBUG: current_user_id is None after get_jwt_identity()")
            return jsonify({"msg": "Token identity missing"}), 401 # Should ideally be caught by jwt_required itself but good to check

        user = user = db.session.get(User, current_user_id)
        #print(f"DEBUG: Retrieved user: {user}")

        if not user:
            #print(f"DEBUG: User not found for ID: {current_user_id}")
            return jsonify({"msg": "User not found for token identity"}), 404

        data = request.get_json()
        #print(f"DEBUG: Request JSON data: {data}")

        if not data:
            return jsonify({"error": "Invalid JSON body"}), 400

        title = data.get("title")
        #print(f"DEBUG: Received title: {title}")

        if not title:
            return jsonify({"error": "Title is required for a chat session"}), 400

        new_session = ChatSession(
            title=title,
            owner=user # Automatically sets owner_id via relationship
        )

        db.session.add(new_session)
        db.session.commit()
        #print("DEBUG: Chat session committed successfully.")
        return jsonify({
            "id": new_session.id,
            "title": new_session.title,
            "owner_id": new_session.owner_id,
            "created_at": new_session.created_at.isoformat()
        }), 201
    except Exception as e:
        db.session.rollback()
        #print(f"DEBUG: An unexpected error occurred: {e}")
        return jsonify({"error": "Internal server error during chat session creation", "details": str(e)}), 500


@app.route("/chat_sessions", methods=["GET"])
@jwt_required() # Requires a valid JWT to access
def get_chat_sessions():
    current_user_id = get_jwt_identity()
    user = user = db.session.get(User, current_user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    # Retrieve chat sessions owned by the current user
    sessions = ChatSession.query.filter_by(owner=user).all()
    sessions_list = []
    for session in sessions:
        sessions_list.append({
            "id": session.id,
            "title": session.title,
            "owner_id": session.owner_id,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat()
        })
    return jsonify(sessions_list), 200

# ... (Rest of your app.py code, including if __name__ == '__main__':) ...

# C:\Users\Ajinkya\Desktop\project\backend\app.py
# ... (Your existing /chat_sessions routes) ...

# --- Chat Message Endpoints ---
@app.route("/chat_sessions/<int:session_id>/messages", methods=["POST"])
@jwt_required()
def send_chat_message(session_id):
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id) # Using db.session.get()
    if not user:
        return jsonify({"msg": "User not found"}), 404

    session = db.session.get(ChatSession, session_id) # Using db.session.get()
    if not session:
        return jsonify({"error": "Chat session not found"}), 404

    # Ensure the user owns this session before adding messages
    if session.owner_id != user.id:
        return jsonify({"error": "You do not have permission to add messages to this session"}), 403 # Forbidden

    data = request.get_json()
    content = data.get("content")
    is_user_message = data.get("is_user_message", True) # Default to True if not provided

    if not content:
        return jsonify({"error": "Message content is required"}), 400

    # THIS IS THE CRITICAL CHANGE:
    new_message = ChatMessage(
        content=content,
        is_user_message=is_user_message,
        session_id=session.id # <--- THIS MUST BE session_id=session.id
    )

    try:
        db.session.add(new_message)
        db.session.commit()
        return jsonify({
            "id": new_message.id,
            "session_id": new_message.session_id,
            "content": new_message.content,
            "is_user_message": new_message.is_user_message,
            "created_at": new_message.created_at.isoformat()
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error sending chat message: {e}")
        return jsonify({"error": "Could not send message", "details": str(e)}), 500


@app.route("/chat_sessions/<int:session_id>/messages", methods=["GET"])
@jwt_required()
def get_chat_messages(session_id):
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id) # Using db.session.get()
    if not user:
        return jsonify({"msg": "User not found"}), 404

    session = db.session.get(ChatSession, session_id) # Using db.session.get()
    if not session:
        return jsonify({"error": "Chat session not found"}), 404

    # Ensure the user owns this session before retrieving messages
    if session.owner_id != user.id:
        return jsonify({"error": "You do not have permission to view messages in this session"}), 403 # Forbidden

    messages = ChatMessage.query.filter_by(session=session).order_by(ChatMessage.created_at).all()
    messages_list = []
    for message in messages:
        messages_list.append({
            "id": message.id,
            "session_id": message.session_id,
            "content": message.content,
            "is_user_message": message.is_user_message,
            "created_at": message.created_at.isoformat()
        })
    return jsonify(messages_list), 200

# ... (Rest of your app.py code) ...

# --- Run the App ---
if __name__ == '__main__':
    app.run(debug=True, port=8000)