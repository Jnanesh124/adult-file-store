import os
import logging

# Mandatory Bot Configuration
API_HASH = os.getenv("API_HASH", "your_api_hash")  # Replace with your API_HASH
APP_ID = int(os.getenv("APP_ID", "123456"))       # Replace with your APP_ID
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN", "your_bot_token")  # Replace with your Bot Token
TG_BOT_WORKERS = int(os.getenv("TG_BOT_WORKERS", "4"))  # Default: 4
LOGGER = logging.getLogger(__name__)             # For logging bot events

# Optional Channel and Subscription Configuration
FORCE_SUB_CHANNEL = os.getenv("FORCE_SUB_CHANNEL", None)  # Channel ID or Username (e.g., "@channel")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "-1001234567890"))  # ID of the bot's database channel
PORT = int(os.getenv("PORT", "8080"))                     # Default port for webhook or server

# Features Configuration
ADMINS = [int(admin) for admin in os.getenv("ADMINS", "").split()]  # List of Admin User IDs
START_MSG = os.getenv(
    "START_MSG",
    "Hello {first},\n\nWelcome to the bot! You can start by exploring available features.",
)  # Customizable start message
CUSTOM_CAPTION = os.getenv(
    "CUSTOM_CAPTION",
    "{previouscaption}\n\nFile Name: {filename}",
)  # Customizable caption for forwarded messages
DISABLE_CHANNEL_BUTTON = bool(os.getenv("DISABLE_CHANNEL_BUTTON", "False") == "True")  # Disable channel buttons
PROTECT_CONTENT = bool(os.getenv("PROTECT_CONTENT", "False") == "True")  # Enable content protection

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,  # Log level: DEBUG, INFO, WARNING, ERROR
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Environment Variables Check (Optional)
def check_env_variables():
    missing_vars = []
    for var in ["API_HASH", "APP_ID", "TG_BOT_TOKEN", "CHANNEL_ID"]:
        if not os.getenv(var):
            missing_vars.append(var)
    if missing_vars:
        LOGGER.warning(f"Missing required environment variables: {', '.join(missing_vars)}")
        raise EnvironmentError("Please set all mandatory environment variables.")

# Call the environment check function (Optional)
check_env_variables()
