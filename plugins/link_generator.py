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

    # Generate the file link (which will redirect to the blog link)
    file_link = f"/start={base64_string}&type=file"

    # Send the file link
    await second_message.reply_text(f"<strong>Link:</strong> {file_link}", quote=True)


@Bot.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    # Extract the full command and parameters
    start_command = message.text.strip()
    if len(start_command.split()) > 1:  # Check if there's a parameter
        start_param = start_command.split(" ", 1)[1]  # Extract parameter after /start
    else:
        start_param = None

    if start_param:
        # Check if the parameter contains "&type=file"
        if "&type=file" in start_param:
            # Extract the base64 string (everything before "&type=file")
            base64_string = start_param.split("&type=file")[0]

            # Generate the blog link
            blogspot_link = f"https://jn2flix.blogspot.com/2025/01/adultx.html?JN2FLIX={base64_string}"

            # Send the blog link
            await message.reply_text(
                f"<strong>Redirected to Blog Link:</strong>\n{blogspot_link}", 
                quote=True
            )
            return  # End processing since we've handled this case

    # Default response if no valid parameter or no type=file
    await message.reply_text(
        "Welcome! This is a bot for generating links.",
        quote=True
    )
