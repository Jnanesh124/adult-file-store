from aiohttp import web
from plugins import web_server
from bot_init import Bot

import pyromod.listen
from pyrogram import Client
from pyrogram.enums import ParseMode
import sys
from datetime import datetime

from config import API_HASH, APP_ID, LOGGER, TG_BOT_TOKEN, TG_BOT_WORKERS, FORCE_SUB_CHANNEL, CHANNEL_ID, PORT
import pyrogram.utils
from helper_func import create_image_thumbnail, create_video_thumbnail  # Import thumbnail functions
import os

pyrogram.utils.MIN_CHAT_ID = -999999999999
pyrogram.utils.MIN_CHANNEL_ID = -100999999999999

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Bot",
            api_hash=API_HASH,
            api_id=APP_ID,
            plugins={
                "root": "plugins"
            },
            workers=TG_BOT_WORKERS,
            bot_token=TG_BOT_TOKEN
        )
        self.LOGGER = LOGGER

    async def start(self):
        await super().start()
        usr_bot_me = await self.get_me()
        self.uptime = datetime.now()

        if FORCE_SUB_CHANNEL:
            try:
                link = (await self.get_chat(FORCE_SUB_CHANNEL)).invite_link
                if not link:
                    await self.export_chat_invite_link(FORCE_SUB_CHANNEL)
                    link = (await self.get_chat(FORCE_SUB_CHANNEL)).invite_link
                self.invitelink = link
            except Exception as a:
                self.LOGGER(__name__).warning(a)
                self.LOGGER(__name__).warning("Bot can't Export Invite link from Force Sub Channel!")
                self.LOGGER(__name__).warning(f"Please Double check the FORCE_SUB_CHANNEL value and Make sure Bot is Admin in channel with Invite Users via Link Permission, Current Force Sub Channel Value: {FORCE_SUB_CHANNEL}")
                self.LOGGER(__name__).info("\nBot Stopped. Join https://t.me/ultroid_official for support")
                sys.exit()
        try:
            db_channel = await self.get_chat(CHANNEL_ID)
            self.db_channel = db_channel
            test = await self.send_message(chat_id=db_channel.id, text="Test Message")
            await test.delete()
        except Exception as e:
            self.LOGGER(__name__).warning(f"Error occurred: {e}")
            self.LOGGER(__name__).warning(f"CHANNEL_ID: {CHANNEL_ID}, DB Channel ID: {db_channel.id if 'db_channel' in locals() else 'N/A'}")
            self.LOGGER(__name__).warning(f"Make sure bot is Admin in DB Channel, and Double-check the CHANNEL_ID value.")
            self.LOGGER(__name__).info("\nBot Stopped. Join https://t.me/ultroid_official for support")
            sys.exit()

        self.set_parse_mode(ParseMode.HTML)
        self.LOGGER(__name__).info(f"Bot Running..!\n\nCreated by \nhttps://t.me/ultroid_official")
        self.LOGGER(__name__).info(f""" \n\n       
(っ◔◡◔)っ ♥ ULTROIDOFFICIAL ♥
░╚════╝░░╚════╝░╚═════╝░╚══════╝
                                          """)
        self.username = usr_bot_me.username
        #web-response
        app = web.AppRunner(await web_server())
        await app.setup()
        bind_address = "0.0.0.0"
        await web.TCPSite(app, bind_address, PORT).start()

    async def handle_file_upload(self, file_path, chat_id):
        """
        Handles file uploads and generates/sends thumbnails.
        """
        thumbnail_path = "thumbnail.jpg"  # Temporary thumbnail path

        if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            # Generate image thumbnail
            create_image_thumbnail(file_path, thumbnail_path)
        elif file_path.lower().endswith(('.mp4', '.mkv', '.avi')):
            # Generate video thumbnail
            create_video_thumbnail(file_path, thumbnail_path)

        # Send the thumbnail to the user
        if os.path.exists(thumbnail_path):
            with open(thumbnail_path, 'rb') as thumb:
                await self.send_photo(chat_id=chat_id, photo=thumb)
            os.remove(thumbnail_path)

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info("Bot stopped.")
