from pyrogram import Client, filters
from pyrogram.types import Message
from bot import Bot
from config import ADMINS
from helper_func import encode, get_message_id

@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('batch'))
async def batch(client: Client, message: Message):
    while True:
        try:
            first_message = await client.ask(
                text="Forward the First Message from DB Channel (with Quotes)..\n\nor Send the DB Channel Post Link",
                chat_id=message.from_user.id,
                filters=(filters.forwarded | filters.regex(r"https://t.me/.+"))
            )
        except:
            return
        f_msg_id = await get_message_id(client, first_message)
        if f_msg_id:
            break
        else:
            await first_message.reply("❌ Error\n\nthis Forwarded Post is not from my DB Channel or this Link is taken from DB Channel", quote=True)
            continue

    while True:
        try:
            second_message = await client.ask(
                text="Forward the Last Message from DB Channel (with Quotes)..\nor Send the DB Channel Post link",
                chat_id=message.from_user.id,
                filters=(filters.forwarded | filters.regex(r"https://t.me/.+"))
            )
        except:
            return
        s_msg_id = await get_message_id(client, second_message)
        if s_msg_id:
            break
        else:
            await second_message.reply("❌ Error\n\nthis Forwarded Post is not from my DB Channel or this Link is taken from DB Channel", quote=True)
            continue

    string = f"get-{f_msg_id * abs(client.db_channel.id)}-{s_msg_id * abs(client.db_channel.id)}"
    base64_string = await encode(string)
    
    # Generate the initial Telegram link
    initial_telegram_link = f"https://t.me/Adult_Video_Storej2_Bot?JN2FLIX={base64_string}777"
    
    # Generate the blogspot link
    blogspot_link = f"https://jn2flix.blogspot.com/2025/01/adultx.html?JN2FLIX={base64_string}777"
    
    # Generate the direct file link
    direct_file_link = f"https://t.me/Adult_Video_Storej2_Bot?start={base64_string}"

    # Send the initial Telegram link in text format
    await second_message.reply_text(f"<strong>\n\n{initial_telegram_link}\n\n</strong>", quote=True)

    @Bot.on_message(filters.regex(rf"https://t.me/Adult_Video_Storej2_Bot\?JN2FLIX={base64_string}777"))
    async def handle_blogspot(client: Client, message: Message):
        await message.reply_text(f"<strong>\n\n{blogspot_link}\n\n</strong>")

    @Bot.on_message(filters.regex(rf"https://t.me/Adult_Video_Storej2_Bot\?JN2FLIX={base64_string}(?!777)"))
    async def handle_direct_file(client: Client, message: Message):
        await message.reply_text(f"<strong>\n\n{direct_file_link}\n\n</strong>")

@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('genlink'))
async def link_generator(client: Client, message: Message):
    while True:
        try:
            channel_message = await client.ask(
                text="Forward Message from the DB Channel (with Quotes)..\nor Send the DB Channel Post link",
                chat_id=message.from_user.id,
                filters=(filters.forwarded | filters.regex(r"https://t.me/.+"))
            )
        except:
            return
        msg_id = await get_message_id(client, channel_message)
        if msg_id:
            break
        else:
            await channel_message.reply("❌ Error\n\nthis Forwarded Post is not from my DB Channel or this Link is not taken from DB Channel", quote=True)
            continue

    base64_string = await encode(f"get-{msg_id * abs(client.db_channel.id)}")
    link = f"https://t.me/Adult_Video_Storej2_Bot?JN2FLIX={base64_string}"
    await channel_message.reply_text(f"<strong>\n\n{link}\n\n</strong>", quote=True)
