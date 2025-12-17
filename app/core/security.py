import hashlib
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

# Create password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class SecurityManager:
    @staticmethod
    def _pre_hash_password(password: str) -> str:
        """Hash password with SHA256 to ensure consistent length for bcrypt"""
        # SHA256 produces 64-byte hex string, well under bcrypt's 72-byte limit
        return hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        # Pre-hash the plain password before verification
        pre_hashed = SecurityManager._pre_hash_password(plain_password)
        return pwd_context.verify(pre_hashed, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        # Pre-hash the password to ensure consistent length
        pre_hashed = SecurityManager._pre_hash_password(password)
        return pwd_context.hash(pre_hashed)
    
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: dict) -> str:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode = data.copy()
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except JWTError:
            return None
    
    @staticmethod
    def extract_email_from_token(token: str) -> Optional[str]:
        payload = SecurityManager.verify_token(token)
        if payload and payload.get("type") == "access":
            return payload.get("sub")
        return None

security_manager = SecurityManager()