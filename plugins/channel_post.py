import asyncio
from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
from moviepy.editor import VideoFileClip
from PIL import Image
from PyPDF2 import PdfReader
import os

from bot import Bot
from config import ADMINS, CHANNEL_ID, DISABLE_CHANNEL_BUTTON
from helper_func import encode


@Bot.on_message(filters.private & filters.user(ADMINS) & ~filters.command(['start', 'users', 'broadcast', 'batch', 'genlink', 'stats']))
async def channel_post(client: Client, message: Message):
    reply_text = await message.reply_text("Please Wait...!", quote=True)
    thumbnail_path = None

    try:
        # Handle video files
        if message.video:
            video_path = await message.download()  # Download the video file
            thumbnail_path = "thumbnail.jpg"
            clip = VideoFileClip(video_path)
            frame = clip.get_frame(0)  # Get the first frame

            # Convert the numpy array frame to an image using PIL
            image = Image.fromarray(frame)
            image.save(thumbnail_path)  # Save as a thumbnail image

            # Remove the downloaded video after use
            os.remove(video_path)

        # Handle PDF files
        elif message.document and message.document.mime_type == "application/pdf":
            pdf_path = await message.download()  # Download the PDF file
            thumbnail_path = "pdf_thumbnail.jpg"
            pdf_reader = PdfReader(pdf_path)
            first_page = pdf_reader.pages[0]
            image = first_page.extract_images()[0]  # Extract the first image
            image.save(thumbnail_path)  # Save as a thumbnail image

            # Remove the downloaded PDF after use
            os.remove(pdf_path)

        # Handle other file types (default image extraction for non-video/document files)
        elif message.document:
            file_path = await message.download()  # Download the file
            thumbnail_path = "file_thumbnail.jpg"
            image = Image.open(file_path)  # Open the file as an image
            image.thumbnail((200, 200))  # Resize to thumbnail size
            image.save(thumbnail_path)  # Save as a thumbnail image

            # Remove the downloaded file after use
            os.remove(file_path)

        # Copy the message to the channel
        post_message = await message.copy(chat_id=client.db_channel.id, disable_notification=True)

    except FloodWait as e:
        await asyncio.sleep(e.value)
        post_message = await message.copy(chat_id=client.db_channel.id, disable_notification=True)
    except Exception as e:
        print(e)
        await reply_text.edit_text("Something went wrong while processing!")
        return

    # Generate the stored link
    converted_id = post_message.id * abs(client.db_channel.id)
    string = f"get-{converted_id}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"

    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]]
    )

    # Send both the thumbnail and the link
    if thumbnail_path:
        await message.reply_photo(
            photo=thumbnail_path,
            caption=f"<b>Here is your link</b>\n\n{link}",
            reply_markup=reply_markup
        )
        os.remove(thumbnail_path)  # Clean up the thumbnail
    else:
        await reply_text.edit(
            f"<b>Here is your link</b>\n\n{link}",
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )

    if not DISABLE_CHANNEL_BUTTON:
        try:
            await post_message.edit_reply_markup(reply_markup)
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await post_message.edit_reply_markup(reply_markup)
        except Exception:
            pass


@Bot.on_message(filters.channel & filters.incoming & filters.chat(CHANNEL_ID))
async def new_post(client: Client, message: Message):
    if DISABLE_CHANNEL_BUTTON:
        return

    # Generate the stored link
    converted_id = message.id * abs(client.db_channel.id)
    string = f"get-{converted_id}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"

    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]]
    )

    try:
        await message.edit_reply_markup(reply_markup)
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await message.edit_reply_markup(reply_markup)
    except Exception:
        pass
