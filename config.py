import os
import logging

# Mandatory Bot Configuration
API_HASH = os.getenv("API_HASH", "your_api_hash")  # Replace with your API_HASH
APP_ID = int(os.getenv("APP_ID", "123456"))        # Replace with your APP_ID
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN", "your_bot_token")  # Replace with your Bot Token
TG_BOT_WORKERS = int(os.getenv("TG_BOT_WORKERS", "4"))  # Default: 4
LOGGER = logging.getLogger(__name__)              # For logging bot events

# Database Configuration
DB_URI = os.getenv("DB_URI", "your_mongodb_uri")  # MongoDB URI
DB_NAME = os.getenv("DB_NAME", "your_database_name")  # Database name

# Optional Channel and Subscription Configuration
FORCE_SUB_CHANNEL = os.getenv("FORCE_SUB_CHANNEL", None)  # Channel ID or Username (e.g., "@channel")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "-1001234567890"))  # ID of the bot's database channel
PORT = int(os.getenv("PORT", "8080"))                      # Default port for webhook or server

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

# Environment Variables Check
def check_env_variables():
    """
    Verifies that all mandatory environment variables are set. 
    Logs warnings for any missing variables.
    """
    mandatory_vars = ["API_HASH", "APP_ID", "TG_BOT_TOKEN", "DB_URI", "DB_NAME", "CHANNEL_ID"]
    missing_vars = [var for var in mandatory_vars if not os.getenv(var)]
    
    if missing_vars:
        LOGGER.warning(f"Missing required environment variables: {', '.join(missing_vars)}")
        raise EnvironmentError("Please set all mandatory environment variables.")

# Run the environment variable check
check_env_variables()
