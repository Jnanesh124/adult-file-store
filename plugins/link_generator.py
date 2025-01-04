from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from helper_func import encode, decode, get_message_id

# Bot 1 (Main Bot) API credentials
API_ID_1 = 22505271  # Replace with your first bot's API ID
API_HASH_1 = "c89a94fcfda4bc06524d0903977fc81e"  # Replace with your first bot's API Hash
BOT_TOKEN_1 = "6570037316:AAEU9Z4wvk5F6AU8EFeAXMf-gL_njebFMKg"  # Replace with your first bot's token

# Bot 2 (Secondary Bot) API credentials
API_ID_2 = 22505271  # Replace with your second bot's API ID
API_HASH_2 = "c89a94fcfda4bc06524d0903977fc81e"  # Replace with your second bot's API Hash
BOT_TOKEN_2 = "7850868885:AAFc5n1OJ3egi7M3mLeJZI0ACyPDprbY_H8"  # Replace with your second bot's token

# DB Channel ID (replace with your actual DB Channel ID)
DB_CHANNEL_ID = -1002446680686

# Initialize bots
MainBot = Client("MainBot", api_id=API_ID_1, api_hash=API_HASH_1, bot_token=BOT_TOKEN_1)
SecondBot = Client("SecondBot", api_id=API_ID_2, api_hash=API_HASH_2, bot_token=BOT_TOKEN_2)

@MainBot.on_message(filters.private & filters.command('batch'))
async def batch(client: Client, message: Message):
    try:
        # Step 1: Ask for the first message
        await message.reply_text(
            "Forward the **First Message** from the DB Channel or send its link:",
            quote=True
        )
        first_message = await client.listen(message.chat.id, timeout=60)
        f_msg_id = await get_message_id(client, first_message)
        if not f_msg_id:
            await message.reply_text("❌ Error: Invalid first message. Please try again.", quote=True)
            return

        # Step 2: Ask for the last message
        await message.reply_text(
            "Now, forward the **Last Message** from the DB Channel or send its link:",
            quote=True
        )
        second_message = await client.listen(message.chat.id, timeout=60)
        s_msg_id = await get_message_id(client, second_message)
        if not s_msg_id:
            await message.reply_text("❌ Error: Invalid last message. Please try again.", quote=True)
            return

        # Generate the deep link
        string = f"get-{f_msg_id * abs(DB_CHANNEL_ID)}-{s_msg_id * abs(DB_CHANNEL_ID)}"
        encoded_string = await encode(string)
        redirect_link = f"https://t.me/{client.username}?start={encoded_string}"

        # Send the generated link
        await message.reply_text(
            f"Here is your generated link:\n\n{redirect_link}",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔁 Share URL", url=f"https://telegram.me/share/url?url={redirect_link}")]]
            ),
            quote=True
        )
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}", quote=True)

@SecondBot.on_message(filters.private & filters.command('start'))
async def start_secondary(client: Client, message: Message):
    if len(message.command) > 1:
        # Extract the start parameter
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
                await message.reply_text("❌ Invalid parameter!", quote=True)
        except Exception as e:
            await message.reply_text(f"❌ Error decoding parameter: {e}", quote=True)
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
