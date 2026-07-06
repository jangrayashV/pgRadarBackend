
import logging
import random
import string
 
from core.config import settings
 
logger = logging.getLogger(__name__)
 
 
def generate_otp(length: int = 6) -> str:
    """Generate a numeric OTP of given length."""
    return "".join(random.choices(string.digits, k=length))
 
 
async def send_otp(phone: str, otp: str) -> None:
    """
    Send OTP via SMS in production.
    In development, logs to console — zero cost testing.
    Swap the else branch with real provider (2Factor, Fast2SMS) when ready.
    """
    if settings.is_development:
        logger.info("=" * 40)
        logger.info("OTP for %s: %s", phone, otp)
        logger.info("=" * 40)
    else:
        # TODO: integrate SMS provider
        # Example with 2Factor:
        # import httpx
        # async with httpx.AsyncClient() as client:
        #     await client.get(
        #         f"https://2factor.in/API/V1/{settings.SMS_PROVIDER_API_KEY}/SMS/{phone}/{otp}"
        #     )
        raise NotImplementedError("SMS provider not configured for production")
 