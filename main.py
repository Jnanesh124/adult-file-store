import signal
import sys
from bot_init import Bot  # Importing Bot from bot_init.py

def signal_handler(sig, frame):
    print("Exiting gracefully...")
    sys.exit(0)

# Register the signal handler for SIGTERM
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    try:
        # Start the bot
        print("Starting bot...")
        Bot.run()  # This should keep the bot running indefinitely
    except Exception as e:
        print(f"Error occurred: {e}")
        sys.exit(1)
