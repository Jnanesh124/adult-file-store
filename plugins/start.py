from pymongo import MongoClient
import asyncio
import base64
import logging
import os
import random
import re
import string
import time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pyrogram import Client, filters, __version__
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated
from datetime import datetime, timedelta
from bot import Bot
from config import *
from helper_func import subscribed, encode, decode, get_messages, get_shortlink, get_verify_status, update_verify_status, get_exp_time
from database.database import add_user, del_user, full_userbase, present_user
from shortzy import Shortzy

client = MongoClient(DB_URI)  # Replace with your MongoDB URI
db = client[DB_NAME]  # Database name
phdlust = db["phdlust"]  # Collection for users
phdlust_tasks = db["phdlust_tasks"] 

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to add a delete task to the database
async def add_delete_task(chat_id, message_id, delete_at):
    phdlust_tasks.insert_one({
        "chat_id": chat_id,
        "message_id": message_id,
        "delete_at": delete_at
    })

# Function to delete the notification after a set delay
async def delete_notification(client, chat_id, notification_id, delay):
    await asyncio.sleep(delay)
    try:
        # Delete the notification message
        await client.delete_messages(chat_id=chat_id, message_ids=notification_id)
    except Exception as e:
        print(f"Error deleting notification {notification_id} in chat {chat_id}: {e}")
        
async def schedule_auto_delete(client, chat_id, message_id, delay):
    delete_at = datetime.now() + timedelta(seconds=int(delay))
    await add_delete_task(chat_id, message_id, delete_at)
    
    # Run deletion in the background to prevent blocking
    async def delete_message():
        await asyncio.sleep(int(delay))
        try:
            # Delete the original message
            await client.delete_messages(chat_id=chat_id, message_ids=message_id)
            phdlust_tasks.delete_one({"chat_id": chat_id, "message_id": message_id})  # Remove from DB
            # Send a notification about the deletion
            notification_text = DELETE_INFORM
            notification_msg = await client.send_message(chat_id, notification_text)
            
            # Schedule deletion of the notification after 60 seconds
            asyncio.create_task(delete_notification(client, chat_id, notification_msg.id, 40))
        except Exception as e:
            print(f"Error deleting message {message_id} in chat {chat_id}: {e}")

    asyncio.create_task(delete_message())  

# Start command handler
@Bot.on_message(filters.command('start') & filters.private)
async def start_command(client: Client, message: Message):
    id = message.from_user.id
    UBAN = BAN  # Owner ID from config

    # List of images for verification instructions
    verification_images = [
        "https://ibb.co/9hny76C",
        "https://ibb.co/v1jVQ92",
        "https://ibb.co/WnhBWd1",
        "https://ibb.co/HrDcV7s",
        "https://ibb.co/djZPV6T",
        "https://ibb.co/5GT6j5k"
    ]

    # Randomly select an image
    random_image = random.choice(verification_images)

    # Check if the user is the owner
    if id == UBAN:
        sent_message = await message.reply("You are the U-BAN! Additional actions can be added here.")
    else:
        if not await present_user(id):
            try:
                await add_user(id)
            except:
                pass

        verify_status = await get_verify_status(id)
        if verify_status['is_verified'] and VERIFY_EXPIRE < (time.time() - verify_status['verified_time']):
            await update_verify_status(id, is_verified=False)

        if "verify_" in message.text:
            _, token = message.text.split("_", 1)
            if verify_status['verify_token'] != token:
                return await message.reply("Your token is invalid or expired. Try again by clicking /start")
            await update_verify_status(id, is_verified=True, verified_time=time.time())
            if verify_status["link"] == "":
                reply_markup = None
            await message.reply(
                f"Your token has been successfully verified and is valid for: 24 hours\n\nVerification successful!",
                reply_markup=reply_markup,
                protect_content=False,
                quote=True
            )

            # Send both success message and random verification image in a single reply
            await message.reply_photo(random_image, caption="Here’s a guide on what to do next. Your verification is successful!")

        elif len(message.text) > 7 and verify_status['is_verified']:
            # Direct file delivery logic (assuming that the file can be directly delivered when verified)
            await send_file_to_user(message, client, verify_status)
            
        elif verify_status['is_verified']:
            # Send a success message and access link after verification
            await message.reply_text(
                "You are successfully verified! Here’s your direct access link:",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("Access Link", url="https://example.com/your_direct_link")
                ]])
            )

            # Send random image with success text and direct access link in a single message
            await message.reply_photo(random_image, caption="Verification successful! You now have access.")
        
        else:
            # User is not verified: Send random image and verification instructions with tutorial link and verification button
            token = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            await update_verify_status(id, verify_token=token, link="")

            link = await get_shortlink(SHORTLINK_URL, SHORTLINK_API, f'https://telegram.dog/{client.username}?start=verify_{token}')
            btn = [
                [InlineKeyboardButton("Click here to verify", url=link)],
                [InlineKeyboardButton('How to use the bot', url="https://www.youtube.com/channel/UC7tAa4hho37iNv731_6RIOg")]
            ]

            # Send a verification message with random image and tutorial link in a single reply
            await message.reply(
                f"<strong>You need to verify first. After 24 hours, your verification expires.</strong>",
                reply_markup=InlineKeyboardMarkup(btn),
                protect_content=False,
                quote=True
            )

            # Send random image with verification message in a single reply
            await message.reply_photo(random_image, caption="Follow the instructions in the image to verify.")

