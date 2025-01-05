import os
import json
import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated

from bot import Bot
from config import ADMINS, FORCE_MSG, START_MSG, CUSTOM_CAPTION, DISABLE_CHANNEL_BUTTON, PROTECT_CONTENT, AUTO_DELETE_TIME, AUTO_DELETE_MSG, JOIN_REQUEST_ENABLE, FORCE_SUB_CHANNEL
from helper_func import subscribed, decode, get_messages, delete_file
from database.database import add_user, del_user, full_userbase, present_user

BROADCASTED_USERS_FILE = "broadcasted_users.json"

# Load the broadcasted users from a file
def load_broadcasted_users():
    if os.path.exists(BROADCASTED_USERS_FILE):
        with open(BROADCASTED_USERS_FILE, "r") as f:
            try:
                data = json.load(f)
                return data if data else []  # If the data is None or empty, return an empty list
            except json.JSONDecodeError:
                print(f"Error decoding JSON from {BROADCASTED_USERS_FILE}. Returning empty list.")
                return []
    return []

# Save the broadcasted users to a file
def save_broadcasted_users(broadcasted_users):
    with open(BROADCASTED_USERS_FILE, "w") as f:
        json.dump(broadcasted_users, f)

@Bot.on_message(filters.command('start') & filters.private & subscribed)
async def start_command(client: Client, message: Message):
    user_id = message.from_user.id
    if not await present_user(user_id):
        try:
            await add_user(user_id)
        except:
            pass

    text = message.text
    if len(text) > 7:
        try:
            base64_string = text.split(" ", 1)[1]
        except:
            return
        string = await decode(base64_string)
        argument = string.split("-")
        ids = []

        if len(argument) == 3:
            try:
                start = int(int(argument[1]) / abs(client.db_channel.id))
                end = int(int(argument[2]) / abs(client.db_channel.id))
                ids = range(start, end + 1) if start <= end else range(start, end - 1, -1)
            except:
                return
        elif len(argument) == 2:
            try:
                ids = [int(int(argument[1]) / abs(client.db_channel.id))]
            except:
                return

        temp_msg = await message.reply("Please wait...")
        try:
            messages = await get_messages(client, ids)
        except:
            await message.reply_text("Something went wrong..!")
            return
        await temp_msg.delete()

        track_msgs = []
        for msg in messages:
            caption = (
                CUSTOM_CAPTION.format(
                    previouscaption="" if not msg.caption else msg.caption.html,
                    filename=msg.document.file_name
                )
                if CUSTOM_CAPTION and msg.document
                else "" if not msg.caption else msg.caption.html
            )

            reply_markup = msg.reply_markup if DISABLE_CHANNEL_BUTTON else None

            try:
                copied_msg = await msg.copy(
                    chat_id=message.from_user.id,
                    caption=caption,
                    parse_mode=ParseMode.HTML,
                    reply_markup=reply_markup,
                    protect_content=PROTECT_CONTENT
                )
                if AUTO_DELETE_TIME:
                    track_msgs.append(copied_msg)
            except FloodWait as e:
                await asyncio.sleep(e.value)
                copied_msg = await msg.copy(
                    chat_id=message.from_user.id,
                    caption=caption,
                    parse_mode=ParseMode.HTML,
                    reply_markup=reply_markup,
                    protect_content=PROTECT_CONTENT
                )
                if AUTO_DELETE_TIME:
                    track_msgs.append(copied_msg)
            except:
                pass

        if track_msgs:
            delete_data = await client.send_message(
                chat_id=message.from_user.id,
                text=AUTO_DELETE_MSG.format(time=AUTO_DELETE_TIME)
            )
            asyncio.create_task(delete_file(track_msgs, client, delete_data))
        return

    else:
        reply_markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("MAIN CHANNEL", url=f"t.me/JN2FLIX"),
                    InlineKeyboardButton("🔒 Close ", callback_data="close")
                ]
            ]
        )

        await message.reply_text(
            text=START_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=None if not message.from_user.username else '@' + message.from_user.username,
                mention=message.from_user.mention,
                id=message.from_user.id
            ),
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            quote=True
        )


@Bot.on_message(filters.command('start') & filters.private)
async def not_joined(client: Client, message: Message):
    if JOIN_REQUEST_ENABLE:
        invite = await client.create_chat_invite_link(
            chat_id=FORCE_SUB_CHANNEL,
            creates_join_request=True
        )
        ButtonUrl = invite.invite_link
    else:
        ButtonUrl = client.invitelink

    buttons = [[InlineKeyboardButton("Join Channel", url=ButtonUrl)]]
    try:
        buttons.append([
            InlineKeyboardButton(
                text='Try Again',
                url=f"https://t.me/{client.username}?start={message.command[1]}"
            )
        ])
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


@Bot.on_message(filters.command('users') & filters.private & filters.user(ADMINS))
async def get_users(client: Bot, message: Message):
    msg = await client.send_message(chat_id=message.chat.id, text="Processing...")
    users = await full_userbase()
    await msg.edit(f"{len(users)} users are using this bot")

@Bot.on_message(filters.private & filters.command('broadcast') & filters.user(ADMINS))
async def send_text(client: Client, message: Message):
    if message.reply_to_message:
        query = await full_userbase()  # Get all user IDs
        broadcast_msg = message.reply_to_message
        total = 0
        successful = 0
        blocked = 0
        deleted = 0
        unsuccessful = 0

        pls_wait = await message.reply("<i>Broadcasting Message.. This will Take Some Time</i>")

        # Load the list of already broadcasted users
        broadcasted_users = load_broadcasted_users()

        # Filter out already broadcasted users
        users_to_broadcast = [chat_id for chat_id in query if chat_id not in broadcasted_users]

        # Create a list of tasks for parallel execution
        tasks = []
        for chat_id in users_to_broadcast:
            task = send_broadcast(broadcast_msg, chat_id, broadcasted_users)
            tasks.append(task)

        # Run all the tasks concurrently
        await asyncio.gather(*tasks)

        # Save the list of broadcasted users
        save_broadcasted_users(broadcasted_users)

        status = f"""<b><u>Broadcast Completed</u>

Total Users: <code>{len(query)}</code>
Successful: <code>{successful}</code>
Blocked Users: <code>{blocked}</code>
Deleted Accounts: <code>{deleted}</code>
Unsuccessful: <code>{unsuccessful}</code></b>"""

        await pls_wait.edit(status)
    else:
        msg = await message.reply("Use this command as a reply to any telegram message without spaces.")
        await asyncio.sleep(8)
        await msg.delete()

async def send_broadcast(broadcast_msg, chat_id, broadcasted_users):
    global successful, blocked, deleted, unsuccessful

    try:
        await broadcast_msg.copy(chat_id)  # Send the broadcast message to the user
        broadcasted_users.append(chat_id)  # Add user to the list of broadcasted users
        successful += 1
        await asyncio.sleep(0.03)  # Adjust sleep to respect rate limits
    except FloodWait as e:
        await asyncio.sleep(e.value)  # Wait the required time before retrying
        await broadcast_msg.copy(chat_id)
        successful += 1
    except UserIsBlocked:
        blocked += 1
    except InputUserDeactivated:
        deleted += 1
    except Exception as e:
        print(f"Error sending message to {chat_id}: {str(e)}")
        unsuccessful += 1
