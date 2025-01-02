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
        thumbnail_path = None  # Initialize thumbnail_path for cleanup
        post_message = None

        if message.video and message.video.thumbs:
            # Extract and download the thumbnail without downloading the full video
            thumbnail = message.video.thumbs[0].file_id
            thumbnail_path = await client.download_media(thumbnail)

        elif message.document and message.document.thumbs:
            # Extract and download the thumbnail without downloading the full document
            thumbnail = message.document.thumbs[0].file_id
            thumbnail_path = await client.download_media(thumbnail)

        # Copy the message to the channel to generate a stored link
        post_message = await message.copy(chat_id=client.db_channel.id, disable_notification=True)

        # Generate the link
        converted_id = post_message.id * abs(client.db_channel.id)
        string = f"get-{converted_id}"
        base64_string = await encode(string)
        link = f"https://t.me/{client.username}?start={base64_string}"

        # Prepare the caption with the link
        caption = f"<b>Here is your link:</b>\n\n{link}"

        # Send the thumbnail with the link in the caption
        if thumbnail_path:
            await message.reply_photo(photo=thumbnail_path, caption=caption, reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]]
            ))
            os.remove(thumbnail_path)  # Clean up the downloaded thumbnail
        else:
            # If no thumbnail, just send the link
            await reply_text.edit_text(caption, reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]]
            ))

        if not DISABLE_CHANNEL_BUTTON:
            try:
                await post_message.edit_reply_markup(InlineKeyboardMarkup(
                    [[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]]
                ))
            except FloodWait as e:
                await asyncio.sleep(e.value)
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
    except Exception:
        pass
