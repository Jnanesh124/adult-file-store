
import os
import logging
from logging.handlers import RotatingFileHandler

#Bot token @Botfather
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "7820594648:AAElYLOYY3Nx3O7U0W3iqaNqrY-pQJXItXI")

#Your API ID & API HASH from my.telegram.org [https://youtu.be/gZQJ-yTMkEo?si=H4NlUUgjsIc5btzH]
#Your API ID from my.telegram.org
APP_ID = int(os.environ.get("APP_ID", "21942125"))

#Your API Hash from my.telegram.org
API_HASH = os.environ.get("API_HASH", "6d412af77ce89f5bb1ed8971589d61b5")

#Your db channel Id
CHANNEL_ID = int(os.environ.get("CHANNEL_ID", "-1002205211966"))

#OWNER ID
OWNER_ID = int(os.environ.get("OWNER_ID", "6643562770"))

#Port
PORT = os.environ.get("PORT", "8585")

#Database 
#Database [https://youtu.be/qFB0cFqiyOM?si=fVicsCcRSmpuja1A]
DB_URI = os.environ.get("DATABASE_URL", "mongodb+srv://easyeasy740:easyeasy740@cluster0.1shrvws.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DB_NAME = os.environ.get("DATABASE_NAME", "Cluster0")

#Shortner (token system) 
# check my discription to help by using my refer link of shareus.io
# 

SHORTLINK_URL = os.environ.get("SHORTLINK_URL", "seturl.in")
SHORTLINK_API = os.environ.get("SHORTLINK_API", "3daf41670bf9ee8030e786aed791f15ffb7eb104")
VERIFY_EXPIRE = int(os.environ.get('VERIFY_EXPIRE', 86400)) # Add time in seconds
IS_VERIFY = os.environ.get("IS_VERIFY", "True")
TUT_VID = os.environ.get("TUT_VID", "https://youtu.be/tTBBA2wl28k?si=KAZYBHomSloGNhrd") # shareus ka tut_vid he 

#force sub channel id, if you want enable force sub
FORCE_SUB_CHANNEL = int(os.environ.get("FORCE_SUB_CHANNEL", "-1002380159168"))
JOIN_REQUEST_ENABLE = os.environ.get("JOIN_REQUEST_ENABLED", None)

TG_BOT_WORKERS = int(os.environ.get("TG_BOT_WORKERS", "4"))

#start message
START_PIC = os.environ.get("START_PIC","https://ibb.co/C7WMV56")
START_MSG = os.environ.get("START_MESSAGE", "<blockquote>I can store private files in Specified Channel and other users can access it from special link.\n\n©️@JN2FLIX</blockquote>")
try:
    ADMINS=[]
    for x in (os.environ.get("ADMINS", "6643562770 6643562770 6643562770").split()):
        ADMINS.append(int(x))
except ValueError:
        raise Exception("Your Admins list does not contain valid integers.")

#Force sub message 
FORCE_MSG = os.environ.get("FORCE_SUB_MESSAGE", "<strong>You need to join in my 5 Channel and subscribe my youtube channel\n\nhttps://youtube.com/@jn2flix?si=VsjRku4VVTjNi5xL\nAfter Join U Will Get Direct File 📂</strong>")

#set your Custom Caption here, Keep None for Disable Custom Caption
CUSTOM_CAPTION = os.environ.get("CUSTOM_CAPTION", None)

#set True if you want to prevent users from forwarding files from bot
PROTECT_CONTENT = True if os.environ.get('PROTECT_CONTENT', "False") == "True" else False

# Auto delete time in seconds.
AUTO_DELETE_TIME = int(os.getenv("AUTO_DELETE_TIME", "0"))
AUTO_DELETE_MSG = os.environ.get("AUTO_DELETE_MSG", "u want direct sex video all type oyo,kannada,rp,nudi,desi,english,lesibian,shemale,more type than msg here to buy https://t.me/Adult_Videos_Membership_Bot")
AUTO_DEL_SUCCESS_MSG = os.environ.get("AUTO_DEL_SUCCESS_MSG", "Your file has been successfully deleted. Thank you for using our service. ✅\n\nJOIN BACKUP CHANNEL @JN2FLIX\nJOIN BOTS CHANNEL @ROCKERSBACKUP")

#Set true if you want Disable your Channel Posts Share button
DISABLE_CHANNEL_BUTTON = os.environ.get("DISABLE_CHANNEL_BUTTON", None) == 'True'

BOT_STATS_TEXT = "<b>BOT UPTIME</b>\n{uptime}"
USER_REPLY_TEXT = "for adult video use this bots\nhttps://t.me/desibhabhisexxxbot\nhttps://t.me/Brazzer_denial_bot\nhttps://t.me/kannada_Sexleaked_bot\nhttps://t.me/oyoroomsexpornxxxbot\n\nhttps://t.me/kannada_nudi_video_bot\n\n\nDirect sex video\nhttps://t.me/Adult_Videos_Membership_Bot"

ADMINS.append(OWNER_ID)
ADMINS.append(6643562770)

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
