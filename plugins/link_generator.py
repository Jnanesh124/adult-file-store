from pyrogram import Client, filters
from pyrogram.types import Message
from bot import Bot
from config import ADMINS
from helper_func import encode, get_message_id

@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('batch'))
async def batch(client: Client, message: Message):
    # Step 1: Ask for the first message
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
            await first_message.reply("❌ Error\n\nThis Forwarded Post is not from my DB Channel or this Link is not taken from DB Channel", quote=True)
            continue

    # Step 2: Ask for the second message
    while True:
        try:
            second_message = await client.ask(
                text="Forward the Last Message from DB Channel (with Quotes)..\n\nor Send the DB Channel Post Link",
                chat_id=message.from_user.id,
                filters=(filters.forwarded | filters.regex(r"https://t.me/.+"))
            )
        except:
            return
        s_msg_id = await get_message_id(client, second_message)
        if s_msg_id:
            break
        else:
            await second_message.reply("❌ Error\n\nThis Forwarded Post is not from my DB Channel or this Link is not taken from DB Channel", quote=True)
            continue

    # Step 3: Generate the encoded string
    string = f"get-{f_msg_id * abs(client.db_channel.id)}-{s_msg_id * abs(client.db_channel.id)}"
    base64_string = await encode(string)

    # Step 4: Generate the initial Telegram link without `&Getfile=true`
    initial_telegram_link = f"https://t.me/Adult_Video_Storej2_Bot?start={base64_string}"

    # Step 5: Send the first link in plain text
    await second_message.reply_text(
        f"<strong>Your First Link:</strong>\n\n{initial_telegram_link}\n\nClick the link to get either the Blogspot link or the direct file link.",
        quote=True
    )

@Bot.on_message(filters.private & filters.regex(r"^/start"))
async def handle_start(client: Client, message: Message):
    # Extract the base64 data from the link
    data = message.text.split(' ', 1)
    if len(data) == 2:
        base64_string = data[1]

        # Check if the "Getfile=true" flag is in the URL
        getfile = False
        if 'Getfile=true' in message.text:
            getfile = True

        # If the Getfile flag is set, generate the direct file link
        if getfile:
            # You can replace this with the actual link to the direct file
            direct_file_link = f"https://yourfilelink.com/{base64_string}"
            await message.reply_text(f"<strong>Your Direct File Link:</strong>\n\n{direct_file_link}")
        else:
            # Generate the Blogspot link
            blogspot_link = f"https://jn2flix.blogspot.com/2025/01/adultx.html?JN2FLIX={base64_string}"
            await message.reply_text(f"<strong>Your Blogspot Link:</strong>\n\n{blogspot_link}")
