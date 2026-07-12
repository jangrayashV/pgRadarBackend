from fastapi import APIRouter, Depends, HTTPException, Request
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
    db: AsyncSession = Depends(get_db),
) -> LoginResponse:
    service = AuthService(db)
    user, access_token, refresh_token = await service.login(
        phone=body.phone,
        otp=body.otp,
    )
    # _set_auth_cookies(response, access_token, refresh_token)
    return LoginResponse(
        access_token=access_token,
        message="Login successful."
    )



@router.post("/logout", response_model=LogoutResponse)
async def logout(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LogoutResponse:
    service = AuthService(db)
    print("---------------------------------------------------------------------------------",type(user))
    jti = user.get("jti")
    if jti:
        await service.logout(jti)
    # _clear_auth_cookies(response)
    return LogoutResponse(message="Logged out successfully.")
 