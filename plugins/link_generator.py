import base64
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot import Bot
from config import ADMINS
from helper_func import get_message_id

# In-memory store for user states (use a database for production)
user_states = {}

# Helper functions for encoding and decoding
async def encode(data: str) -> str:
    """Encode a string using base64 encoding."""
    return base64.b64encode(data.encode("utf-8")).decode("utf-8")


async def decode(data: str) -> str:
    """Decode a base64-encoded string."""
    try:
        return base64.b64decode(data.encode("utf-8")).decode("utf-8")
    except Exception:
        return "invalid"


@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('batch'))
async def batch(client: Client, message: Message):
    while True:
        try:
            first_message = await client.ask(
                text="Forward the First Message from DB Channel (with Quotes)..\n\nor Send the DB Channel Post Link",
                chat_id=message.from_user.id,
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60
            )
        except:
            return
        f_msg_id = await get_message_id(client, first_message)
        if f_msg_id:
            break
        else:
            await first_message.reply(
                "❌ Error\n\nThis Forwarded Post is not from my DB Channel or this Link is not from DB Channel",
                quote=True
            )
            continue

    while True:
        try:
            second_message = await client.ask(
                text="Forward the Last Message from DB Channel (with Quotes)..\nor Send the DB Channel Post link",
                chat_id=message.from_user.id,
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60
            )
        except:
            return
        s_msg_id = await get_message_id(client, second_message)
        if s_msg_id:
            break
        else:
            await second_message.reply(
                "❌ Error\n\nThis Forwarded Post is not from my DB Channel or this Link is not from DB Channel",
                quote=True
            )
            continue

    # Generate a unique deep link
    string = f"get-{f_msg_id * abs(client.db_channel.id)}-{s_msg_id * abs(client.db_channel.id)}"
    base64_string = await encode(string)
    deep_link = f"https://t.me/{client.username}?start={base64_string}"
    
    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={deep_link}')]]
    )
    await second_message.reply_text(
        f"<strong>480P 720P 720PHEVC 1080P 📂\n\n{deep_link}\n\n"
        "▪️▪️▪️▪️▪️▪️▪️▪️▪️▪️▪️▪️▪️\nJoin Backup channel @JN2FLIX\n▪️▪️▪️▪️▪️▪️▪️▪️▪️▪️▪️▪️▪️</strong>",
        quote=True,
        reply_markup=reply_markup
    )


@Bot.on_message(filters.private & filters.command('start'))
async def start(client: Client, message: Message):
    if len(message.command) > 1:
        # Process the deep link parameter
        parameter = message.command[1]
        decoded = await decode(parameter)  # Use the decode function
        if decoded.startswith("get-"):
            # Store the user's state for tracking
            user_states[message.from_user.id] = {
                "parameter": parameter,
                "completed": False
            }

            # Redirect the user to the first HTML page
            html_link = f"https://jn2flix.blogspot.com/2025/01/j1.html?JN2FLIX={parameter}"
            await message.reply_text(
                f"<strong>Click the button below to proceed:</strong>",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("📂 Open Page", url=html_link)]]
                )
            )
        else:
            await message.reply_text("❌ Invalid start parameter!")
    else:
        if user_states.get(message.from_user.id, {}).get("completed"):
            # If the user has completed the process, send the file
            await message.reply_document(
                document="/mnt/data/my_files/requested_file.mp4",  # File path updated
                caption="Here is your requested file!"
            )
        else:
            await message.reply_text(
                "Welcome! Use the bot to generate and share links.",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("🔗 About", url="https://t.me/JN2FLIX")]]
                )
            )


@Bot.on_message(filters.private & filters.text)
async def handle_return(client: Client, message: Message):
    """Handle the return message after the redirection process."""
    user_state = user_states.get(message.from_user.id)
    if user_state and not user_state["completed"]:
        # Mark the process as completed
        user_states[message.from_user.id]["completed"] = True

        # Send the file to the user
        await message.reply_document(
            document="/mnt/data/my_files/requested_file.mp4",  # File path updated
            caption="Here is your requested file!"
        )
    else:
        await message.reply_text("I couldn't understand your request. Please restart.")
