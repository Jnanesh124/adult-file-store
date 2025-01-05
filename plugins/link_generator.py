from pyrogram import Client, filters
from pyrogram.types import Message
from bot import Bot
from helper_func import encode

@Bot.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    # Extract the start parameter from the command
    if len(message.text.split()) > 1:  # Check if there's a parameter
        start_param = message.text.split(" ", 1)[1]  # Extract parameter after /start
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
            return  # Exit after handling this case

    # Default response if no valid parameter or no type=file
    await message.reply_text(
        "Welcome! This is a bot for generating links.",
        quote=True
    )

@Bot.on_message(filters.private & filters.command("genlink"))
async def link_generator(client: Client, message: Message):
    while True:
        try:
            channel_message = await client.ask(
                text="Forward Message from the DB Channel (with Quotes)..\n"
                     "or Send the DB Channel Post link",
                chat_id=message.from_user.id,
                filters=(filters.forwarded | filters.regex(r"https://t.me/.+"))
            )
        except:
            return  # Exit if user doesn't respond

        # Get the message ID or post link details
        msg_id = await get_message_id(client, channel_message)
        if msg_id:
            break
        else:
            await channel_message.reply(
                "❌ Error\n\nThis Forwarded Post is not from my DB Channel "
                "or this Link is not taken from DB Channel",
                quote=True
            )

    # Encode the message ID for the link
    base64_string = await encode(f"get-{msg_id}")
    generated_link = f"https://t.me/Adult_Video_Storej2_Bot?start={base64_string}&type=file"

    # Send the generated link
    await channel_message.reply_text(
        f"<strong>Generated Link:</strong>\n{generated_link}",
        quote=True
    )
print(f"Received start_param: {start_param}")
