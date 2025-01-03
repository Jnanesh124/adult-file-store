import asyncio
import os
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
import subprocess
from bot import Bot
from config import ADMINS, CHANNEL_ID, DISABLE_CHANNEL_BUTTON
from helper_func import encode

# Function to generate a 30-second sample from the video stream using ffmpeg
async def generate_sample_video_from_stream(client, video_file_id, output_video_path, start_time=0, duration=30):
    # Create a temporary file path to save the sample video
    temp_video_path = "temp_sample_video.mp4"
    
    # Download the video as a stream
    video_stream = await client.download_media(video_file_id, file_name=temp_video_path)

    # Use ffmpeg to generate a 30-second sample from the video stream
    command = [
        "ffmpeg",
        "-i", temp_video_path,         # Input video stream
        "-ss", str(start_time),         # Start time (in seconds)
        "-t", str(duration),            # Duration of the sample
        "-c:v", "libx264",              # Video codec
        "-c:a", "aac",                  # Audio codec
        "-preset", "fast",              # Encoding speed
        "-y",                           # Overwrite output file
        output_video_path               # Output file path
    ]
    
    # Run the ffmpeg command to create the sample
    subprocess.run(command)

    # Clean up the temporary video file
    os.remove(temp_video_path)

# Handler to process private messages from admins
@Bot.on_message(filters.private & filters.user(ADMINS) & ~filters.command(['start', 'users', 'broadcast', 'batch', 'genlink', 'stats']))
async def channel_post(client: Client, message: Message):
    reply_text = await message.reply_text("Please Wait...!", quote=True)
    try:
        video_path = None
        sample_video_path = "sample_video.mp4"  # Path to save the 30-second sample video

        # Check if the message contains a video
        if message.video:
            # Generate a 30-second sample from the video stream
            await generate_sample_video_from_stream(client, message.video.file_id, sample_video_path, start_time=0, duration=30)

            # Send the 30-second sample video
            await message.reply_video(video=sample_video_path, caption="Here is your 30-second sample video.", reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={sample_video_path}')]]
            ))

            # Clean up the generated sample video
            os.remove(sample_video_path)

        # If the message does not contain a video, proceed with usual link generation
        else:
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

# Handler for incoming channel messages
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
