import asyncio
import os
import shutil
import zipfile
from mega import Mega
from pymongo import MongoClient
from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait

from bot import Bot
from config import ADMINS, CHUNK_SIZE_MB
from helper_func import encode

CHUNK_SIZE_BYTES = CHUNK_SIZE_MB * 1024 * 1024  # Convert MB to bytes

# MongoDB connection
mongo_client = MongoClient("mongodb+srv://easyeasy740:easyeasy740@cluster0.1shrvws.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = mongo_client["file_progress"]
collection = db["progress"]

# Mega instance
mega = Mega()


@Bot.on_message(filters.private & filters.user(ADMINS) & filters.regex(r"https://mega\.nz/"))
async def handle_mega_link(client: Client, message: Message):
    link = message.text.strip()
    reply_text = await message.reply_text("Processing Mega link...", quote=True)

    # Fetch progress from MongoDB for resumption
    progress = collection.find_one({"link": link}) or {
        "link": link,
        "total_size": 0,
        "downloaded_size": 0,
        "uploaded_chunks": [],
        "current_step": "Initializing"
    }

    chunk_dir = None  # Initialize chunk_dir to None in case of early exit

    try:
        mega_client = mega.login()
        mega_file = mega_client.get_public_url_info(link)

        # Initialize progress if it's a new link
        if progress["total_size"] == 0:
            progress["total_size"] = mega_file['size']
            progress["file_name"] = mega_file['name']
            collection.update_one({"link": link}, {"$set": progress}, upsert=True)

        total_size = progress["total_size"]
        file_name = progress["file_name"]
        downloaded_size = progress["downloaded_size"]

        # Update and notify progress
        await update_progress(reply_text, progress)

        # Download and upload in 500MB chunks
        chunk_dir = f"temp/{file_name}"
        os.makedirs(chunk_dir, exist_ok=True)

        while downloaded_size < total_size:
            chunk_path = mega_client.download_url(link, dest_path=chunk_dir, chunk_size=CHUNK_SIZE_BYTES)
            downloaded_size += CHUNK_SIZE_BYTES
            progress["downloaded_size"] = downloaded_size
            progress["current_step"] = f"Downloading: {downloaded_size / (1024**2):.2f} MB / {total_size / (1024**3):.2f} GB"
            collection.update_one({"link": link}, {"$set": progress})

            # Notify the user
            await update_progress(reply_text, progress)

            # Zip the chunk
            zip_path = create_zip(chunk_path)
            progress["current_step"] = "Zipping completed, uploading..."
            collection.update_one({"link": link}, {"$set": progress})

            # Upload chunk
            await upload_file(client, zip_path, message, progress)

            # Cleanup
            shutil.rmtree(chunk_path)
            os.remove(zip_path)

        progress["current_step"] = "All chunks uploaded successfully!"
        collection.update_one({"link": link}, {"$set": progress})
        await update_progress(reply_text, progress)

    except FloodWait as e:
        await asyncio.sleep(e.value)
    except Exception as e:
        print(e)
        progress["current_step"] = f"Error: {str(e)}"
        collection.update_one({"link": link}, {"$set": progress})
        await reply_text.edit_text("An error occurred while processing the Mega link.")
    finally:
        if chunk_dir and os.path.exists(chunk_dir):
            shutil.rmtree(chunk_dir)


def create_zip(directory):
    """Creates a ZIP archive for the given directory."""
    zip_path = f"{directory}.zip"
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, start=directory)
                zipf.write(file_path, arcname=arcname)
    return zip_path


async def upload_file(client, file_path, message, progress):
    """Uploads the given file to Telegram."""
    try:
        file_size = os.path.getsize(file_path)
        file_name = os.path.basename(file_path)
        if file_size > 2 * 1024 * 1024 * 1024:  # Telegram limit: 2GB
            progress["current_step"] = f"Skipping {file_name} (exceeds 2GB)"
            collection.update_one({"link": progress["link"]}, {"$set": progress})
            return

        progress["current_step"] = f"Uploading: {file_name}"
        collection.update_one({"link": progress["link"]}, {"$set": progress})
        await update_progress(message, progress)

        sent_message = await client.send_document(
            chat_id=message.chat.id,
            document=file_path,
            caption=f"Chunk: {file_name}"
        )

        progress["uploaded_chunks"].append(file_name)
        collection.update_one({"link": progress["link"]}, {"$set": progress})
    except Exception as e:
        print(f"Error uploading file: {e}")
        progress["current_step"] = f"Error uploading {file_name}: {str(e)}"
        collection.update_one({"link": progress["link"]}, {"$set": progress})


async def update_progress(reply_text, progress):
    """Updates the progress message with live statistics."""
    downloaded_mb = progress.get("downloaded_size", 0) / (1024**2)
    total_gb = progress.get("total_size", 0) / (1024**3)
    uploaded_chunks = len(progress.get("uploaded_chunks", []))
    current_step = progress.get("current_step", "Initializing...")

    await reply_text.edit_text(
        f"**Progress Update:**\n"
        f"- Total Size: {total_gb:.2f} GB\n"
        f"- Downloaded: {downloaded_mb:.2f} MB\n"
        f"- Uploaded Chunks: {uploaded_chunks}\n"
        f"- Current Step: {current_step}"
    )
