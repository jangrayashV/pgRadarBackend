import logging
import uuid
from datetime import datetime, timedelta, timezone
 
from sqlalchemy.ext.asyncio import AsyncSession
 
from auth.models import UserRole
from auth.repository import AuthRepository
from auth.utils.auth_utils import hash_otp, verify_otp
from auth.utils.sms_utils import generate_otp, send_otp
from auth.utils.token_utils import create_access_token, create_refresh_token, verify_refresh_token, TokenError
from core.config import settings
from core.exceptions import (
    AccountLockedError,
    AuthError,
    ConflictError,
    NotFoundError,
    ValidationError,
)
 
logger = logging.getLogger(__name__)
 
class AuthService:
    def __init__(self, db: AsyncSession):
        self.repo = AuthRepository(db)
 
 
    async def register(
        self,
        phone: str,
        full_name: str,
        email: str | None = None,
    ) -> dict:
        existing = await self.repo.get_by_phone(phone)
        if existing:
            raise ConflictError("Phone number already registered")
 
        if email:
            existing_email = await self.repo.get_by_email(email)
            if existing_email:
                raise ConflictError("Email already registered")
 
        user = await self.repo.create(
            phone=phone,
            email=email,
            full_name=full_name,
            role=UserRole.owner.value,
        )
        logger.info("New owner registered: %s", phone)
        return user
 
 
    async def login(
        self,
        phone: str,
        otp: str,
    ) -> tuple[object, str, str]:
        """
        Returns (user, access_token, refresh_token).
        Router sets tokens as HttpOnly cookies.
        """
        now = datetime.now(timezone.utc)
 
        user = await self.repo.get_by_phone(phone)
        if not user:
            raise AuthError("Invalid credentials")
 
        if not user.is_active:
            raise AuthError("Account has been deactivated", code="account_inactive")
 
        if user.locked_until and user.locked_until > now:
            minutes_left = int((user.locked_until - now).total_seconds() / 60)
            raise AccountLockedError(minutes_left)

        otp_hash = await self.repo.get_verification_code(phone)
        print("---------------------------------------------otp hash------------------------------------------", otp_hash)
        print(verify_otp(otp, otp_hash.code_hash))
        if not verify_otp(otp, otp_hash.code_hash):
            attempts = await self.repo.increment_failed_attempts(user.id) if attempts < 3 else 3
            print("---------------------------------------------failed attempts------------------------------------------", attempts)
            if attempts >= 3:
                locked_until = now + timedelta(minutes=30)
                await self.repo.lock_account(user.id, locked_until)
                raise AccountLockedError(30)
            remaining = 3 - attempts
            raise AuthError(f"Invalid credentials. {remaining} attempts remaining.")
 
        await self.repo.reset_failed_attempts(user.id)
        await self.repo.update_last_login(user.id)
 
        access_token = create_access_token(
            user_id=str(user.id),
            email=user.phone,
            role=user.role.value,
        )
        refresh_token, jti = create_refresh_token(user_id=str(user.id))
 
        expires_at = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        await self.repo.create_refresh_token(
            user_id=user.id,
            jti=jti,
            expires_at=expires_at,
        )

 
        logger.info("User logged in: %s", phone)
        return user, access_token, refresh_token
 

 
    async def logout(self, jti: str) -> None:
        await self.repo.delete_refresh_token(jti)
        logger.info("User logged out, jti: %s", jti)
 

 
    async def refresh_tokens(self, refresh_token: str) -> tuple[str, str]:
        """
        Verify refresh token, rotate it, issue new access token.
        Returns (new_access_token, new_refresh_token).
        """
        try:
            payload = verify_refresh_token(refresh_token)
        except TokenError as e:
            raise AuthError(str(e), code="token_expired" if e.expired else "invalid_token")
 
        jti = payload["jti"]
        user_id = uuid.UUID(payload["sub"])
 
        stored = await self.repo.get_refresh_token_by_jti(jti)
        if not stored:
            # jti not in DB — replay attack, revoke all sessions
            await self.repo.delete_all_refresh_tokens(user_id)
            raise AuthError("Token reuse detected. All sessions revoked.", code="token_reuse")
 
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
 
        # rotate
        await self.repo.delete_refresh_token(jti)
        new_access_token = create_access_token(
            user_id=str(user.id),
            email=user.phone,
            role=user.role.value,
        )
        new_refresh_token, new_jti = create_refresh_token(user_id=str(user.id))
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        await self.repo.create_refresh_token(
            user_id=user.id,
            jti=new_jti,
            expires_at=expires_at,
        )
 
        return new_access_token, new_refresh_token
 
    
 
    async def create_tenant(
        self,
        phone: str,
        full_name: str,
        email: str | None = None,
    ) -> object:

        existing = await self.repo.get_by_phone(phone)
        if existing:
            raise ConflictError("A user with this phone already exists")
 
 
        user = await self.repo.create(
            phone=phone,
            email=email,
            full_name=full_name,
            role=UserRole.tenant.value,
        )
 
        logger.info("Tenant created: %s", phone)
        return user
        
    async def create_verification_code(self, phone: str):
        existing_user = await self.repo.get_by_phone(phone)
        if not existing_user:
            raise NotFoundError("User not found")
        import secrets
        
        verification_code = f"{secrets.randbelow(1_000_000):06d}"
        
        await self.repo.create_verification_code(phone=phone, code_hash=hash_otp(verification_code))
        
        return verification_code
        
   