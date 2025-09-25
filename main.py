import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config import config

# Import handlers
from handlers.commands import start, help_command, connect, run_command, status, disconnect
from handlers.message_handlers import handle_message

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """Start the bot"""
    if not config.BOT_TOKEN:
        logger.error("BOT_TOKEN environment variable is required!")
        return
    
    if not config.ALLOWED_USER_IDS:
        logger.warning("No ALLOWED_USER_IDS specified - bot will reject all users!")
    
    # Create Application
    application = Application.builder().token(config.BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("connect", connect))
    application.add_handler(CommandHandler("run", run_command))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("disconnect", disconnect))
    
    # Add message handler for credential extraction
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start the bot
    logger.info("Bot starting...")
    application.run_polling()

if __name__ == "__main__":
    main()