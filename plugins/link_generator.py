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
            await first_message.reply(
                "❌ Error\n\nThis forwarded post is not from my DB Channel or this link is invalid.", quote=True)
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
            await second_message.reply(
                "❌ Error\n\nThis forwarded post is not from my DB Channel or this link is invalid.", quote=True)
            continue

    # Generate the encoded string
    string = f"get-{f_msg_id * abs(client.db_channel.id)}-{s_msg_id * abs(client.db_channel.id)}"
    base64_string = await encode(string)

    # Generate links
    blogspot_link = f"https://jn2flix.blogspot.com/2025/01/adultx.html?JN2FLIX={base64_string}&type=blog"
    direct_file_link = f"https://t.me/Adult_Video_Storej2_Bot?start={base64_string}&type=file"

    # Send the blog link instead of the direct file link
    await second_message.reply_text(
        f"<strong>Blog Link:</strong> {blogspot_link}\n"
        f"<strong>Direct File Link (for reference):</strong> {direct_file_link}",
        quote=True
    )


@Bot.on_message(filters.regex(r"https://t.me/Adult_Video_Storej2_Bot\?start=(.+)&type=file$"))
async def handle_file_link_as_blog(client: Client, message: Message):
    # Extract the base64 part of the URL
    base64_string = message.matches[0].group(1)

    # Generate the corresponding blog link
    blogspot_link = f"https://jn2flix.blogspot.com/2025/01/adultx.html?JN2FLIX={base64_string}&type=blog"

    # Send the blog link instead of the file
    await message.reply_text(f"<strong>{blogspot_link}</strong>", quote=True)


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
            await channel_message.reply(
                "❌ Error\n\nThis forwarded post is not from my DB Channel or this link is invalid.", quote=True)
            continue

    # Generate the encoded string
    base64_string = await encode(f"get-{msg_id * abs(client.db_channel.id)}")

    # Generate blog and file links
    blogspot_link = f"https://jn2flix.blogspot.com/2025/01/adultx.html?JN2FLIX={base64_string}&type=blog"
    direct_file_link = f"https://t.me/Adult_Video_Storej2_Bot?start={base64_string}&type=file"

    # Send the blog link
    await channel_message.reply_text(
        f"<strong>Blog Link:</strong> {blogspot_link}\n"
        f"<strong>Direct File Link (for reference):</strong> {direct_file_link}",
        quote=True
    )
