# Windows Server Admin Telegram Bot

A lightweight Telegram bot for managing Windows servers via WinRM when RDP is unstable.

## Features

- 🔐 Auto credential extraction from messy text dumps
- 🖥️ WinRM connection to Windows servers
- ⚡ Execute both CMD and PowerShell commands
- 🔒 Secure session management with auto-expiry
- 👥 Restricted access to verified users only

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
```

1. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your values
   ```
2. Get Bot Token:
   · Create bot with @BotFather
   · Get your Telegram User ID with @userinfobot
3. Run the bot:
   ```bash
   python src/main.py
   ```

Usage

1. Manual connection:
   ```
   /connect 192.168.1.1 administrator password123
   ```
2. Auto-extraction (paste credential dump):
   ```
   IP: 192.168.1.1 User: admin Pass: password123
   ```
3. Run commands:
   ```
   /run ipconfig
   /run powershell Get-Service
   /run dir C:\
   ```

Security Notes

· Credentials are stored in memory only
· Sessions auto-expire after 15 minutes
· Only verified users can access the bot
· Passwords are never logged or displayed
· Credential messages are deleted when possible

```

## 🚀 Installation & Usage

1. **Create the project structure:**
```bash
mkdir -p src/handlers
cd src
```

1. Create all the files above in their respective locations
2. Install dependencies:

```bash
pip install python-telegram-bot==20.7 pywinrm python-dotenv
```

1. Set up environment:

```bash
cp .env.example .env
# Edit .env with your actual values
```

1. Run the bot:

```bash
python main.py
```