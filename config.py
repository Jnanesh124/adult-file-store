import os
import logging
from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler

load_dotenv()
START_PIC = os.environ.get("START_PIC","https://envs.sh/Ype.jpg")
#Bot token @Botfather
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "8011382U515mKPJwdo64")

LINK = os.environ.get("LINK","https://t.me/ROCKERSBACKUP")
CHAT = os.environ.get("CHAT","ROCKERSBACKUP")
CHANNEL = os.environ.get("CHANNEL","ROCKERSBACKUP")

# Auto delete time in seconds.
AUTO_DELETE_TIME = int(os.getenv("AUTO_DELETE_TIME", "100"))
AUTO_DELETE_MSG = os.environ.get("AUTO_DELETE_MSG", "<strong>This file will be automatically deleted in {time} seconds. Please ensure you have saved any necessary content before this time.</strong>")
AUTO_DEL_SUCCESS_MSG = os.environ.get("AUTO_DEL_SUCCESS_MSG", "Your file has been successfully deleted. Thank you for using our service. ✅\n\n Join Free Loots channel https://t.me/JNKFREELOOTS ⚪")

#Your API ID & API HASH from my.telegram.org [https://youtu.be/gZQJ-yTMkEo?si=H4NlUUgjsIc5btzH]
#Your API ID from my.telegram.org
APP_ID = int(os.environ.get("APP_ID", "22505271"))

TG_BOT_WORKERS = int(os.environ.get("TG_BOT_WORKERS", "4"))

#Your API Hash from my.telegram.org
API_HASH = os.environ.get("API_HASH", "c89a94fcfda4bc06524d0903977fc81e")

#Your db channel Id
CHANNEL_ID = int(os.environ.get("CHANNEL_ID", "-1002075726565"))

#OWNER ID
OWNER_ID = int(os.environ.get("OWNER_ID", "6695586027"))

#Port
PORT = os.environ.get("PORT", "8585")

#Database 
#Database [https://youtu.be/qFB0cFqiyOM?si=fVicsCcRSmpuja1A]
DB_URI = os.environ.get("DATABASE_URL", "mongodb+srv://ultroidxTeam:ultroidxTeam@cluster0.gabxs6m.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DB_NAME = os.environ.get("DATABASE_NAME", "Cluster0")



SHORTLINK_URL = os.environ.get("SHORTLINK_URL", "inshort")
SHORTLINK_API = os.environ.get("SHORTLINK_API", "9f943360ced66d9d5cbaa0c2b3d41f81")
VERIFY_EXPIRE = int(os.environ.get('VERIFY_EXPIRE', 86400)) # Add time in seconds
IS_VERIFY = os.environ.get("IS_VERIFY", "False")
TUT_VID = os.environ.get("TUT_VID", "https://t.me/+PZfHvzjSiZc4OGE1") # shareus ka tut_vid he 

#force sub channel id, if you want enable force sub
FORCE_SUB_CHANNEL = int(os.environ.get("FORCE_SUB_CHANNEL", "-1002108419450"))
JOIN_REQUEST_ENABLE = os.environ.get("JOIN_REQUEST_ENABLED", None)


#start message
START_MSG = os.environ.get("START_MESSAGE", "Hello {first}\n\nI can store private files in Specified Channel and other users can access it from special link.")
try:
    ADMINS=[]
    for x in (os.environ.get("ADMINS", "1480923991 5069922547 6695586027").split()):
        ADMINS.append(int(x))
except ValueError:
        raise Exception("Your Admins list does not contain valid integers.")

#Force sub message 
FORCE_MSG = os.environ.get("FORCE_SUB_MESSAGE", "Hello {first}\n\n<b>You need to join in my Channel/Group to use me\n\nKindly Please join all Channel</b>")

#set your Custom Caption here, Keep None for Disable Custom Caption
CUSTOM_CAPTION = os.environ.get("CUSTOM_CAPTION", None)

#set True if you want to prevent users from forwarding files from bot
PROTECT_CONTENT = True if os.environ.get('PROTECT_CONTENT', "False") == "True" else False

#Set true if you want Disable your Channel Posts Share button
DISABLE_CHANNEL_BUTTON = os.environ.get("DISABLE_CHANNEL_BUTTON", None) == 'True'

BOT_STATS_TEXT = "<b>BOT UPTIME</b>\n{uptime}"
USER_REPLY_TEXT = "❌Don't send me messages directly I'm only File Share bot! Join @ROCKERSBACKUP @JNKFREELOOTS"

ADMINS.append(OWNER_ID)
ADMINS.append(6695586027)

LOG_FILE_NAME = "filesharingbot.txt"

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt='%d-%b-%y %H:%M:%S',
    handlers=[
        RotatingFileHandler(
            LOG_FILE_NAME,
            maxBytes=50000000,
            backupCount=10
        ),
        logging.StreamHandler()
    ]
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)
