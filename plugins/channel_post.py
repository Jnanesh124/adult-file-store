import asyncio
from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
import os

from bot import Bot
from config import ADMINS, CHANNEL_ID, DISABLE_CHANNEL_BUTTON
from helper_func import encode

@Bot.on_message(filters.private & filters.user(ADMINS) & ~filters.command(['start', 'users', 'broadcast', 'batch', 'genlink', 'stats']))
async def channel_post(client: Client, message: Message):
    reply_text = await message.reply_text("Please Wait...!", quote=True)
    try:
        if message.video and message.video.thumbs:
            # Extract and download the thumbnail without downloading the full video
            thumbnail = message.video.thumbs[0].file_id
            thumb_file = await client.download_media(thumbnail)
            await message.reply_photo(photo=thumb_file, caption="Here is your video thumbnail!")
            os.remove(thumb_file)  # Clean up the downloaded thumbnail
        elif message.document and message.document.thumbs:
            # Extract and download the thumbnail without downloading the full document
            thumbnail = message.document.thumbs[0].file_id
            thumb_file = await client.download_media(thumbnail)
            await message.reply_photo(photo=thumb_file, caption="Here is your document thumbnail!")
            os.remove(thumb_file)  # Clean up the downloaded thumbnail
        else:
            # Proceed with link generation if no thumbnail exists
            post_message = await message.copy(chat_id=client.db_channel.id, disable_notification=True)

        converted_id = post_message.id * abs(client.db_channel.id)
        string = f"get-{converted_id}"
        base64_string = await encode(string)
        link = f"https://t.me/{client.username}?start={base64_string}"

        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]])
        await reply_text.edit(f"<b>Here is your link</b>\n\n{link}", reply_markup=reply_markup, disable_web_page_preview=True)

        if not DISABLE_CHANNEL_BUTTON:
            try:
                await post_message.edit_reply_markup(reply_markup)
            except FloodWait as e:
                await asyncio.sleep(e.value)
                await post_message.edit_reply_markup(reply_markup)
            except Exception:
                pass

    except FloodWait as e:
        await asyncio.sleep(e.value)
    except Exception as e:
        print(e)
        await reply_text.edit_text("Something went Wrong..!")
        return

@Bot.on_message(filters.channel & filters.incoming & filters.chat(CHANNEL_ID))
async def new_post(client: Client, message: Message):
    if DISABLE_CHANNEL_BUTTON:
        return

    converted_id = message.id * abs(client.db_channel.id)
    string = f"get-{converted_id}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]])

    try:
        await message.edit_reply_markup(reply_markup)
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await message.edit_reply_markup(reply_markup)
    except Exception:
        pass
