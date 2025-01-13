from aiohttp import web
from plugins import web_server

import pyromod.listen
from pyrogram import Client
from pyrogram.enums import ParseMode
import sys
import os
import asyncio
from datetime import datetime

from config import API_HASH, APP_ID, LOGGER, TG_BOT_TOKEN, TG_BOT_WORKERS, FORCE_SUB_CHANNEL, CHANNEL_ID, PORT
import pyrogram.utils

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
        try:
            await super().start()
            usr_bot_me = await self.get_me()
            self.uptime = datetime.now()

            # Force Sub Channel Handling
            if FORCE_SUB_CHANNEL:
                try:
                    link = (await self.get_chat(FORCE_SUB_CHANNEL)).invite_link
                    if not link:
                        await self.export_chat_invite_link(FORCE_SUB_CHANNEL)
                        link = (await self.get_chat(FORCE_SUB_CHANNEL)).invite_link
                    self.invitelink = link
                except Exception as a:
                    self.LOGGER(__name__).warning(f"Force Sub Channel Error: {a}")
                    self.LOGGER(__name__).info("Bot stopping due to Force Sub Channel configuration error.")
                    self.restart_bot()

            # Database Channel Handling
            try:
                db_channel = await self.get_chat(CHANNEL_ID)
                self.db_channel = db_channel
                test = await self.send_message(chat_id=db_channel.id, text="Test Message")
                await test.delete()
            except Exception as e:
                self.LOGGER(__name__).warning(f"Error with DB Channel: {e}")
                self.LOGGER(__name__).info("Bot stopping due to DB Channel configuration error.")
                self.restart_bot()

            self.set_parse_mode(ParseMode.HTML)
            self.LOGGER(__name__).info(f"Bot Running..!\nCreated by https://t.me/ultroid_official")
            self.username = usr_bot_me.username

            # Web Response
            app = web.AppRunner(await web_server())
            await app.setup()
            bind_address = "0.0.0.0"
            await web.TCPSite(app, bind_address, PORT).start()

        except Exception as e:
            self.LOGGER(__name__).error(f"Critical error during bot startup: {e}")
            self.restart_bot()

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info("Bot stopped.")

    def restart_bot(self):
        """Restart the bot by re-executing the script."""
        self.LOGGER(__name__).info("Restarting the bot...")
        os.execv(sys.executable, [sys.executable] + sys.argv)


if __name__ == "__main__":
    bot = Bot()
    try:
        asyncio.run(bot.start())
    except KeyboardInterrupt:
        bot.LOGGER(__name__).info("Bot stopped manually.")
    except Exception as e:
        bot.LOGGER(__name__).error(f"Unhandled exception: {e}")
        bot.restart_bot()
