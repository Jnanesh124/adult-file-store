from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from helper_func import encode, decode, get_message_id

# Configuration for the main bot
MAIN_API_ID = 21942125
MAIN_API_HASH = "6d412af77ce89f5bb1ed8971589d61b5"
MAIN_BOT_TOKEN = "7850868885:AAFc5n1OJ3egi7M3mLeJZI0ACyPDprbY_H8"

# Configuration for the secondary bot (optional)
SECOND_API_ID = 12345678
SECOND_API_HASH = "abcdef1234567890abcdef1234567890"
SECOND_BOT_TOKEN = "123456789:ABCDEF1234567890abcdef1234567890"

# Initialize the main bot
MainBot = Client("MainBot", api_id=MAIN_API_ID, api_hash=MAIN_API_HASH, bot_token=MAIN_BOT_TOKEN)

# Command: /batch
@MainBot.on_message(filters.private & filters.command('batch'))
async def batch(client: Client, message: Message):
    # Step 1: Ask for the first message
    while True:
        try:
            first_message = await client.ask(
                chat_id=message.from_user.id,
                text="Please forward the first message from your DB Channel or send the channel post link.",
                filters=(filters.forwarded | filters.text),
                timeout=60
            )
            first_msg_id = await get_message_id(client, first_message)
            if first_msg_id:
                break
            else:
                await message.reply("❌ Invalid message. Please try again.")
        except Exception as e:
            await message.reply(f"❌ Error: {e}")
            return

    # Step 2: Ask for the last message
    while True:
        try:
            second_message = await client.ask(
                chat_id=message.from_user.id,
                text="Please forward the last message from your DB Channel or send the channel post link.",
                filters=(filters.forwarded | filters.text),
                timeout=60
            )
            last_msg_id = await get_message_id(client, second_message)
            if last_msg_id:
                break
            else:
                await message.reply("❌ Invalid message. Please try again.")
        except Exception as e:
            await message.reply(f"❌ Error: {e}")
            return

    # Generate a unique link
    try:
        db_channel_id = -1002075726565  # Replace with your actual channel ID if not dynamic
        string = f"get-{first_msg_id * abs(db_channel_id)}-{last_msg_id * abs(db_channel_id)}"
        encoded_string = await encode(string)
        redirect_link = f"https://t.me/{client.username}?start={encoded_string}"

        # Send the link with a reply button
        await message.reply_text(
            f"Here is your generated link:\n\n{redirect_link}",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔁 Share URL", url=f"https://telegram.me/share/url?url={redirect_link}")]]
            )
        )
    except Exception as e:
        await message.reply(f"❌ Unexpected Error: {e}")

# Command: /start
@MainBot.on_message(filters.private & filters.command('start'))
async def start(client: Client, message: Message):
    if len(message.command) > 1:
        parameter = message.command[1]
        try:
            decoded = await decode(parameter)
            if decoded.startswith("get-"):
                await message.reply_text(
                    "Click the button below to proceed:",
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("📂 Open Link", url=f"https://example.com/{parameter}")]]
                    )
                )
            else:
                await message.reply("❌ Invalid start parameter.")
        except Exception as e:
            await message.reply(f"❌ Error decoding parameter: {e}")
    else:
        await message.reply("Welcome! Use /batch to generate links.")

# Run the bot
if __name__ == "__main__":
    MainBot.run()
