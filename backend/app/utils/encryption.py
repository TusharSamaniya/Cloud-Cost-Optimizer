from cryptography.fernet import Fernet
from app.core.config import settings

# Initialize the Fernet tool using your master key
fernet = Fernet(settings.ENCRYPTION_KEY.encode())

def encrypt_value(value: str) -> str:
    """Takes a plain text string and returns a scrambled string"""
    if not value:
        return value
    # Fernet requires bytes, so we encode the string, encrypt it, and decode back to a string
    return fernet.encrypt(value.encode()).decode()

def decrypt_value(encrypted_value: str) -> str:
    """Takes a scrambled string and returns the original plain text"""
    if not encrypted_value:
        return encrypted_value
    return fernet.decrypt(encrypted_value.encode()).decode()