import os
import firebase_admin
from firebase_admin import credentials, auth, firestore
from dotenv import load_dotenv

load_dotenv()

class FirebaseConfig:
    """Firebase configuration and initialization (Auth + Firestore only)"""
    
    def __init__(self):
        self.app = None
        self.db = None
        self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Initialize Firebase with service account"""
        try:
            # Check if Firebase is already initialized
            if not firebase_admin._apps:
                # Use the service account file directly
                service_account_path = 'serviceAccountKey.json'
                
                if os.path.exists(service_account_path):
                    # Initialize with service account file
                    cred = credentials.Certificate(service_account_path)
                    self.app = firebase_admin.initialize_app(cred, {
                        'projectId': 'aim-cdac'
                    })
                    print("✅ Firebase initialized successfully!")
                else:
                    # Initialize with default credentials (for production)
                    self.app = firebase_admin.initialize_app()
                    print("✅ Firebase initialized with default credentials!")
            else:
                self.app = firebase_admin.get_app()
                print("✅ Firebase already initialized!")
            
            # Initialize Firestore
            self.db = firestore.client()
            
        except Exception as e:
            print(f"❌ Firebase initialization failed: {str(e)}")
            raise
    
    def get_auth(self):
        """Get Firebase Auth instance"""
        return auth
    
    def get_firestore(self):
        """Get Firestore client"""
        return self.db
    
    def verify_id_token(self, id_token):
        """Verify Firebase ID token"""
        try:
            decoded_token = auth.verify_id_token(id_token)
            return decoded_token
        except Exception as e:
            print(f"Token verification failed: {str(e)}")
            return None
    
    def get_user_by_uid(self, uid):
        """Get user by Firebase UID"""
        try:
            user = auth.get_user(uid)
            return user
        except Exception as e:
            print(f"Failed to get user by UID: {str(e)}")
            return None
    
    def create_user(self, email, password, display_name=None):
        """Create new user in Firebase Auth"""
        try:
            user_properties = {
                'email': email,
                'password': password,
                'email_verified': False
            }
            
            if display_name:
                user_properties['display_name'] = display_name
            
            user = auth.create_user(**user_properties)
            return user
        except Exception as e:
            print(f"Failed to create user: {str(e)}")
            return None
    
    def delete_user(self, uid):
        """Delete user from Firebase Auth"""
        try:
            auth.delete_user(uid)
            return True
        except Exception as e:
            print(f"Failed to delete user: {str(e)}")
            return False

# Global Firebase instance
firebase_config = FirebaseConfig() 