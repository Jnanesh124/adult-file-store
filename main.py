from bot import Bot
import logging
import asyncio
import sys
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def restart_bot():
    """Restart the bot in case of unexpected errors."""
    logger.warning("Restarting the bot...")
    os.execv(sys.executable, [sys.executable] + sys.argv)

if __name__ == "__main__":
    bot = Bot()
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        logger.info("Bot stopped manually.")
    except Exception as e:
        logger.error(f"Unhandled exception: {e}")
        restart_bot()
