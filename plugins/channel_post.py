import asyncio
from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
import os

from bot import Bot
from config import ADMINS, CHANNEL_ID, DISABLE_CHANNEL_BUTTON, BACKUP_BOTS
from helper_func import encode

# Function to get the active bot
def get_active_bot(main_bot_username, backup_bots):
    """
    Returns the currently active bot username.
    - Tries the main bot first.
    - Fallback to backup bots in order if the main bot is unavailable.
    """
    # List of all bots to check
    bots = [main_bot_username] + backup_bots

    # Logic to find the first active bot (you can replace this with a more robust check if needed)
    for bot in bots:
        # Assuming we have a function to check if the bot is active
        # If bot is active, return it (you'll need to implement the check)
        return bot  # For simplicity, returning the first one in the list

    # If no bots are active, return None
    return None

@Bot.on_message(filters.private & filters.user(ADMINS) & ~filters.command(['start', 'users', 'broadcast', 'batch', 'genlink', 'stats']))
async def channel_post(client: Client, message: Message):
    reply_text = await message.reply_text("Please Wait...!", quote=True)
    try:
        thumbnail_path = None  # Initialize thumbnail_path for cleanup
        post_message = None

        # Check if the message contains a video with a thumbnail
        if message.video and message.video.thumbs:
            thumbnail = message.video.thumbs[0].file_id
            thumbnail_path = await client.download_media(thumbnail)

        # Check if the message contains a document with a thumbnail
        elif message.document and message.document.thumbs:
            thumbnail = message.document.thumbs[0].file_id
            thumbnail_path = await client.download_media(thumbnail)

        # Check if the message contains a GIF with a thumbnail
        elif message.animation and message.animation.thumbs:
            thumbnail = message.animation.thumbs[0].file_id
            thumbnail_path = await client.download_media(thumbnail)

        # If there's no thumbnail, proceed with the usual link generation
        if not thumbnail_path:
            post_message = await message.copy(chat_id=client.db_channel.id, disable_notification=True)

            # Generate the link
            converted_id = post_message.id * abs(client.db_channel.id)
            string = f"get-{converted_id}"
            base64_string = await encode(string)

            # Get the active bot to create the link
            active_bot = get_active_bot(client.username, BACKUP_BOTS)
            if not active_bot:
                await reply_text.edit_text("No active bots available. Please try again later.")
                return

            link = f"https://t.me/{active_bot}?start={base64_string}"

            # Prepare the caption with the link
            caption = f"<strong>🥵 DIRECT VIDEO 📂 👇\n\n{link}\n\n📩 How To Open @How_to_open_link_rockersbot</strong>"

            # Send the link without a thumbnail (if no media)
            await message.reply_text(caption, reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]]
            ))

            # Delete the original media message if it was a media message (not just a text)
            if message.video or message.document or message.animation:
                await message.delete()

            # Remove the "Please Wait..." message after processing
            await reply_text.delete()
            return  # Exit here to prevent further processing

        # If a thumbnail is available, send the thumbnail and link
        if thumbnail_path:
            post_message = await message.copy(chat_id=client.db_channel.id, disable_notification=True)

            # Generate the link
            converted_id = post_message.id * abs(client.db_channel.id)
            string = f"get-{converted_id}"
            base64_string = await encode(string)

            # Get the active bot to create the link
            active_bot = get_active_bot(client.username, BACKUP_BOTS)
            if not active_bot:
                await reply_text.edit_text("No active bots available. Please try again later.")
                return

            link = f"https://t.me/{active_bot}?start={base64_string}"

            # Prepare the caption with the link
            caption = f"<strong>🥵 DIRECT VIDEO 📂 👇\n\n{link}\n\n📩 How To Open @How_to_open_link_rockersbot</strong>"

            # Send the thumbnail with the link in the caption
            await message.reply_photo(photo=thumbnail_path, caption=caption, reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]]
            ))
            os.remove(thumbnail_path)  # Clean up the downloaded thumbnail

            # Delete the original media message if it was a media message (not just a text)
            if message.video or message.document or message.animation:
                await message.delete()

        # Remove the "Please Wait..." message after processing
        await reply_text.delete()

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

@Bot.on_message(filters.channel & filters.incoming & filters.chat(CHANNEL_ID))
async def new_post(client: Client, message: Message):
    if DISABLE_CHANNEL_BUTTON:
        return

    converted_id = message.id * abs(client.db_channel.id)
    string = f"get-{converted_id}"
    base64_string = await encode(string)

    # Get the active bot to create the link
    active_bot = get_active_bot(client.username, BACKUP_BOTS)
    if not active_bot:
        return  # Exit if no active bot is found

    link = f"https://t.me/{active_bot}?start={base64_string}"

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]])

    try:
        await message.edit_reply_markup(reply_markup)
    except FloodWait as e:
        await asyncio.sleep(e.value)
    except Exception:
        pass
