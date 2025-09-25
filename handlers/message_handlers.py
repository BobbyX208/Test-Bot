from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from config import config
from sessions import session_manager
from extractor import extractor
from winrm_client import test_connection, WinRMClient
from security import allowed_users_only, delete_credential_message
from utils import validate_host

@allowed_users_only
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular messages for credential extraction"""
    user_id = update.effective_user.id
    text = update.message.text
    
    # Try to extract credentials
    credentials = extractor.extract(text)
    
    if credentials:
        # Delete message containing credentials if possible
        await delete_credential_message(update, context)
        
        # Validate host
        host = validate_host(credentials['host'])
        if not host:
            await update.message.reply_text("❌ Could not extract valid host from message.")
            return
        
        username = credentials['username']
        password = credentials['password']
        
        # Test connection
        await update.message.reply_text("🔍 **Credentials extracted!** Testing connection...", parse_mode=ParseMode.MARKDOWN)
        
        success, message = test_connection(host, username, password)
        
        if success:
            # Create session
            session = session_manager.create_session(user_id, host, username, password)
            session_manager.update_session_connection(user_id, True)
            
            await update.message.reply_text(
                f"✅ **Auto-connected successfully!**\n"
                f"**Host:** `{host}`\n"
                f"**User:** `{username}`\n"
                f"**Test:** `{message}`\n\n"
                f"Use `/run <command>` to execute commands.",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await update.message.reply_text(f"❌ **Connection failed:** {message}")
    else:
        # Not a credential message, check if user has active session
        session = session_manager.get_session(user_id)
        if session and session.is_connected:
            await update.message.reply_text(
                "ℹ️ **Session active.** Use `/run <command>` to execute commands.\n"
                "Use /help for usage examples.",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await update.message.reply_text(
                "🔍 **No credentials found in message.**\n\n"
                "**Supported formats:**\n"
                "• `IP: 192.168.1.1 User: admin Pass: password`\n"
                "• `Host: 192.168.1.1 Username: admin Password: password`\n"
                "• Or use `/connect host user pass`",
                parse_mode=ParseMode.MARKDOWN
            )