import asyncio
from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import os
import ffmpeg
import logging

from bot import Bot
from config import ADMINS

logging.basicConfig(level=logging.INFO)

@Bot.on_message(filters.private & filters.user(ADMINS) & ~filters.command(['start', 'users', 'broadcast', 'batch', 'genlink', 'stats']))
async def channel_post(client: Client, message: Message):
    if not (message.video or message.document or message.animation):
        await message.reply_text("Please send a valid video or document.")
        return

    buttons = [
        [InlineKeyboardButton("🎞 Generate Sample Video", callback_data=f"generate_sample|{message.id}")],
        [InlineKeyboardButton("📸 Generate Screenshot", callback_data=f"generate_screenshot|{message.id}")],
        [InlineKeyboardButton("🖼 Extract Thumbnail", callback_data=f"extract_thumbnail|{message.id}")]
    ]

    await message.reply_text(
        "What would you like to do?",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


async def generate_sample_video(client: Client, file_id: str, callback_query: CallbackQuery):
    try:
        sample_path = f"sample_{file_id}.mp4"
        await callback_query.answer("Generating sample video...")
        input_stream = await client.download_media(file_id, file_ref=True)

        ffmpeg.input(input_stream, ss=0, t=10).output(
            sample_path, vcodec="libx264", acodec="aac"
        ).run()

        await callback_query.message.reply_video(sample_path, caption="Here's your sample video!")
        os.remove(sample_path)
    except Exception as e:
        logging.error(f"Error generating sample video: {e}")
        await callback_query.message.reply_text("Failed to generate sample video.")


async def generate_screenshot(client: Client, file_id: str, callback_query: CallbackQuery):
    try:
        screenshot_path = f"screenshot_{file_id}.jpg"
        await callback_query.answer("Generating screenshot...")
        input_stream = await client.download_media(file_id, file_ref=True)

        ffmpeg.input(input_stream, ss=5).output(
            screenshot_path, vframes=1
        ).run()

        await callback_query.message.reply_photo(screenshot_path, caption="Here's a screenshot!")
        os.remove(screenshot_path)
    except Exception as e:
        logging.error(f"Error generating screenshot: {e}")
        await callback_query.message.reply_text("Failed to generate screenshot.")


async def extract_thumbnail(client: Client, file_id: str, callback_query: CallbackQuery):
    try:
        thumbnail_path = f"thumbnail_{file_id}.jpg"
        await callback_query.answer("Extracting thumbnail...")
        input_stream = await client.download_media(file_id, file_ref=True)

        ffmpeg.input(input_stream, ss=1).output(
            thumbnail_path, vframes=1, vf="scale=320:-1"
        ).run()

        await callback_query.message.reply_photo(thumbnail_path, caption="Here's the extracted thumbnail!")
        os.remove(thumbnail_path)
    except Exception as e:
        logging.error(f"Error extracting thumbnail: {e}")
        await callback_query.message.reply_text("Failed to extract thumbnail.")


@Bot.on_callback_query()
async def handle_callbacks(client: Client, callback_query: CallbackQuery):
    data = callback_query.data
    if "|" not in data:
        await callback_query.answer("Invalid action.", show_alert=True)
        return

    action, message_id = data.split("|")

    try:
        # Fetch the original message to retrieve the file
        original_message = await client.get_messages(
            chat_id=callback_query.message.chat.id, message_ids=int(message_id)
        )

        if original_message.video:
            file_id = original_message.video.file_id
        elif original_message.document and original_message.document.mime_type.startswith("video/"):
            file_id = original_message.document.file_id
        else:
            await callback_query.message.reply_text("Unsupported file type.")
            return

        if action == "generate_sample":
            await generate_sample_video(client, file_id, callback_query)
        elif action == "generate_screenshot":
            await generate_screenshot(client, file_id, callback_query)
        elif action == "extract_thumbnail":
            await extract_thumbnail(client, file_id, callback_query)
        else:
            await callback_query.answer("Unknown action.", show_alert=True)

    except Exception as e:
        logging.error(f"Error handling callback: {e}")
        await callback_query.message.reply_text("Something went wrong.")
