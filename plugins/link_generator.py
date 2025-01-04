from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from helper_func import encode, decode, get_message_id

# Primary Bot API credentials
API_ID = 22505271  # Main bot's API ID
API_HASH = "c89a94fcfda4bc06524d0903977fc81e"  # Main bot's API Hash
BOT_TOKEN = "7850868885:AAFc5n1OJ3egi7M3mLeJZI0ACyPDprbY_H8"  # Main bot's token

# Secondary Bot API credentials
SECONDARY_API_ID = 22505271  # Replace with second bot's API ID
SECONDARY_API_HASH = "c89a94fcfda4bc06524d0903977fc81e"  # Replace with second bot's API Hash
SECONDARY_BOT_TOKEN = "7850868885:AAFc5n1OJ3egi7M3mLeJZI0ACyPDprbY_H8"  # Replace with second bot's token

# Initialize both bot clients
MainBot = Client("MainBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
SecondBot = Client("SecondBot", api_id=SECONDARY_API_ID, api_hash=SECONDARY_API_HASH, bot_token=SECONDARY_BOT_TOKEN)


@MainBot.on_message(filters.private & filters.command('batch'))
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
                "❌ Error\n\nThis Forwarded Post is not from my DB Channel or this Link is taken from DB Channel",
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
                "❌ Error\n\nThis Forwarded Post is not from my DB Channel or this Link is taken from DB Channel",
                quote=True
            )
            continue

    # Generate deep link
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


@MainBot.on_message(filters.private & filters.command('start'))
async def start(client: Client, message: Message):
    if len(message.command) > 1:
        parameter = message.command[1]
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
    else:
        await message.reply_text(
            "Welcome to the bot! Use /batch to generate links.",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔗 Help", url="https://t.me/JN2FLIX")]]
            )
        )


# Run both bots
if __name__ == "__main__":
    MainBot.start()
    SecondBot.start()
    print("Both bots are running...")
    MainBot.idle()  # Keeps the bots running
    SecondBot.stop()
    MainBot.stop()
