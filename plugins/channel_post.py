import asyncio
import os
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
from moviepy.editor import VideoFileClip
from bot import Bot
from config import ADMINS, CHANNEL_ID, DISABLE_CHANNEL_BUTTON
from helper_func import encode

# Function to generate a 30-second sample video from a partial download
def generate_sample_video(input_video_path, output_video_path, start_time=0, duration=30):
    # Load the video file
    video = VideoFileClip(input_video_path)
    
    # Ensure the video is at least 30 seconds long
    duration = min(duration, video.duration - start_time)
    
    # Extract a 30-second clip from the video starting at 'start_time'
    sample_video = video.subclip(start_time, start_time + duration)
    
    # Write the sample video to the output path
    sample_video.write_videofile(output_video_path, codec="libx264", fps=24)

# Handler to process private messages from admins
@Bot.on_message(filters.private & filters.user(ADMINS) & ~filters.command(['start', 'users', 'broadcast', 'batch', 'genlink', 'stats']))
async def channel_post(client: Client, message: Message):
    reply_text = await message.reply_text("Please Wait...!", quote=True)
    try:
        video_path = None
        sample_video_path = "sample_video.mp4"  # Path to save the 30-second sample video

        # Check if the message contains a video
        if message.video:
            # Download only the first 30 seconds of the video
            video_path = await message.download(file_name="partial_video.mp4", progress=None)

            # Generate a 30-second sample from the downloaded video
            generate_sample_video(video_path, sample_video_path, start_time=0, duration=30)

            # Send the 30-second sample video
            await message.reply_video(video=sample_video_path, caption="Here is your 30-second sample video.", reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={sample_video_path}')]]
            ))

            # Clean up the downloaded video and generated sample video
            os.remove(video_path)
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
