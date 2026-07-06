import uuid
from datetime import datetime, timezone, timedelta

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import User, RefreshToken, VerificationCode


# auth/repository.py

import uuid
from datetime import datetime, timezone

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import PasswordReset, RefreshToken, User


class AuthRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_phone(self, phone: str) -> User | None:
        result = await self.db.execute(select(User).where(User.phone == phone))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def create(
        self,
        phone: str,
        password_hash: str,
        full_name: str,
        role: str,
        email: str | None = None,
    ) -> User:
        user = User(
            phone=phone,
            email=email,
            password_hash=password_hash,
            full_name=full_name,
            role=role,
        )
        self.db.add(user)
        await self.db.flush()
        return user

    async def update_last_login(self, user_id: uuid.UUID) -> None:
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(last_login_at=datetime.now(timezone.utc))
        )

    async def update_password(self, user_id: uuid.UUID, password_hash: str) -> None:
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(password_hash=password_hash)
        )




    async def increment_failed_attempts(self, user_id: uuid.UUID) -> int:
        result = await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                failed_login_attempts=User.failed_login_attempts + 1,
                last_failed_at=datetime.now(timezone.utc),
            )
            .returning(User.failed_login_attempts)
        )
        return result.scalar_one()

    async def lock_account(self, user_id: uuid.UUID, locked_until: datetime) -> None:
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(locked_until=locked_until)
        )

    async def reset_failed_attempts(self, user_id: uuid.UUID) -> None:
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                failed_login_attempts=0,
                locked_until=None,
                last_failed_at=None,
            )
        )





    async def create_refresh_token(
        self,
        user_id: uuid.UUID,
        jti: str,
        expires_at: datetime,
    ) -> RefreshToken:
        token = RefreshToken(user_id=user_id, jti=jti, expires_at=expires_at)
        self.db.add(token)
        await self.db.flush()
        return token

    async def get_refresh_token_by_jti(self, jti: str) -> RefreshToken | None:
        result = await self.db.execute(
            select(RefreshToken).where(RefreshToken.jti == jti)
        )
        return result.scalar_one_or_none()

    async def delete_refresh_token(self, jti: str) -> None:
        await self.db.execute(
            delete(RefreshToken).where(RefreshToken.jti == jti)
        )

    async def delete_all_refresh_tokens(self, user_id: uuid.UUID) -> None:
        await self.db.execute(
            delete(RefreshToken).where(RefreshToken.user_id == user_id)
        )

    
    
    

    async def create_password_reset(
        self,
        user_id: uuid.UUID,
        otp_hash: str,
        expires_at: datetime,
    ) -> PasswordReset:
        # invalidate any existing unused resets for this user
        await self.db.execute(
            delete(PasswordReset).where(
                PasswordReset.user_id == user_id,
                PasswordReset.used_at.is_(None),
            )
        )
        reset = PasswordReset(user_id=user_id, otp_hash=otp_hash, expires_at=expires_at)
        self.db.add(reset)
        await self.db.flush()
        return reset

    async def get_active_password_reset(self, user_id: uuid.UUID) -> PasswordReset | None:
        result = await self.db.execute(
            select(PasswordReset)
            .where(
                PasswordReset.user_id == user_id,
                PasswordReset.used_at.is_(None),
            )
            .order_by(PasswordReset.created_at.desc())
        )
        return result.scalar_one_or_none()

    async def increment_reset_attempts(self, reset_id: uuid.UUID) -> int:
        result = await self.db.execute(
            update(PasswordReset)
            .where(PasswordReset.id == reset_id)
            .values(attempts=PasswordReset.attempts + 1)
            .returning(PasswordReset.attempts)
        )
        return result.scalar_one()

    async def mark_password_reset_used(self, reset_id: uuid.UUID) -> None:
        await self.db.execute(
            update(PasswordReset)
            .where(PasswordReset.id == reset_id)
            .values(used_at=datetime.now(timezone.utc))
        )
        
    async def create_verification_code(self, phone: str, code_hash: str):
        entry = VerificationCode(
            phone=phone,
            code_hash=code_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=5)
        )
        
        self.db.add(entry)
        await self.db.flush()
    
    async def get_verification_code(self, phone: str) -> VerificationCode | None:
        result = await self.db.execute(
            select(VerificationCode)
            .where(VerificationCode.phone == phone)
            .order_by(VerificationCode.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    async def set_verification_code_used_at(self, code_id: uuid.UUID) -> None:
        await self.db.execute(
            update(VerificationCode)
            .where(VerificationCode.id == code_id)
            .values(used_at=datetime.now(timezone.utc))
        )