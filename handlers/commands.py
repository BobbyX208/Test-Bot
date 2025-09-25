from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from config import config
from sessions import session_manager
from winrm_client import test_connection, WinRMClient
from security import allowed_users_only, delete_credential_message
from utils import truncate_text, format_command_output, validate_host

@allowed_users_only
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    welcome_text = """
🤖 **Windows Server Admin Bot**

I help you manage Windows servers via WinRM when RDP is unstable.

**Available Commands:**
/connect <host> <username> <password> [port] - Manual connection
/run <command> - Execute command (CMD or PowerShell)
/status - Show current session status
/disconnect - Clear credentials
/help - Show this help

**Auto-extraction:** Just paste credential dumps like:
`IP: 192.168.1.1 User: admin Pass: password`

**Security:** Sessions auto-expire after 15 minutes.
    """
    
    await update.message.reply_text(welcome_text, parse_mode=ParseMode.MARKDOWN)

@allowed_users_only
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """
🔧 **How to use this bot:**

1. **Connect manually:**
   `/connect 192.168.1.1 administrator password123`

2. **Or paste credential dump:**
```

Server: 192.168.1.1:5985
Username: admin
Password: password123

```

3. **Run commands:**
   - `/run ipconfig`
   - `/run powershell Get-Service`
   - `/run dir C:\\`

4. **Manage session:**
   - `/status` - Check connection
   - `/disconnect` - Clear credentials

⚡ **Features:**
- Auto credential extraction
- Both CMD and PowerShell
- Session timeout (15min)
- Secure credential handling
    """
    
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

@allowed_users_only
async def connect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /connect command"""
    user_id = update.effective_user.id
    
    if not context.args or len(context.args) < 3:
        await update.message.reply_text(
            "❌ **Usage:** `/connect <host> <username> <password> [port]`\n\n"
            "**Example:** `/connect 192.168.1.1 administrator password123 5985`",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    host = validate_host(context.args[0])
    if not host:
        await update.message.reply_text("❌ Invalid host format. Use IP address with optional port.")
        return
    
    username = context.args[1]
    password = context.args[2]
    port = int(context.args[3]) if len(context.args) > 3 and context.args[3].isdigit() else None
    
    # Test connection
    await update.message.reply_text("🔌 Testing connection...")
    success, message = test_connection(host, username, password, port)
    
    if success:
        # Create session
        session = session_manager.create_session(user_id, host, username, password, port)
        session_manager.update_session_connection(user_id, True)
        
        await update.message.reply_text(
            f"✅ **Connected successfully!**\n"
            f"**Host:** `{host}:{port or config.WINRM_PORT}`\n"
            f"**User:** `{username}`\n"
            f"**Test:** `{message}`\n\n"
            f"Use `/run <command>` to execute commands.",
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await update.message.reply_text(f"❌ **Connection failed:** {message}")

@allowed_users_only
async def run_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /run command"""
    user_id = update.effective_user.id
    session = session_manager.get_session(user_id)
    
    if not session or not session.is_connected:
        await update.message.reply_text(
            "❌ **No active session.**\n"
            "Please connect first using /connect or paste credentials."
        )
        return
    
    if not context.args:
        await update.message.reply_text(
            "❌ **Usage:** `/run <command>`\n\n"
            "**Examples:**\n"
            "• `/run ipconfig`\n"
            "• `/run powershell Get-Process`\n"
            "• `/run dir C:\\`",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    command = ' '.join(context.args)
    
    # Determine if it's PowerShell or CMD
    if command.lower().startswith('powershell'):
        # Extract the actual PowerShell command
        ps_command = command[10:].strip()  # Remove 'powershell'
        await execute_powershell(update, session, ps_command)
    else:
        await execute_cmd(update, session, command)

async def execute_cmd(update: Update, session, command: str):
    """Execute CMD command"""
    user_id = update.effective_user.id
    
    try:
        # Create WinRM client if not exists
        if not session.winrm_client:
            session.winrm_client = WinRMClient(session.host, session.username, session.password, session.port)
            session.winrm_client.session = winrm.Session(
                f"{session.host}:{session.port}",
                auth=(session.username, session.password),
                transport='ntlm',
                server_cert_validation='ignore'
            )
        
        await update.message.reply_text(f"🖥️ **Executing:** `{command}`", parse_mode=ParseMode.MARKDOWN)
        
        stdout, stderr, exit_code = session.winrm_client.run_cmd(command)
        
        # Format output
        output = format_command_output(stdout, stderr, exit_code)
        truncated_output = truncate_text(output, config.MAX_OUTPUT_LENGTH)
        
        await update.message.reply_text(truncated_output, parse_mode=ParseMode.MARKDOWN)
        
    except Exception as e:
        await update.message.reply_text(f"❌ **Error executing command:** {str(e)}")

async def execute_powershell(update: Update, session, command: str):
    """Execute PowerShell command"""
    user_id = update.effective_user.id
    
    try:
        # Create WinRM client if not exists
        if not session.winrm_client:
            session.winrm_client = WinRMClient(session.host, session.username, session.password, session.port)
            session.winrm_client.session = winrm.Session(
                f"{session.host}:{session.port}",
                auth=(session.username, session.password),
                transport='ntlm',
                server_cert_validation='ignore'
            )
        
        await update.message.reply_text(f"💻 **Executing PowerShell:** `{command}`", parse_mode=ParseMode.MARKDOWN)
        
        stdout, stderr, exit_code = session.winrm_client.run_ps(command)
        
        # Format output
        output = format_command_output(stdout, stderr, exit_code)
        truncated_output = truncate_text(output, config.MAX_OUTPUT_LENGTH)
        
        await update.message.reply_text(truncated_output, parse_mode=ParseMode.MARKDOWN)
        
    except Exception as e:
        await update.message.reply_text(f"❌ **Error executing PowerShell:** {str(e)}")

@allowed_users_only
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command"""
    user_id = update.effective_user.id
    session = session_manager.get_session(user_id)
    
    if session:
        time_remaining = config.SESSION_TTL - (session.last_used - session.created_at)
        minutes = int(time_remaining // 60)
        seconds = int(time_remaining % 60)
        
        status_text = (
            f"🟢 **Session Active**\n"
            f"**Host:** `{session.host}:{session.port}`\n"
            f"**User:** `{session.username}`\n"
            f"**Connected:** `{session.is_connected}`\n"
            f"**Time remaining:** `{minutes}m {seconds}s`\n"
            f"**Last used:** <{int(session.last_used)}>"
        )
    else:
        status_text = "🔴 **No active session**\nUse /connect or paste credentials to start."
    
    await update.message.reply_text(status_text, parse_mode=ParseMode.MARKDOWN)

@allowed_users_only
async def disconnect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /disconnect command"""
    user_id = update.effective_user.id
    
    if session_manager.delete_session(user_id):
        await update.message.reply_text("✅ **Session disconnected and credentials cleared.**")
    else:
        await update.message.reply_text("ℹ️ **No active session to disconnect.**")