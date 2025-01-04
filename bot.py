from aiohttp import web
from plugins import web_server

import pyromod.listen
from pyrogram import Client
from pyrogram.enums import ParseMode
import sys
from datetime import datetime

from config import (
    API_HASH,
    APP_ID,
    LOGGER,
    TG_BOT_TOKEN,
    TG_BOT_WORKERS,
    FORCE_SUB_CHANNEL,
    CHANNEL_ID,
    PORT,
)
import pyrogram.utils
from helper_func import create_image_thumbnail, create_video_thumbnail
import os

# Extend Pyrogram's minimum chat/channel IDs for database handling
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
            bot_token=TG_BOT_TOKEN,
        )
        self.LOGGER = LOGGER

    async def start(self):
        await super().start()
        usr_bot_me = await self.get_me()
        self.uptime = datetime.now()

        # Check Force Subscription Channel
        if FORCE_SUB_CHANNEL:
            try:
                link = (await self.get_chat(FORCE_SUB_CHANNEL)).invite_link
                if not link:
                    await self.export_chat_invite_link(FORCE_SUB_CHANNEL)
                    link = (await self.get_chat(FORCE_SUB_CHANNEL)).invite_link
                self.invitelink = link
            except Exception as e:
                self.LOGGER(__name__).warning(f"Error setting Force Sub Channel: {e}")
                self.LOGGER(__name__).warning(
                    "Please Double-check FORCE_SUB_CHANNEL and ensure the bot has admin rights."
                )
                sys.exit()

        # Validate Database Channel
        try:
            db_channel = await self.get_chat(CHANNEL_ID)
            self.db_channel = db_channel
            test = await self.send_message(chat_id=db_channel.id, text="Test Message")
            await test.delete()
        except Exception as e:
            self.LOGGER(__name__).warning(f"Database Channel Error: {e}")
            self.LOGGER(__name__).warning("Ensure the bot has admin access to the channel.")
            sys.exit()

        self.set_parse_mode(ParseMode.HTML)
        self.LOGGER(__name__).info(f"Bot @{usr_bot_me.username} is running.")
        self.username = usr_bot_me.username

        # Web server initialization
        app = web.AppRunner(await web_server())
        await app.setup()
        bind_address = "0.0.0.0"
        await web.TCPSite(app, bind_address, PORT).start()

    async def handle_file_upload(self, file_path, chat_id):
        """
        Handles file uploads and generates/sends thumbnails.
        """
        thumbnail_path = "thumbnail.jpg"  # Temporary thumbnail path

        try:
            # Generate and send thumbnails
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                create_image_thumbnail(file_path, thumbnail_path)
            elif file_path.lower().endswith(('.mp4', '.mkv', '.avi')):
                create_video_thumbnail(file_path, thumbnail_path)

            # Send the thumbnail
            if os.path.exists(thumbnail_path):
                with open(thumbnail_path, 'rb') as thumb:
                    await self.send_photo(chat_id=chat_id, photo=thumb)
                os.remove(thumbnail_path)
        except Exception as e:
            self.LOGGER(__name__).error(f"Error handling file upload: {e}")

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info("Bot stopped.")


if __name__ == "__main__":
    LOGGER(__name__).info("Starting Bot...")
    Bot().run()
