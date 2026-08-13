import re
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

try:
    import bcrypt
except ImportError:
    bcrypt = None
import hashlib

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.session import AsyncSessionLocal
from backend.models.domain import UserModel, UserSessionModel, RefreshTokenModel

from config import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REMEMBER_ME_ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 24 hours
REFRESH_TOKEN_EXPIRE_DAYS = 7

REMEMBER_ME_REFRESH_TOKEN_EXPIRE_DAYS = 30
MAX_FAILED_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

def hash_password(password: str) -> str:
    """Hash password using bcrypt with PBKDF2 fallback."""
    pwd_bytes = password.encode("utf-8")
    if bcrypt is not None:
        try:
            salt = bcrypt.gensalt()
            return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")
        except Exception:
            pass
    salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac('sha256', pwd_bytes, salt.encode('utf-8'), 100000).hex()
    return f"pbkdf2:{salt}:{hashed}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against bcrypt hash or PBKDF2 fallback."""
    try:
        if hashed_password.startswith("pbkdf2:"):
            parts = hashed_password.split(":")
            if len(parts) == 3:
                salt = parts[1]
                expected_hash = parts[2]
                computed = hashlib.pbkdf2_hmac('sha256', plain_password.encode('utf-8'), salt.encode('utf-8'), 100000).hex()
                return secrets.compare_digest(computed, expected_hash)
        if bcrypt is not None:
            return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False
    return False




def validate_email(email: str) -> bool:
    """Validate RFC 5322 email syntax."""
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email.strip()))

def validate_password_strength(password: str) -> Optional[str]:
    """Verify strong password criteria (min 8 chars, 1 uppercase, 1 lowercase, 1 digit, 1 special char)."""
    if len(password) < 8:
        return "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return "Password must contain at least one lowercase letter."
    if not re.search(r"\d", password):
        return "Password must contain at least one digit."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return "Password must contain at least one special character (!@#$%^&*...)."
    return None

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create signed JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create signed JWT refresh token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh", "jti": secrets.token_hex(16)})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> Optional[dict]:
    """Decode and verify JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

async def get_db():
    """FastAPI async session dependency."""
    async with AsyncSessionLocal() as session:
        yield session

def ensure_utc(dt: Optional[datetime]) -> Optional[datetime]:
    """Ensure datetime is timezone-aware UTC."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

async def get_current_user(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db)
) -> UserModel:
    """Dependency to extract and validate current authenticated user from Bearer token or Cookie."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials or token expired",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        # Fallback to HTTP-only cookie
        token = request.cookies.get("lumo_access_token") or request.cookies.get("access_token")


    if not token:
        raise credentials_exception

    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise credentials_exception

    user_id = payload.get("sub")
    if not user_id:
        raise credentials_exception

    try:
        user_id_int = int(user_id)
    except ValueError:
        raise credentials_exception

    result = await session.execute(select(UserModel).where(UserModel.id == user_id_int))
    user = result.scalars().first()

    if not user or not user.is_active:
        raise credentials_exception

    # Check account lock status safely
    locked_until_utc = ensure_utc(user.locked_until)
    if locked_until_utc and locked_until_utc > datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"Account locked due to repeated failed logins until {locked_until_utc.strftime('%Y-%m-%d %H:%M:%S UTC')}"
        )

    return user


async def get_optional_current_user(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db)
) -> Optional[UserModel]:
    """Dependency that returns current user if authenticated, or None if unauthenticated/demo mode."""
    if not token:
        token = request.cookies.get("lumo_access_token") or request.cookies.get("access_token")

    if not token:
        return None

    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    try:
        user_id_int = int(user_id)
        result = await session.execute(select(UserModel).where(UserModel.id == user_id_int))
        user = result.scalars().first()
        return user if (user and user.is_active) else None
    except Exception:
        return None


