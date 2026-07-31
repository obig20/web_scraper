"""Security utilities: JWT, password hashing, encryption, RBAC."""

from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any

from cryptography.fernet import Fernet, InvalidToken
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from app.config import get_settings

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"


class Role(str, Enum):
    VIEWER = "viewer"
    RESEARCHER = "researcher"
    ADMIN = "admin"


class TokenPayload(BaseModel):
    sub: str
    role: Role
    exp: datetime | None = None


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(subject: str, role: Role, expires_delta: timedelta | None = None) -> str:
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload = {"sub": subject, "role": role.value, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def decode_access_token(token: str) -> TokenPayload | None:
    try:
        data = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        return TokenPayload(sub=data["sub"], role=Role(data["role"]))
    except (JWTError, KeyError, ValueError):
        return None


def _get_fernet() -> Fernet:
    key = settings.encryption_key.encode()[:32].ljust(32, b"0")
    import base64

    return Fernet(base64.urlsafe_b64encode(key))


def encrypt_credential(value: str) -> str:
    return _get_fernet().encrypt(value.encode()).decode()


def decrypt_credential(value: str) -> str:
    try:
        return _get_fernet().decrypt(value.encode()).decode()
    except InvalidToken as exc:
        raise ValueError("Invalid encrypted credential") from exc


ROLE_PERMISSIONS: dict[Role, set[str]] = {
    Role.VIEWER: {"read:articles", "read:cases", "search"},
    Role.RESEARCHER: {
        "read:articles",
        "read:cases",
        "search",
        "write:notes",
        "write:scripts",
        "trigger:crawl",
    },
    Role.ADMIN: {"*"},
}


def has_permission(role: Role, permission: str) -> bool:
    perms = ROLE_PERMISSIONS.get(role, set())
    return "*" in perms or permission in perms
