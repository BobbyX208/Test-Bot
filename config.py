import os
from typing import List, Set

class Config:
    """Configuration class for bot settings"""
    
    def __init__(self):
        # Telegram Bot Token
        self.BOT_TOKEN = os.getenv("BOT_TOKEN", "")
        
        # Allowed Telegram User IDs
        allowed_users = os.getenv("ALLOWED_USER_IDS", "")
        self.ALLOWED_USER_IDS = set(map(int, filter(None, allowed_users.split(',')))) if allowed_users else set()
        
        # Session TTL in seconds (default 15 minutes)
        self.SESSION_TTL = int(os.getenv("SESSION_TTL", "900"))
        
        # WinRM configuration
        self.WINRM_PORT = int(os.getenv("WINRM_PORT", "5985"))
        self.WINRM_TIMEOUT = int(os.getenv("WINRM_TIMEOUT", "10"))
        
        # Security settings
        self.DELETE_CREDENTIAL_MESSAGES = os.getenv("DELETE_CREDENTIAL_MESSAGES", "true").lower() == "true"
        
        # Output truncation (Telegram message limit is 4096 chars)
        self.MAX_OUTPUT_LENGTH = 4000

# Global config instance
config = Config()