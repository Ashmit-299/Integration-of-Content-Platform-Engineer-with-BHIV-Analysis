# security/auth.py - Professional Authentication & Authorization
import os
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import secrets
import logging

logger = logging.getLogger(__name__)

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Security scheme
security = HTTPBearer()

class UserRole:
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"

class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[str] = None
    roles: List[str] = []

class User(BaseModel):
    id: str
    username: str
    email: str
    roles: List[str]
    is_active: bool = True
    created_at: datetime
    last_login: Optional[datetime] = None

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    roles: List[str] = [UserRole.USER]

class UserLogin(BaseModel):
    username: str
    password: str

class AuthManager:
    """Professional authentication and authorization manager"""
    
    def __init__(self):
        self.users_db = {}  # In production, use proper database
        self.refresh_tokens = {}  # Store refresh tokens
        self._create_default_admin()
    
    def _create_default_admin(self):
        """Create default admin user"""
        admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
        
        if "admin" not in self.users_db:
            hashed_password = self.hash_password(admin_password)
            self.users_db["admin"] = {
                "id": "admin",
                "username": "admin",
                "email": "admin@bhiv.platform",
                "password_hash": hashed_password,
                "roles": [UserRole.ADMIN],
                "is_active": True,
                "created_at": datetime.now(),
                "last_login": None
            }
            logger.info("Default admin user created")
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def create_access_token(self, data: Dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    def create_refresh_token(self, user_id: str) -> str:
        """Create refresh token"""
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode = {
            "user_id": user_id,
            "exp": expire,
            "type": "refresh"
        }
        
        token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        self.refresh_tokens[token] = user_id
        
        return token
    
    def verify_token(self, token: str) -> TokenData:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            username: str = payload.get("sub")
            user_id: str = payload.get("user_id")
            roles: List[str] = payload.get("roles", [])
            
            if username is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            return TokenData(username=username, user_id=user_id, roles=roles)
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user credentials"""
        user = self.users_db.get(username)
        
        if not user:
            return None
        
        if not user["is_active"]:
            return None
        
        if not self.verify_password(password, user["password_hash"]):
            return None
        
        # Update last login
        user["last_login"] = datetime.now()
        
        return user
    
    def create_user(self, user_data: UserCreate) -> User:
        """Create new user"""
        if user_data.username in self.users_db:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        
        user_id = secrets.token_urlsafe(16)
        hashed_password = self.hash_password(user_data.password)
        
        user_dict = {
            "id": user_id,
            "username": user_data.username,
            "email": user_data.email,
            "password_hash": hashed_password,
            "roles": user_data.roles,
            "is_active": True,
            "created_at": datetime.now(),
            "last_login": None
        }
        
        self.users_db[user_data.username] = user_dict
        
        return User(**{k: v for k, v in user_dict.items() if k != "password_hash"})
    
    def get_user(self, username: str) -> Optional[User]:
        """Get user by username"""
        user_dict = self.users_db.get(username)
        
        if not user_dict:
            return None
        
        return User(**{k: v for k, v in user_dict.items() if k != "password_hash"})
    
    def login(self, login_data: UserLogin) -> Dict:
        """User login"""
        user = self.authenticate_user(login_data.username, login_data.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create tokens
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.create_access_token(
            data={
                "sub": user["username"],
                "user_id": user["id"],
                "roles": user["roles"]
            },
            expires_delta=access_token_expires
        )
        
        refresh_token = self.create_refresh_token(user["id"])
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "roles": user["roles"]
            }
        }
    
    def refresh_access_token(self, refresh_token: str) -> Dict:
        """Refresh access token"""
        if refresh_token not in self.refresh_tokens:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        try:
            payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("user_id")
            
            # Find user by ID
            user = None
            for u in self.users_db.values():
                if u["id"] == user_id:
                    user = u
                    break
            
            if not user or not user["is_active"]:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found or inactive"
                )
            
            # Create new access token
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = self.create_access_token(
                data={
                    "sub": user["username"],
                    "user_id": user["id"],
                    "roles": user["roles"]
                },
                expires_delta=access_token_expires
            )
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
            }
            
        except jwt.ExpiredSignatureError:
            # Remove expired refresh token
            del self.refresh_tokens[refresh_token]
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

# Global auth manager instance
auth_manager = AuthManager()

# Dependency functions
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current authenticated user"""
    token_data = auth_manager.verify_token(credentials.credentials)
    user = auth_manager.get_user(token_data.username)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return current_user

def require_roles(required_roles: List[str]):
    """Decorator to require specific roles"""
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if not any(role in current_user.roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    
    return role_checker

# Role-specific dependencies
require_admin = require_roles([UserRole.ADMIN])
require_user = require_roles([UserRole.USER, UserRole.ADMIN])
require_viewer = require_roles([UserRole.VIEWER, UserRole.USER, UserRole.ADMIN])

class SecurityValidator:
    """Security validation utilities"""
    
    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """Validate API key format and strength"""
        if not api_key:
            return False
        
        # Check minimum length
        if len(api_key) < 32:
            return False
        
        # Check for basic entropy (not just repeated characters)
        if len(set(api_key)) < 10:
            return False
        
        return True
    
    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, bool]:
        """Validate password strength"""
        checks = {
            "min_length": len(password) >= 8,
            "has_upper": any(c.isupper() for c in password),
            "has_lower": any(c.islower() for c in password),
            "has_digit": any(c.isdigit() for c in password),
            "has_special": any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        }
        
        checks["is_strong"] = all(checks.values())
        
        return checks
    
    @staticmethod
    def sanitize_input(input_str: str) -> str:
        """Basic input sanitization"""
        if not input_str:
            return ""
        
        # Remove potential script tags and other dangerous content
        dangerous_patterns = ["<script", "</script>", "javascript:", "onload=", "onerror="]
        
        sanitized = input_str
        for pattern in dangerous_patterns:
            sanitized = sanitized.replace(pattern.lower(), "")
            sanitized = sanitized.replace(pattern.upper(), "")
        
        return sanitized.strip()

def get_auth_manager() -> AuthManager:
    """Get auth manager instance"""
    return auth_manager