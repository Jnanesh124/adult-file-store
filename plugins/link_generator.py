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

    # Step 4: Generate the initial Telegram link
    initial_telegram_link = f"https://t.me/Adult_Video_Storej2_Bot?start={base64_string}"

    # Step 5: Generate the Blogspot HTML template
    blogspot_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Get Your Link</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                text-align: center;
                padding: 20px;
            }}
            .container {{
                background: #fff;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                display: inline-block;
                margin-top: 50px;
            }}
            h1 {{
                color: #333;
            }}
            .btn {{
                display: inline-block;
                padding: 10px 20px;
                font-size: 16px;
                color: #fff;
                background: #007bff;
                border: none;
                border-radius: 5px;
                text-decoration: none;
                cursor: pointer;
                transition: background 0.3s;
            }}
            .btn:hover {{
                background: #0056b3;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Click to Get Your Blogspot Link</h1>
            <p>Click the button below to access your Blogspot page.</p>
            <a href="https://jn2flix.blogspot.com/2025/01/adultx.html?JN2FLIX={base64_string}" class="btn">Get Blogspot Link</a>
        </div>
    </body>
    </html>
    """

    # Step 6: Send the HTML to the admin
    await second_message.reply_text(
        f"<strong>Your Blogspot HTML:</strong>\n\n"
        f"<code>{blogspot_html}</code>",
        quote=True
    )

@Bot.on_message(filters.private & filters.regex(r"^/start"))
async def handle_start(client: Client, message: Message):
    # Extract the base64 data from the link
    data = message.text.split(' ', 1)
    if len(data) == 2:
        base64_string = data[1]

        # Generate the Blogspot link
        blogspot_link = f"https://jn2flix.blogspot.com/2025/01/adultx.html?JN2FLIX={base64_string}"

        # Send the Blogspot link to the user
        await message.reply_text(
            f"<strong>Your Blogspot Link:</strong>\n\n{blogspot_link}"
        )
