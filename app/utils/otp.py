import random
import string
from datetime import datetime, timedelta

def generate_otp(length: int = 6) -> str:
    """Generate random numeric OTP"""
    return ''.join(random.choices(string.digits, k=length))

def generate_alphanumeric_otp(length: int = 8) -> str:
    """Generate alphanumeric OTP (excluding confusing characters)"""
    characters = string.ascii_uppercase + string.digits
    # Remove confusing characters: 0, O, I, 1, L
    characters = characters.translate(str.maketrans('', '', '0O1IL'))
    return ''.join(random.choices(characters, k=length))

def calculate_expiry(minutes: int = 10) -> datetime:
    """Calculate expiry datetime"""
    return datetime.utcnow() + timedelta(minutes=minutes)