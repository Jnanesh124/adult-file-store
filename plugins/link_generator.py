from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from helper_func import encode, decode, get_message_id
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# API credentials for the main bot
MAIN_API_ID = 21942125  # Your Main Bot API ID
MAIN_API_HASH = "6d412af77ce89f5bb1ed8971589d61b5"  # Your Main Bot API Hash
MAIN_BOT_TOKEN = "7850868885:AAFc5n1OJ3egi7M3mLeJZI0ACyPDprbY_H8"  # Your Main Bot Token

# API credentials for the secondary bot (if needed)
SECOND_API_ID = 12345678  # Replace with your Secondary Bot API ID
SECOND_API_HASH = "abcdef1234567890abcdef1234567890"  # Replace with your Secondary Bot API Hash
SECOND_BOT_TOKEN = "123456789:ABCDEF1234567890abcdef1234567890"  # Replace with your Secondary Bot Token

# Initialize bot clients
MainBot = Client("MainBot", api_id=MAIN_API_ID, api_hash=MAIN_API_HASH, bot_token=MAIN_BOT_TOKEN)
SecondBot = Client("SecondBot", api_id=SECOND_API_ID, api_hash=SECOND_API_HASH, bot_token=SECOND_BOT_TOKEN)

# Command: /batch
@MainBot.on_message(filters.private & filters.command('batch'))
async def batch(client: Client, message: Message):
    logging.info(f"Batch command triggered by user: {message.from_user.id}")
    
    # Step 1: Get the first message ID
    while True:
        try:
            first_message = await client.ask(
                text="Forward the First Message from DB Channel (with Quotes)..\n\nor Send the DB Channel Post Link",
                chat_id=message.from_user.id,
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60
            )
        except Exception as e:
            await message.reply_text(f"❌ Error: {e}\n\nPlease try again.")
            return
        
        f_msg_id = await get_message_id(client, first_message)
        if f_msg_id:
            break
        else:
            await first_message.reply(
                "❌ Error\n\nThis Forwarded Post is not from my DB Channel or this Link is invalid.",
                quote=True
            )

    # Step 2: Get the last message ID
    while True:
        try:
            second_message = await client.ask(
                text="Forward the Last Message from DB Channel (with Quotes)..\n\nor Send the DB Channel Post link",
                chat_id=message.from_user.id,
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60
            )
        except Exception as e:
            await message.reply_text(f"❌ Error: {e}\n\nPlease try again.")
            return
        
        s_msg_id = await get_message_id(client, second_message)
        if s_msg_id:
            break
        else:
            await second_message.reply(
                "❌ Error\n\nThis Forwarded Post is not from my DB Channel or this Link is invalid.",
                quote=True
            )

    # Generate the deep link
    try:
        string = f"get-{f_msg_id * abs(client.db_channel.id)}-{s_msg_id * abs(client.db_channel.id)}"
        encoded_string = await encode(string)
        redirect_link = f"https://t.me/{client.username}?start={encoded_string}"

        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={redirect_link}')]]
        )
        await second_message.reply_text(
            f"<strong>480P 720P 720PHEVC 1080P 📂\n\n{redirect_link}\n\n"
            "▪️▪️▪️▪️▪️▪️▪️▪️▪️▪️▪️▪️▪️\nJoin Backup channel @JN2FLIX\n▪️▪️▪️▪️▪️▪️▪️▪️▪️▪️▪️▪️▪️</strong>",
            quote=True,
            reply_markup=reply_markup
        )
    except Exception as e:
        await message.reply_text(f"❌ Unexpected Error: {e}")

# Command: /start
@MainBot.on_message(filters.private & filters.command('start'))
async def start(client: Client, message: Message):
    logging.info(f"Start command triggered by user: {message.from_user.id}")
    
    if len(message.command) > 1:
        # Extract the start parameter
        parameter = message.command[1]
        try:
            decoded = await decode(parameter)
        except Exception as e:
            await message.reply_text(f"❌ Invalid parameter: {e}")
            return

        if decoded.startswith("get-"):
            # Redirect to the first HTML page with the parameter
            html_link = f"https://jn2flix.blogspot.com/2025/01/j1.html?JN2FLIX={parameter}"
            await message.reply_text(
                "Click the button below to proceed to the link:",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("📂 Open Page", url=html_link)]]
                )
            )
        else:
            await message.reply_text("❌ Invalid parameter!")
    else:
        await message.reply_text(
            "Welcome to the bot! Use /batch to generate links.",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔗 Help", url="https://t.me/JN2FLIX")]]
            )
        )

# Run both bots
if __name__ == "__main__":
    try:
        MainBot.start()
        SecondBot.start()
        logging.info("Both bots started successfully.")
        MainBot.idle()
    except KeyboardInterrupt:
        logging.info("Bot stopped.")
