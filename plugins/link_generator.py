from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from helper_func import encode, decode, get_message_id

# Bot 1 (Main Bot) API credentials
API_ID_1 = 25166107  # Replace with your first bot's API ID
API_HASH_1 = "8a386f1bde254b67f917a9b2b436d0d6"  # Replace with your first bot's API Hash
BOT_TOKEN_1 = "6570037316:AAEU9Z4wvk5F6AU8EFeAXMf-gL_njebFMKg"  # Replace with your first bot's token

# Bot 2 (Secondary Bot) API credentials
API_ID_2 = 25166107  # Replace with your second bot's API ID
API_HASH_2 = "8a386f1bde254b67f917a9b2b436d0d6"  # Replace with your second bot's API Hash
BOT_TOKEN_2 = "7850868885:AAFc5n1OJ3egi7M3mLeJZI0ACyPDprbY_H8"  # Replace with your second bot's token

# DB Channel ID
DB_CHANNEL_ID = -1002446680686  # Replace with your actual DB Channel ID

# Admin IDs
ADMINS = [6643562770]  # Add admin IDs here

# Initialize bots
MainBot = Client("MainBot", api_id=API_ID_1, api_hash=API_HASH_1, bot_token=BOT_TOKEN_1)
SecondBot = Client("SecondBot", api_id=API_ID_2, api_hash=API_HASH_2, bot_token=BOT_TOKEN_2)

# Attach the DB channel attribute
MainBot.db_channel = type("db_channel", (object,), {"id": DB_CHANNEL_ID})
SecondBot.db_channel = type("db_channel", (object,), {"id": DB_CHANNEL_ID})


@MainBot.on_message(filters.private & filters.command('batch'))
async def batch(client: Client, message: Message):
    # Check if the user is an admin
    if message.from_user.id not in ADMINS:
        await message.reply_text("❌ You are not authorized to use this command.")
        return

    while True:
        try:
            # Ask for the first message
            first_message = await client.ask(
                text="Forward the **First Message** from DB Channel or send its link:",
                chat_id=message.from_user.id,
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60
            )
        except Exception as e:
            await message.reply_text(f"❌ Error: {e}")
            return

        f_msg_id = await get_message_id(client, first_message)
        if f_msg_id:
            break
        else:
            await first_message.reply_text("❌ Invalid first message. Please try again.", quote=True)

    while True:
        try:
            # Ask for the last message
            second_message = await client.ask(
                text="Now, forward the **Last Message** from DB Channel or send its link:",
                chat_id=message.from_user.id,
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60
            )
        except Exception as e:
            await message.reply_text(f"❌ Error: {e}")
            return

        s_msg_id = await get_message_id(client, second_message)
        if s_msg_id:
            break
        else:
            await second_message.reply_text("❌ Invalid last message. Please try again.", quote=True)

    # Generate the deep link
    string = f"get-{f_msg_id * abs(DB_CHANNEL_ID)}-{s_msg_id * abs(DB_CHANNEL_ID)}"
    encoded_string = await encode(string)
    redirect_link = f"https://t.me/{client.username}?start={encoded_string}"

    # Send the generated link
    await message.reply_text(
        f"Here is your generated link:\n\n{redirect_link}",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔁 Share URL", url=f"https://telegram.me/share/url?url={redirect_link}")]]
        )
    )


@SecondBot.on_message(filters.private & filters.command('start'))
async def start_secondary(client: Client, message: Message):
    if len(message.command) > 1:
        parameter = message.command[1]
        try:
            decoded = await decode(parameter)
            if decoded.startswith("get-"):
                html_link = f"https://jn2flix.blogspot.com/2025/01/j1.html?JN2FLIX={parameter}"
                await message.reply_text(
                    "Click the button below to proceed to the link:",
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("📂 Open Page", url=html_link)]]
                    )
                )
            else:
                await message.reply_text("❌ Invalid parameter!")
        except Exception as e:
            await message.reply_text(f"❌ Error: {e}")
    else:
        await message.reply_text(
            "Welcome to the Secondary Bot! Use /start with a parameter to get started.",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔗 Help", url="https://t.me/JN2FLIX")]]
            )
        )


if __name__ == "__main__":
    try:
        MainBot.start()
        SecondBot.start()
        print("Both bots are running.")
        MainBot.idle()
        SecondBot.idle()
    except KeyboardInterrupt:
        print("Bots stopped.")
