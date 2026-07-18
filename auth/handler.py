import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from auth.models import User
from auth.schemas import RegisterRequest, RegisterResponse, LoginRequest, LoginResponse,VerificationCodeRequest, VerificationCodeResponse, LogoutResponse, UserResponse
from auth.service import AuthService
from core.db import get_db
from core.rate_limiter import limiter
from core.dependencies import get_current_user

router = APIRouter()

 
@router.post("/register", response_model=RegisterResponse)
async def register(
    body: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> RegisterResponse:
    service = AuthService(db)
    user = await service.register(
        phone=body.phone,
        full_name=body.full_name,
        email=body.email,
    )
    return RegisterResponse(
        message="Registration successful.",
        user=UserResponse.model_validate(user)
    )
 

@router.post("/login/otp/request")
# @limiter.limit("3/minute")
async def request_otp(cred: VerificationCodeRequest, request: Request, db: AsyncSession = Depends(get_db)) -> VerificationCodeResponse:
    auth_context = AuthService(db)
    verification_code = await auth_context.create_verification_code(phone=cred.phone) 
    return {"otp": verification_code}


@router.post("/login", response_model=LoginResponse)
async def login(
    body: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> LoginResponse:
    service = AuthService(db)
    user, access_token, refresh_token = await service.login(
        phone=body.phone,
        otp=body.otp,
    )
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="none",
        secure=True,       # True in production (HTTPS only)
        max_age=15 * 60,    # 15 minutes
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="none",
        secure=True,
        max_age=7 * 24 * 60 * 60,  # 7 days
    )
    return LoginResponse(
        access_token=access_token,
        message="Login successful."
    )


@router.get("/me", response_model=UserResponse)
async def get_me(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    service = AuthService(db)
    user_obj = await service.get_me(uuid.UUID(user["sub"]))
    return UserResponse.model_validate(user_obj)

@router.post("/logout", response_model=LogoutResponse)
async def logout(
    response: Response,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> LogoutResponse:
    service = AuthService(db)
    jti = user.get("jti")
    if jti:
        await service.logout(jti)
    
    response.delete_cookie(
        key="access_token",
        path="/",
        httponly=True,
        secure=True,
        samesite="none",
    )
    response.delete_cookie(
        key="refresh_token",
        path="/",
        httponly=True,
        secure=True,
        samesite="none",
    )
    
    return LogoutResponse(message="Logged out successfully.")
 