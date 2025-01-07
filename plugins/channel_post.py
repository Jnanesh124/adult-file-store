import asyncio
from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait
import os
import ffmpeg
import logging

from bot import Bot
from config import ADMINS

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

@Bot.on_message(filters.private & filters.user(ADMINS) & ~filters.command(['start', 'users', 'broadcast', 'batch', 'genlink', 'stats']))
async def channel_post(client: Client, message: Message):
    if not (message.video or message.document or message.animation):
        await message.reply_text("Please send a valid video or document.")
        return

    buttons = [
        [InlineKeyboardButton("🎞 Generate Sample Video", callback_data="generate_sample")],
        [InlineKeyboardButton("📸 Generate Screenshot", callback_data="generate_screenshot")],
        [InlineKeyboardButton("🖼 Extract Thumbnail", callback_data="extract_thumbnail")]
    ]

    await message.reply_text(
        "What would you like to do?",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def generate_sample_video(client: Client, file_id: str, message: Message):
    sample_path = f"sample_{file_id}.mp4"
    try:
        input_stream = await client.download_media(file_id, file_ref=True)
        ffmpeg.input(input_stream, ss=0, t=10).output(
            sample_path, vcodec="libx264", acodec="aac"
        ).run()

        await message.reply_video(sample_path, caption="Here's your sample video!")
        os.remove(sample_path)
    except Exception as e:
        logging.error(f"Error generating sample video: {e}")
        await message.reply_text("Failed to generate sample video.")

async def generate_screenshot(client: Client, file_id: str, message: Message):
    screenshot_path = f"screenshot_{file_id}.jpg"
    try:
        input_stream = await client.download_media(file_id, file_ref=True)
        ffmpeg.input(input_stream, ss=5).output(
            screenshot_path, vframes=1
        ).run()

        await message.reply_photo(screenshot_path, caption="Here's a screenshot!")
        os.remove(screenshot_path)
    except Exception as e:
        logging.error(f"Error generating screenshot: {e}")
        await message.reply_text("Failed to generate screenshot.")

async def extract_thumbnail(client: Client, file_id: str, message: Message):
    thumbnail_path = f"thumbnail_{file_id}.jpg"
    try:
        input_stream = await client.download_media(file_id, file_ref=True)
        ffmpeg.input(input_stream, ss=1).output(
            thumbnail_path, vframes=1, vf="scale=320:-1"
        ).run()

        await message.reply_photo(thumbnail_path, caption="Here's the extracted thumbnail!")
        os.remove(thumbnail_path)
    except Exception as e:
        logging.error(f"Error extracting thumbnail: {e}")
        await message.reply_text("Failed to extract thumbnail.")

@Bot.on_callback_query()
async def handle_callbacks(client: Client, callback_query: CallbackQuery):
    user = callback_query.from_user.id
    data = callback_query.data
    message = callback_query.message

    if user not in ADMINS:
        await callback_query.answer("You're not allowed to perform this action.", show_alert=True)
        return

    await callback_query.answer("Processing...")
    msg = await message.reply_text("Downloading media...")

    try:
        if message.reply_to_message.video:
            file_id = message.reply_to_message.video.file_id
        elif message.reply_to_message.document and message.reply_to_message.document.mime_type.startswith("video/"):
            file_id = message.reply_to_message.document.file_id
        else:
            await msg.edit_text("Unsupported file type.")
            return

        # Handle callbacks for sample video, screenshot, and thumbnail
        if data == "generate_sample":
            await generate_sample_video(client, file_id, message)
        elif data == "generate_screenshot":
            await generate_screenshot(client, file_id, message)
        elif data == "extract_thumbnail":
            await extract_thumbnail(client, file_id, message)

        await msg.delete()

    except Exception as e:
        logging.error(f"Error in callback: {e}")
        await msg.edit_text("Something went wrong!")

@Bot.on_message(filters.channel & filters.incoming)
async def new_post(client: Client, message: Message):
    # Placeholder for channel posts logic
    pass
