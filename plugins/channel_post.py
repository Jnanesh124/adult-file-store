import asyncio
import subprocess
import os
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
from bot import Bot
from config import ADMINS, CHANNEL_ID, DISABLE_CHANNEL_BUTTON
from helper_func import encode

# Function to generate a 30-second sample from the streaming video URL using ffmpeg
async def generate_sample_video_from_stream(stream_url, output_video_path, start_time=0, duration=30):
    try:
        # Use ffmpeg to generate a 30-second sample from the video stream
        command = [
            "ffmpeg",
            "-i", stream_url,                  # Input video stream URL
            "-ss", str(start_time),             # Start time (in seconds)
            "-t", str(duration),                # Duration of the sample
            "-c:v", "libx264",                  # Video codec
            "-c:a", "aac",                      # Audio codec
            "-preset", "fast",                  # Encoding speed
            "-y",                               # Overwrite output file
            output_video_path                   # Output file path
        ]
        
        # Run the ffmpeg command to create the sample
        print("Running ffmpeg command:", " ".join(command))  # Debugging line
        subprocess.run(command, check=True)
        print("Sample video generated successfully.")  # Debugging line
    except Exception as e:
        print("Error during ffmpeg execution:", e)  # Debugging line
        raise e

# Handler to process private messages from admins
@Bot.on_message(filters.private & filters.user(ADMINS) & ~filters.command(['start', 'users', 'broadcast', 'batch', 'genlink', 'stats']))
async def channel_post(client: Client, message: Message):
    reply_text = await message.reply_text("Please Wait...!", quote=True)
    try:
        sample_video_path = "sample_video.mp4"  # Path to save the 30-second sample video

        # Check if the message contains a file
        if message.document:
            # Forward the file to the stream bot
            stream_bot_username = "@Rockers_File_To_Stream_Bot"
            forwarded_message = await message.forward(chat_id=stream_bot_username)

            # Get the stream URL from the button (extract from the inline keyboard)
            stream_url = None
            if forwarded_message.reply_markup:
                for row in forwarded_message.reply_markup.inline_keyboard:
                    for button in row:
                        if button.url and "https://" in button.url:
                            stream_url = button.url
                            print("Stream URL found:", stream_url)  # Debugging line
                            break

            if stream_url:
                # Generate a 30-second sample from the video stream
                await generate_sample_video_from_stream(stream_url, sample_video_path, start_time=0, duration=30)

                # Send the 30-second sample video
                await message.reply_video(video=sample_video_path, caption="Here is your 30-second sample video.", reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={sample_video_path}')]]
                ))

                # Clean up the generated sample video
                os.remove(sample_video_path)

            else:
                await reply_text.edit_text("Failed to get stream URL from the stream bot.")
                print("No stream URL found.")  # Debugging line

        else:
            await reply_text.edit_text("No file received.")

        # Remove the "Please Wait..." message after processing
        await reply_text.delete()

    except FloodWait as e:
        await asyncio.sleep(e.value)
    except Exception as e:
        print("Error:", e)  # Debugging line
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
