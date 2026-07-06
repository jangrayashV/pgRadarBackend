from urllib import response

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from auth.models import User
from auth.schemas import RegisterRequest, RegisterResponse, LoginRequest, LoginResponse,VerificationCodeRequest, VerificationCodeResponse, VerifyVerificationCodeRequest, LogoutResponse, UserResponse
from auth.service import AuthService
from core.db import get_db
from core.rate_limiter import limiter
from core.dependencies import get_current_user, get_owner, get_tenant

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
        user=user
    )
 

# @router.post("/register")
# async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)) -> RegisterResponse:
#     auth_context = AuthService(db)
#     result = await auth_context.register(
#         phone=body.phone,
#         plain_password=body.password,
#         role=body.role,
#         full_name=body.full_name,
#         email=body.email
#         )
#     return RegisterResponse(
#         id=str(result.id),
#         full_name=result.full_name,
#         message="User registered successfully", 
#         role=result.role
#     )

# @router.post("/login/password")
# async def login_by_password(cred: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)) -> LoginResponse:
    auth_context = AuthService(db)
    result = await auth_context.login_by_password(
        phone=cred.username,
        plain_password=cred.password
        )
    return LoginResponse(
        access_token=result["access_token"],
        message="Login successful"
    )

@router.post("/login/otp/request")
@limiter.limit("3/minute")
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
    jti = user.get("jti")
    if jti:
        await service.logout(jti)
    # _clear_auth_cookies(response)
    return LogoutResponse(message="Logged out successfully.")
 