# Helper function for sending file if the user is verified
async def send_file_to_user(message, client, verify_status):
    # Logic to send the file to the user based on the IDs in the verify_status
    # Example of sending a file
    file_id = verify_status.get("file_id")  # Replace with actual logic to get the file ID
    if file_id:
        await client.send_document(
            message.chat.id,
            file_id,
            caption="Here is the file you requested.",
            reply_markup=None  # Modify this as needed for additional buttons
        )

# User not joined handler
@Bot.on_message(filters.command('start') & filters.private)
async def not_joined(client: Client, message: Message):
    buttons = [
        [InlineKeyboardButton(
            "Join Channel", url=f"https://t.me/+0S0i5fWcJUZjODJl"),
         InlineKeyboardButton(
            "Join Channel", url=client.invitelink)],
        [InlineKeyboardButton(
            "Join Channel", url=f"https://t.me/+jc7Wwu1pxMc1MTFl"),
         InlineKeyboardButton(
            "Join Channel", url=f"https://t.me/+cw0DyuLqmdk1NTE1")]
    ]
    try:
        buttons.append([InlineKeyboardButton(
            text='Try Again',
            url=f"https://t.me/{client.username}?start={message.command[1]}")])
    except IndexError:
        pass

    await message.reply(
        text=FORCE_MSG.format(
            first=message.from_user.first_name,
            last=message.from_user.last_name,
            username=None if not message.from_user.username else '@' + message.from_user.username,
            mention=message.from_user.mention,
            id=message.from_user.id
        ),
        reply_markup=InlineKeyboardMarkup(buttons),
        quote=True,
        disable_web_page_preview=True
    )

# Broadcast message handler for admins
@Bot.on_message(filters.command('broadcast') & filters.private & filters.user(ADMINS))
async def send_text(client: Bot, message: Message):
    if message.reply_to_message:
        query = await full_userbase()
        broadcast_msg = message.reply_to_message
        total = 0
        successful = 0
        blocked = 0
        deleted = 0
        unsuccessful = 0
        
        pls_wait = await message.reply("<i>Broadcasting Message.. This will Take Some Time</i>")
        for chat_id in query:
            try:
                await broadcast_msg.copy(chat_id)
                successful += 1
            except FloodWait as e:
                await asyncio.sleep(e.x)
                await broadcast_msg.copy(chat_id)
                successful += 1
            except UserIsBlocked:
                await del_user(chat_id)
                blocked += 1
            except InputUserDeactivated:
                await del_user(chat_id)
                deleted += 1
            except Exception as e:
                unsuccessful += 1
                pass

        await pls_wait.delete()

        return await message.reply(
            text=SEND_BROADCAST.format(
                total=total,
                successful=successful,
                blocked=blocked,
                deleted=deleted,
                unsuccessful=unsuccessful
            )
        )

