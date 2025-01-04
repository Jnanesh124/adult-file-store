import signal
import sys
from bot import Bot
from config import API_HASH, APP_ID, TG_BOT_TOKEN, TG_BOT_WORKERS, LOGGER

def signal_handler(sig, frame):
    print("Exiting gracefully...")
    sys.exit(0)

# Register the signal handler
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    try:
        bot = Bot(
            api_hash=API_HASH,
            api_id=APP_ID,
            bot_token=TG_BOT_TOKEN,
            workers=TG_BOT_WORKERS,
            logger=LOGGER,
        )
        bot.run()
    except KeyboardInterrupt:
        print("Bot interrupted by user. Exiting...")
        sys.exit(0)
