from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, HTTPAuthorizationCredentials
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from auth.models import User
from core.db import get_db
from auth.utils.token_utils import verify_access_token, TokenError
from fastapi import HTTPException
from fastapi.security import HTTPBearer

bearer_scheme = HTTPBearer()


async def get_current_user(token: HTTPAuthorizationCredentials = Depends(bearer_scheme), db: AsyncSession = Depends(get_db)):
    payload = verify_access_token(token.credentials)
    print("----------------------------------------------------payload------------------------------------------", payload)
    sub = payload.get("sub")
    if not sub:
        raise TokenError("Token missing subject claim")
    
    result = await db.execute(Select(User).where(User.id == sub))
    user = result.scalar_one_or_none()
    if not user:
        raise TokenError("User not found")  
    return payload 


async def require_owner(user: dict = Depends(get_current_user)) -> dict:
    if user["role"]!= "owner":
        raise HTTPException(403, "Owners only")
    return user

async def require_tenant(user: dict = Depends(get_current_user)) -> dict:
    if user["role"] != "tenant":
        raise HTTPException(403, "Tenants only")
    return user
