import signal
import sys

def signal_handler(sig, frame):
    print("Exiting gracefully...")
    sys.exit(0)

# Register the signal handler
signal.signal(signal.SIGTERM, signal_handler)

# Now start the bot
from bot import Bot
Bot().run()
