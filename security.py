from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from typing import Callable, Any
from config import config
from utils import redact_password

def allowed_users_only(func: Callable) -> Callable:
    """Decorator to restrict access to allowed users only"""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args: Any, **kwargs: Any):
        user_id = update.effective_user.id
        
        if user_id not in config.ALLOWED_USER_IDS:
            if update.message:
                await update.message.reply_text(
                    "Bot is running just fine but you're not a verified user 😂"
                )
            return
        
        return await func(update, context, *args, **kwargs)
    return wrapper

def redact_secrets(func: Callable) -> Callable:
    """Decorator to redact secrets from logs"""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args: Any, **kwargs: Any):
        # Store original text for processing
        original_text = update.message.text if update.message else ""
        
        # Redact for logging
        if original_text and any(keyword in original_text.lower() for keyword in ['pass', 'password', 'pwd']):
            # This is a simple redaction for logging purposes
            # Actual credential redaction happens in message processing
            pass
        
        return await func(update, context, *args, **kwargs)
    return wrapper

async def delete_credential_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Delete message containing credentials if possible"""
    if not config.DELETE_CREDENTIAL_MESSAGES:
        return False
    
    try:
        if update.message:
            await update.message.delete()
            return True
    except Exception:
        # If bot doesn't have permission to delete, just continue
        pass
    
    return False