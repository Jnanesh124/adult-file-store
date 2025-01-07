import os
import asyncio
import logging
import ffmpeg
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import ADMINS, APP_ID, API_HASH, TG_BOT_TOKEN

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Initialize the bot
Bot = Client("adult_file_store", api_id=APP_ID, api_hash=API_HASH, bot_token=TG_BOT_TOKEN)

@Bot.on_message(filters.private & filters.user(ADMINS))
async def receive_file(client: Client, message: Message):
    if not (message.video or message.document):
        await message.reply_text("Please send a valid video or document.")
        return

    # Log user action
    logger.info(f"User {message.from_user.id} sent a file.")

    # Reply with buttons
    buttons = [
        [InlineKeyboardButton("🎞 Generate Sample Video", callback_data=f"generate_sample|{message.id}")],
        [InlineKeyboardButton("📸 Generate Screenshot", callback_data=f"generate_screenshot|{message.id}")],
        [InlineKeyboardButton("🖼 Extract Thumbnail", callback_data=f"extract_thumbnail|{message.id}")]
    ]

    await message.reply_text(
        "What would you like to do?",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


@Bot.on_callback_query()
async def handle_callbacks(client: Client, callback_query: CallbackQuery):
    try:
        action, message_id = callback_query.data.split("|")
        user_id = callback_query.from_user.id
        logger.info(f"User {user_id} clicked: {action}")

        original_message = await client.get_messages(chat_id=callback_query.message.chat.id, message_ids=int(message_id))

        if original_message.video:
            file_id = original_message.video.file_id
        elif original_message.document and original_message.document.mime_type.startswith("video/"):
            file_id = original_message.document.file_id
        else:
            await callback_query.answer("Unsupported file type.", show_alert=True)
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
        logger.error(f"Error handling callback: {e}")
        await callback_query.message.reply_text("Something went wrong.")


async def generate_sample_video(client: Client, file_id: str, callback_query: CallbackQuery):
    try:
        logger.info(f"Generating sample video for file ID {file_id}")
        sample_path = f"sample_{file_id}.mp4"
        await callback_query.answer("Generating sample video...")

        input_stream = await client.download_media(file_id, file_ref=True)

        ffmpeg.input(input_stream, ss=0, t=10).output(
            sample_path, vcodec="libx264", acodec="aac"
        ).run()

        await callback_query.message.reply_video(sample_path, caption="Here's your sample video!")
        os.remove(sample_path)
    except Exception as e:
        logger.error(f"Error generating sample video: {e}")
        await callback_query.message.reply_text("Failed to generate sample video.")


async def generate_screenshot(client: Client, file_id: str, callback_query: CallbackQuery):
    try:
        logger.info(f"Generating screenshot for file ID {file_id}")
        screenshot_path = f"screenshot_{file_id}.jpg"
        await callback_query.answer("Generating screenshot...")

        input_stream = await client.download_media(file_id, file_ref=True)

        ffmpeg.input(input_stream, ss=5).output(
            screenshot_path, vframes=1
        ).run()

        await callback_query.message.reply_photo(screenshot_path, caption="Here's a screenshot!")
        os.remove(screenshot_path)
    except Exception as e:
        logger.error(f"Error generating screenshot: {e}")
        await callback_query.message.reply_text("Failed to generate screenshot.")


async def extract_thumbnail(client: Client, file_id: str, callback_query: CallbackQuery):
    try:
        logger.info(f"Extracting thumbnail for file ID {file_id}")
        thumbnail_path = f"thumbnail_{file_id}.jpg"
        await callback_query.answer("Extracting thumbnail...")

        input_stream = await client.download_media(file_id, file_ref=True)

        ffmpeg.input(input_stream, ss=1).output(
            thumbnail_path, vframes=1, vf="scale=320:-1"
        ).run()

        await callback_query.message.reply_photo(thumbnail_path, caption="Here's the extracted thumbnail!")
        os.remove(thumbnail_path)
    except Exception as e:
        logger.error(f"Error extracting thumbnail: {e}")
        await callback_query.message.reply_text("Failed to extract thumbnail.")


# Start the bot
if __name__ == "__main__":
    logger.info("Bot is starting...")
    Bot.run()
