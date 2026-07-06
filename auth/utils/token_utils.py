import uuid
from datetime import datetime, timedelta, timezone
from typing import Literal
from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError
from core.config import settings


_ACCESS_SECRET =  settings.ACCESS_TOKEN_SECRET_KEY
_REFRESH_SECRET = settings.REFRESH_TOKEN_SECRET_KEY

ALGORITHM = settings.ALGORITHM

ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS  = settings.REFRESH_TOKEN_EXPIRE_DAYS

TokenType = Literal["access", "refresh"]


def create_access_token(
    user_id: str,
    email: str,
    role: str = "owner",
    extra_claims: dict | None = None,
) -> str:
    
    now = datetime.now(timezone.utc)
    jti = str(uuid.uuid4())

    payload = {
        "sub":   str(user_id),
        "email": email,
        "role":  role,
        "type":  "access",
        "jti":   jti,
        "iat":   now,
        "exp":   now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    if extra_claims:
        # Never let extra_claims overwrite reserved keys
        reserved = {"sub", "email", "role", "type", "jti", "iat", "exp"}
        payload.update({k: v for k, v in extra_claims.items() if k not in reserved})

    return jwt.encode(payload, _ACCESS_SECRET, algorithm=ALGORITHM)


def create_refresh_token(user_id: str) -> tuple[str, str]:
    now = datetime.now(timezone.utc)
    jti = str(uuid.uuid4())
    payload = {
        "sub":  str(user_id),
        "type": "refresh",
        "jti":  jti,
        "iat":  now,
        "exp":  now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    }
    token = jwt.encode(payload, _REFRESH_SECRET, algorithm=ALGORITHM)
    return token, jti



class TokenError(Exception):
    def __init__(self, message: str, expired: bool = False):
        super().__init__(message)
        self.expired = expired  # lets callers distinguish expired vs invalid


def _decode(token: str, secret: str, expected_type: TokenType) -> dict:
    try:
        payload = jwt.decode(
            token,
            secret,
            algorithms=[ALGORITHM],
            options={
                "require": ["sub", "exp", "iat", "jti", "type"],
            },
        )
    except ExpiredSignatureError:
        raise TokenError(f"{expected_type} token has expired", expired=True)
    # except JWTClaimsError as e:
    #     raise TokenError(f"Missing required claim: {e}")
    except JWTError as e:
        raise TokenError(f"Invalid token: {e}")

    if payload.get("type") != expected_type:
        raise TokenError(
            f"Token type mismatch: expected '{expected_type}', "
            f"got '{payload.get('type')}'"
        )

    if not payload.get("sub"):
        raise TokenError("Token missing subject claim")

    return payload


def verify_access_token(token: str) -> dict:
    return _decode(token, _ACCESS_SECRET, expected_type="access")


def verify_refresh_token(token: str) -> dict:
    return _decode(token, _REFRESH_SECRET, expected_type="refresh")


def rotate_refresh_token(old_token: str) -> tuple[str, str, str]:
    payload = verify_refresh_token(old_token)
    old_jti = payload["jti"]
    user_id = payload["sub"]

    new_token, new_jti = create_refresh_token(user_id)
    return new_token, new_jti, old_jti


# ---------------------------------------------------------------------------
# Usage in FastAPI (dependency pattern)
# ---------------------------------------------------------------------------
#
# from fastapi import Depends, HTTPException, status
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# from token_utils import verify_access_token, TokenError
#
# bearer = HTTPBearer()
#
# async def get_current_user(
#     credentials: HTTPAuthorizationCredentials = Depends(bearer),
# ) -> dict:
#     try:
#         payload = verify_access_token(credentials.credentials)
#     except TokenError as e:
#         status_code = status.HTTP_401_UNAUTHORIZED
#         raise HTTPException(status_code=status_code, detail=str(e))
#     return payload
#
# @router.get("/me")
# async def me(user: dict = Depends(get_current_user)):
#     return {"user_id": user["sub"], "email": user["email"]}
#
# ---------------------------------------------------------------------------
# Redis blocklist for immediate logout invalidation (optional but recommended)
# ---------------------------------------------------------------------------
#
# Access tokens are stateless — they're valid until expiry even after logout.
# 15-min window is usually acceptable. If you need instant invalidation:
#
# On logout:
#   redis.setex(f"blocklist:{jti}", ACCESS_TOKEN_EXPIRE_MINUTES * 60, "1")
#
# In verify_access_token (after decode succeeds):
#   if redis.exists(f"blocklist:{payload['jti']}"):
#       raise TokenError("Token has been revoked")
#
# Keep the TTL equal to the token's remaining lifetime — no point storing
# expired jtis since they'd fail signature verification anyway.
# ---------------------------------------------------------------------------