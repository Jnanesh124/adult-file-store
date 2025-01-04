import signal
import sys
from bot_instance import Bot  # Import Bot from a renamed or separate file to avoid circular dependency.

def signal_handler(sig, frame):
    print("Exiting gracefully...")
    sys.exit(0)

# Register the signal handler
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    try:
        bot = Bot()
        bot.run()
    except KeyboardInterrupt:
        print("Bot interrupted by user. Exiting...")
        sys.exit(0)
