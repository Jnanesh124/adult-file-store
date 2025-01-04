from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot import Bot
from config import ADMINS
from helper_func import encode, decode, get_message_id

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
    deep_link = f"https://t.me/{client.username}?start={encoded_string}"

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
        # Extract the start parameter
        parameter = message.command[1]
        decoded = await decode(parameter)

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
