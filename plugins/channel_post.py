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
        [InlineKeyboardButton("🎞 Generate Sample Video", callback_data=f"generate_sample|{message.message_id}")],
        [InlineKeyboardButton("📸 Generate Screenshot", callback_data=f"generate_screenshot|{message.message_id}")],
        [InlineKeyboardButton("🖼 Extract Thumbnail", callback_data=f"extract_thumbnail|{message.message_id}")]
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

    # Extract the action and original message ID from the callback data
    try:
        action, original_message_id = data.split("|")
    except ValueError:
        logging.error("Invalid callback data format.")
        return

    # Fetch the original message to retrieve the file
    original_message = await client.get_messages(chat_id=callback_query.message.chat.id, message_ids=int(original_message_id))
    if not original_message or not (original_message.video or original_message.document):
        await message.edit_text("Original media not found.")
        return

    msg = await message.reply_text("Downloading media...")

    try:
        if original_message.video:
            file_id = original_message.video.file_id
        elif original_message.document and original_message.document.mime_type.startswith("video/"):
            file_id = original_message.document.file_id
        else:
            await msg.edit_text("Unsupported file type.")
            return

        if action == "generate_sample":
            await generate_sample_video(client, file_id, original_message)
        elif action == "generate_screenshot":
            await generate_screenshot(client, file_id, original_message)
        elif action == "extract_thumbnail":
            await extract_thumbnail(client, file_id, original_message)

        await msg.delete()

    except Exception as e:
        logging.error(f"Error in callback: {e}")
        await msg.edit_text("Something went wrong!")


@Bot.on_message(filters.channel & filters.incoming)
async def new_post(client: Client, message: Message):
    # Placeholder for channel posts logic
    pass
