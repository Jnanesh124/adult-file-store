import asyncio
import logging
import time
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
from bot import Bot
from config import (
    ADMINS,
    START_MSG,
    CUSTOM_CAPTION,
    DISABLE_CHANNEL_BUTTON,
    PROTECT_CONTENT
)
from helper_func import get_messages, present_user, add_user
from database.database import full_userbase

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@Bot.on_message(filters.command('start') & filters.private)
async def start_command(client: Client, message: Message):
    user_id = message.from_user.id

    if not await present_user(user_id):
        try:
            await add_user(user_id)
        except Exception as e:
            logger.error(f"Failed to add user: {e}")

    if len(message.text) > 7:
        try:
            base64_string = message.text.split(" ", 1)[1]
        except:
            return
        _string = await decode(base64_string)
        argument = _string.split("-")
        ids = []

        if len(argument) == 3:
            try:
                start = int(int(argument[1]) / abs(client.db_channel.id))
                end = int(int(argument[2]) / abs(client.db_channel.id))
                ids = range(start, end + 1) if start <= end else range(start, end - 1, -1)
            except ValueError:
                return
        elif len(argument) == 2:
            try:
                ids = [int(int(argument[1]) / abs(client.db_channel.id))]
            except ValueError:
                return

        temp_msg = await message.reply("Sending, please wait...")
        try:
            messages = await get_messages(client, ids)
        except Exception as e:
            await message.reply_text("Something went wrong!")
            logger.error(f"Error fetching messages: {e}")
            return
        await temp_msg.delete()

        for msg in messages:
            caption = (
                CUSTOM_CAPTION.format(
                    previouscaption="" if not msg.caption else msg.caption.html,
                    filename=msg.document.file_name
                )
                if bool(CUSTOM_CAPTION) and bool(msg.document) else (msg.caption.html if msg.caption else "")
            )

            reply_markup = None if DISABLE_CHANNEL_BUTTON else msg.reply_markup

            try:
                await msg.copy(
                    chat_id=message.from_user.id,
                    caption=caption,
                    parse_mode=ParseMode.HTML,
                    reply_markup=reply_markup,
                    protect_content=PROTECT_CONTENT
                )
                await asyncio.sleep(0.5)
            except FloodWait as e:
                logger.warning(f"FloodWait: Sleeping for {e.x} seconds")
                await asyncio.sleep(e.x)
            except Exception as e:
                logger.error(f"Error copying message: {e}")

    else:
        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Main Adult Channel", url='https://t.me/+SmF5dsu_aWQ5ZGFl')]]
        )
        await message.reply_text(
            text=START_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=None if not message.from_user.username else '@' + message.from_user.username,
                mention=message.from_user.mention,
                id=message.from_user.id
            ),
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            quote=True
        )


@Bot.on_message(filters.command('users') & filters.private & filters.user(ADMINS))
async def get_users(client: Bot, message: Message):
    users = await full_userbase()
    await message.reply(f"Total users using this bot: {len(users)}")


@Bot.on_message(filters.command('broadcast') & filters.private & filters.user(ADMINS))
async def broadcast_message(client: Bot, message: Message):
    if message.reply_to_message:
        users = await full_userbase()
        broadcast_msg = message.reply_to_message
        total, successful, blocked, deleted, unsuccessful = 0, 0, 0, 0, 0

        pls_wait = await message.reply("<i>Broadcasting message... This will take some time</i>")
        for chat_id in users:
            try:
                await broadcast_msg.copy(chat_id)
                successful += 1
            except FloodWait as e:
                await asyncio.sleep(e.x)
                await broadcast_msg.copy(chat_id)
                successful += 1
            except Exception as e:
                unsuccessful += 1
                logger.error(f"Failed to send message to {chat_id}: {e}")
            total += 1

        status = (
            f"<b><u>Broadcast Completed</u></b>\n\n"
            f"Total Users: <code>{total}</code>\n"
            f"Successful: <code>{successful}</code>\n"
            f"Unsuccessful: <code>{unsuccessful}</code>"
        )
        await pls_wait.edit(status)
    else:
        await message.reply("<i>Please reply to a message to broadcast it.</i>")


if __name__ == "__main__":
    Bot.run()
