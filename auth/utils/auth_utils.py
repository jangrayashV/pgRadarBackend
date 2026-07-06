import hmac
from passlib.context import CryptContext
# from passlib.exc import VerifyMismatchError, VerifyError



_PEPPER: str = ""

_pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",              # flags old hashes for rehash on login
    argon2__type="ID",              # argon2id variant
    argon2__memory_cost=65536,      # 64 MB
    argon2__time_cost=3,            # iterations
    argon2__parallelism=4,          # threads
)


# def _apply_pepper(password: str) -> str:
#     """
#     HMAC-SHA256 the password with the pepper before hashing.
#     Using HMAC instead of plain concatenation prevents length-extension
#     attacks and makes pepper rotation tractable.
#     """
#     return hmac.new(
#         _PEPPER.encode(),
#         password.encode(),
#         digestmod="sha256",
#     ).hexdigest()


# def hash_password(password: str) -> str:
#     peppered = _apply_pepper(password)
#     return _pwd_context.hash(peppered)

def hash_otp(otp: str) -> str:
    # peppered = _apply_pepper(otp)
    return _pwd_context.hash(otp)


# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     peppered = _apply_pepper(plain_password)
#     try:
#         return _pwd_context.verify(peppered, hashed_password)
#     except Exception:
#         return False

def verify_otp(otp: str, hashed_otp: str) -> bool:
    try:
        return _pwd_context.verify(otp, hashed_otp)
    except Exception:
        return False


def needs_rehash(hashed_password: str) -> bool:
    """
    Returns True if the stored hash was produced with outdated parameters
    (old time_cost, memory_cost, or a deprecated scheme).

    Call this after a successful verify() and re-hash + save if True.
    This is how you migrate users forward when you tighten parameters.
    """
    return _pwd_context.needs_update(hashed_password)