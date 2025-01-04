import signal
import sys
from bot import Bot  # Import the Bot class from bot.py
from config import API_HASH, APP_ID, TG_BOT_TOKEN, TG_BOT_WORKERS, LOGGER  # Import config values

def signal_handler(sig, frame):
    """
    Graceful exit handler for the bot.
    """
    print("Exiting gracefully...")
    sys.exit(0)

# Register the signal handler for SIGTERM (used by Heroku)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    try:
        # Initialize the bot with configuration values
        bot = Bot(
            api_hash=API_HASH,
            api_id=APP_ID,
            bot_token=TG_BOT_TOKEN,
            workers=TG_BOT_WORKERS,
            logger=LOGGER,
        )
        # Run the bot
        bot.run()
    except KeyboardInterrupt:
        print("Bot interrupted by user. Exiting...")
        sys.exit(0)
