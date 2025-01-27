import asyncio
from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
import os

from bot import Bot
from config import ADMINS, CHANNEL_ID, DISABLE_CHANNEL_BUTTON
from helper_func import encode
from pymongo import MongoClient

# MongoDB connection setup with your provided URL
client_db = MongoClient("mongodb+srv://easyeasy740:easyeasy740@cluster0.1shrvws.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client_db["movie_db"]
movies_collection = db["movies"]

# Indexing related functions
async def index_file(message, client):
    thumbnail_path = None
    try:
        # Check for video, document, or animation (media files)
        if message.video and message.video.thumbs:
            thumbnail = message.video.thumbs[0].file_id
            thumbnail_path = await client.download_media(thumbnail)
        elif message.document and message.document.thumbs:
            thumbnail = message.document.thumbs[0].file_id
            thumbnail_path = await client.download_media(thumbnail)
        elif message.animation and message.animation.thumbs:
            thumbnail = message.animation.thumbs[0].file_id
            thumbnail_path = await client.download_media(thumbnail)
        
        # Generate the link for the media
        converted_id = message.id * abs(client.db_channel.id)
        string = f"get-{converted_id}"
        base64_string = await encode(string)
        link = f"https://t.me/{client.username}?start={base64_string}"

        # Save media details to the MongoDB database
        movie_data = {
            "file_id": message.id,
            "file_name": message.caption or message.text,
            "file_link": link,
            "type": "video" if message.video else "document" if message.document else "animation",
        }

        # Insert movie data into MongoDB
        movies_collection.update_one({"file_id": message.id}, {"$set": movie_data}, upsert=True)

        # Send reply with link and share button
        caption = f"<strong>🥵 DIRECT VIDEO 📂 👇\n\n{link}</strong>"
        await message.reply_text(caption, reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]]
        ))

        # Clean up
        if thumbnail_path:
            os.remove(thumbnail_path)

    except Exception as e:
        print(f"Error in indexing file: {e}")

# Index Command (/index)
@Bot.on_message(filters.private & filters.command('index') & filters.user(ADMINS))
async def index_files(bot, message: Message):
    reply_text = await message.reply_text("Fetching and indexing files. Please wait...")

    try:
        # Fetch all files from the channel for indexing
        async for msg in bot.get_chat_history(CHANNEL_ID):
            # Check if it's a media message and index it
            if msg.video or msg.document or msg.animation:
                await index_file(msg, bot)

        await reply_text.edit_text("Indexing completed! All files are now indexed.")
    except Exception as e:
        print(f"Error during indexing: {e}")
        await reply_text.edit_text("An error occurred while indexing the files.")

# Movie Search Command (/search)
@Bot.on_message(filters.private & filters.command('search'))
async def search_movie(bot, message: Message):
    movie_name = ' '.join(message.command[1:]).lower().strip()
    if not movie_name:
        return await message.reply("Please provide a movie name to search.")

    # Search in the database
    movie_data = movies_collection.find({"file_name": {"$regex": movie_name, "$options": "i"}})
    if not movie_data:
        return await message.reply("No results found for this movie.")

    # Prepare the buttons with movie links
    buttons = []
    for movie in movie_data:
        link = movie['file_link']
        buttons.append([InlineKeyboardButton(movie['file_name'], url=link)])

    # Send search results as inline buttons
    await message.reply_text("Here are the movie links:", reply_markup=InlineKeyboardMarkup(buttons))

# Show Total Files Command (/file)
@Bot.on_message(filters.private & filters.command('file') & filters.user(ADMINS))
async def show_total_files(bot, message: Message):
    total_files = movies_collection.count_documents({})
    await message.reply(f"Total indexed files: {total_files}")

# Automatically Index New Files (Live Indexing)
@Bot.on_message(filters.channel & filters.incoming & filters.chat(CHANNEL_ID))
async def new_post(bot, message: Message):
    if DISABLE_CHANNEL_BUTTON:
        return

    # Index each new post (for live indexing)
    if message.video or message.document or message.animation:
        await index_file(message, bot)

    # Prepare the link for the new post
    converted_id = message.id * abs(bot.db_channel.id)
    string = f"get-{converted_id}"
    base64_string = await encode(string)
    link = f"https://t.me/{bot.username}?start={base64_string}"

    # Edit the message reply markup to include share buttons
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]])

    try:
        await message.edit_reply_markup(reply_markup)
    except FloodWait as e:
        await asyncio.sleep(e.value)
    except Exception:
        pass
