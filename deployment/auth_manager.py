import json
import jwt
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict
import hashlib

class AuthManager:
    def __init__(self):
        self.users_file = Path("data/users.json")
        self.sessions_file = Path("data/sessions.json")
        self.secret_key = "bhiv-secret-key-2024"
        self.users_file.parent.mkdir(exist_ok=True)
        self.load_data()
    
    def load_data(self):
        """Load users and sessions from files"""
        # Load users
        if self.users_file.exists():
            with open(self.users_file, 'r') as f:
                self.users = json.load(f)
        else:
            self.users = {"admin": {"password": self.hash_password("admin123"), "role": "admin"}}
            self.save_users()
        
        # Load sessions
        if self.sessions_file.exists():
            with open(self.sessions_file, 'r') as f:
                self.sessions = json.load(f)
        else:
            self.sessions = {}
    
    def save_users(self):
        """Save users to file"""
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f, indent=2)
    
    def save_sessions(self):
        """Save sessions to file"""
        with open(self.sessions_file, 'w') as f:
            json.dump(self.sessions, f, indent=2)
    
    def hash_password(self, password: str) -> str:
        """Hash password"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_token(self, username: str) -> str:
        """Create JWT token"""
        payload = {
            "username": username,
            "exp": datetime.utcnow() + timedelta(days=7),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm="HS256")
    
    def verify_token(self, token: str) -> Optional[str]:
        """Verify JWT token and return username"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload.get("username")
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def login(self, username: str, password: str) -> Dict:
        """Login user and create session"""
        if username not in self.users:
            return {"success": False, "message": "User not found"}
        
        if self.users[username]["password"] != self.hash_password(password):
            return {"success": False, "message": "Invalid password"}
        
        # Create token and session
        token = self.create_token(username)
        session_id = hashlib.md5(f"{username}{datetime.now()}".encode()).hexdigest()
        
        self.sessions[session_id] = {
            "username": username,
            "token": token,
            "created_at": datetime.now().isoformat(),
            "last_access": datetime.now().isoformat()
        }
        self.save_sessions()
        
        return {
            "success": True,
            "token": token,
            "session_id": session_id,
            "username": username,
            "role": self.users[username]["role"]
        }
    
    def auto_login(self, session_id: str = None, token: str = None) -> Optional[Dict]:
        """Auto login using session_id or token"""
        # Try session_id first
        if session_id and session_id in self.sessions:
            session = self.sessions[session_id]
            username = self.verify_token(session["token"])
            if username:
                # Update last access
                session["last_access"] = datetime.now().isoformat()
                self.save_sessions()
                return {
                    "success": True,
                    "username": username,
                    "role": self.users[username]["role"],
                    "session_id": session_id,
                    "token": session["token"]
                }
        
        # Try direct token
        if token:
            username = self.verify_token(token)
            if username and username in self.users:
                return {
                    "success": True,
                    "username": username,
                    "role": self.users[username]["role"],
                    "token": token
                }
        
        return None
    
    def logout(self, session_id: str):
        """Logout user and remove session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            self.save_sessions()
            return {"success": True, "message": "Logged out"}
        return {"success": False, "message": "Session not found"}
    
    def register(self, username: str, password: str, role: str = "user") -> Dict:
        """Register new user"""
        if username in self.users:
            return {"success": False, "message": "User already exists"}
        
        self.users[username] = {
            "password": self.hash_password(password),
            "role": role,
            "created_at": datetime.now().isoformat()
        }
        self.save_users()
        
        return {"success": True, "message": "User created successfully"}

# Global auth manager instance
auth_manager = AuthManager()