import asyncio
import subprocess
import tempfile
import os
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
from bot import Bot
from config import ADMINS, CHANNEL_ID, DISABLE_CHANNEL_BUTTON
from helper_func import encode

@Bot.on_message(filters.private & filters.user(ADMINS) & ~filters.command(['start', 'users', 'broadcast', 'batch', 'genlink', 'stats']))
async def channel_post(client: Client, message: Message):
    reply_text = await message.reply_text("Please Wait...!", quote=True)
    try:
        thumbnail_path = None  # Initialize thumbnail_path for cleanup
        post_message = None

        # Check if the message contains a video
        if message.video:
            video_file_id = message.video.file_id

            # Create a temporary file for the sample video
            with tempfile.NamedTemporaryFile(delete=False) as temp_video:
                temp_video_path = temp_video.name

                # Generate a 30-second preview of the video
                ffmpeg_command = [
                    'ffmpeg', '-i', video_file_id, '-t', '30', '-c:v', 'libx264', '-c:a', 'aac',
                    '-strict', 'experimental', temp_video_path
                ]
                subprocess.run(ffmpeg_command, check=True)

                # Send the sample video as a preview
                await message.reply_video(video=temp_video_path, caption="Here is a 30-second sample preview of the video.", reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]]
                ))

                # Clean up the temporary file
                os.remove(temp_video_path)

            # Generate the link
            converted_id = post_message.id * abs(client.db_channel.id)
            string = f"get-{converted_id}"
            base64_string = await encode(string)
            link = f"https://t.me/{client.username}?start={base64_string}"

            # Send the link without a thumbnail (if no media)
            await message.reply_text(f"<b>Here is your link:</b>\n\n{link}", reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]]
            ))

            # Delete the original text message after sending the link
            await message.delete()

            # Remove the "Please Wait..." message after processing
            await reply_text.delete()
            return  # Exit here to prevent further processing

        # If no video found, proceed with the usual link generation
        post_message = await message.copy(chat_id=client.db_channel.id, disable_notification=True)

        # Generate the link
        converted_id = post_message.id * abs(client.db_channel.id)
        string = f"get-{converted_id}"
        base64_string = await encode(string)
        link = f"https://t.me/{client.username}?start={base64_string}"

        # Prepare the caption with the link
        caption = f"<b>Here is your link:</b>\n\n{link}"

        # Send the link without a thumbnail (if no media)
        await message.reply_text(caption, reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]]
        ))

        # Delete the original text message after sending the link
        await message.delete()

        # Remove the "Please Wait..." message after processing
        await reply_text.delete()

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
