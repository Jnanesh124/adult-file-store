import os
import logging
from logging.handlers import RotatingFileHandler

#Bot token @Botfather
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "68330jP4y0lZwQIeN-9_C0")

#Your API ID & API HASH from my.telegram.org [https://youtu.be/gZQJ-yTMkEo?si=H4NlUUgjsIc5btzH]
#Your API ID from my.telegram.org
APP_ID = int(os.environ.get("APP_ID", "21125"))

#Your API Hash from my.telegram.org
API_HASH = os.environ.get("API_HASH", "6d412589d61b5")

BACKUP_BOTS = [
    "rockersjnbot",  # Replace with the actual username of the first backup bot
    "BackupBot2",  # Replace with the actual username of the second backup bot
    # Add more bots if needed
]

#Your db channel Id
CHANNEL_ID = int(os.environ.get("CHANNEL_ID", "-1002205211966"))

CHUNK_SIZE_MB = 500  # Example: 500MB

#OWNER ID
OWNER_ID = int(os.environ.get("OWNER_ID", "662770"))

#Port
PORT = os.environ.get("PORT", "8585")

#Database 
#Database [https://youtu.be/qFB0cFqiyOM?si=fVicsCcRSmpuja1A]
DB_URI = os.environ.get("DATABASE_URL", "")
DB_NAME = os.environ.get("DATABASE_NAME", "Cluster0")

#auto delete
DELETE_AFTER = int(os.environ.get("DELETE_AFTER", 60)) #seconds
NOTIFICATION_TIME = int(os.environ.get('NOTIFICATION_TIME', 60)) #seconds
AUTO_DELETE = os.environ.get("AUTO_DELETE", True) #ON/OFF
GET_AGAIN = os.environ.get("GET_AGAIN", False) #ON/OFF
DELETE_INFORM = os.environ.get("INFORM" , "Successfully DELETED !! For Video Available Here See https://t.me/+rmz5f_q49qk5ZmZl")
NOTIFICATION = os.environ.get("NOTIFICATION" ,"🥵 No link ❌ no ads ❌ Direct video ✅\n\n⛔️ Kannada sex video\n⛔️ Nudi\n⛔️ Oyo\n⛔️ Hidden Cam\n⛔️ Rap video\n⛔️ Brzzer\n⛔️ Only fan\n⛔️ Celebrity sex\n⛔️ Animal Sex\n⛔️ Girls lesbian\n⛔️ Desi video\n⛔️ She male\n⛔️ Savitha Bhabhi \n⛔️ Comic sex video\n⛔️ African girl sex \n⛔️ Sex web series\n\n👆🏻 Above all direct video 👆🏻\n\nJust :- 250₹ (one-time payment, lifetime free)\n\nTo Buy, msg :- @msgmetobuy\n\n✅ All videos are uploaded in different channels with forwarding allowed ✅")
GET_INFORM = os.environ.get("GET_INFORM" ,"File was deleted after {DELETE_AFTER} seconds. Use the button below to GET FILE AGAIN.")

BAN = int(os.environ.get("BAN", "6331847574")) #Owner user id - dont chnge 
OWNER = os.environ.get("OWNER", "erlibedu") #Owner username
OWNER_ID = int(os.environ.get("OWNER_ID", "6643562770")) #Owner user id
OWNER_USERNAME = os.environ.get('OWNER_USERNAME', 'janugowda')
SUPPORT_GROUP = os.environ.get("SUPPORT_GROUP", "JN2FLIX") # WITHOUR @
CHANNEL = os.environ.get("CHANNEL", "JN2FLIX") # WITHOUR @

#Shortner (token system) 
SHORTLINK_URL = os.environ.get("SHORTLINK_URL", "seturl.in")
SHORTLINK_API = os.environ.get("SHORTLINK_API", "3daf41670bf9ee8030e786aed791f15ffb7eb104")
VERIFY_EXPIRE = int(os.environ.get('VERIFY_EXPIRE', 82400)) # Add time in seconds
IS_VERIFY = os.environ.get("IS_VERIFY", "True")
TUT_VID = os.environ.get("TUT_VID", "https://youtu.be/tTBBA2wl28k?si=XWoOZQyJcaO9p3eA") # shareus ka tut_vid he 

#force sub channel id, if you want enable force sub
FORCE_SUB_CHANNEL = int(os.environ.get("FORCE_SUB_CHANNEL", "-1002380159168"))

TG_BOT_WORKERS = int(os.environ.get("TG_BOT_WORKERS", "4"))

#start message
START_MSG = os.environ.get("START_MESSAGE", "https://t.me/+p-aHmJNvBNszODM1\n\nhttps://t.me/+jc7Wwu1pxMc1MTFl")
try:
    ADMINS=[]
    for x in (os.environ.get("ADMINS", "6643562770 6643562770 6643562770").split()):
        ADMINS.append(int(x))
except ValueError:
        raise Exception("Your Admins list does not contain valid integers.")

#Force sub message 
FORCE_MSG = os.environ.get("FORCE_SUB_MESSAGE", "You need to join in my Channel/Group to use me\n\nand subscribe my youtube channel\n\nhttps://youtube.com/@jn2flix?si=VsjRku4VVTjNi5xL</b>")

#set your Custom Caption here, Keep None for Disable Custom Caption
CUSTOM_CAPTION = os.environ.get("CUSTOM_CAPTION", None)

#set True if you want to prevent users from forwarding files from bot
PROTECT_CONTENT = True if os.environ.get('PROTECT_CONTENT', "False") == "True" else False

#Set true if you want Disable your Channel Posts Share button
DISABLE_CHANNEL_BUTTON = os.environ.get("DISABLE_CHANNEL_BUTTON", None) == 'True'

BOT_STATS_TEXT = "<b>BOT UPTIME</b>\n{uptime}"
USER_REPLY_TEXT = "for adult video use this bots\nhttps://t.me/desibhabhisexxxbot\nhttps://t.me/Brazzer_denial_bot\nhttps://t.me/kannada_Sexleaked_bot\nhttps://t.me/oyoroomsexpornxxxbot\n\n\nDirect sex video\nhttps://t.me/Adult_Videos_Membership_Bot"

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
