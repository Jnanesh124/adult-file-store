import asyncio
import difflib
import re
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, UserNotParticipant, RPCError
from bot import Bot  # Bot instance
from config import ADMINS  # Admins
from helper_func import encode  # Encoding for file links

# Auto-delete message duration
AUTO_DELETE_DURATION = 60  

# File Channel Info
FILE_CHANNEL_ID = -1002397642850  # Your private file channel ID
JOIN_LINK = "https://t.me/+QlhpE2sIYgliYWE1"  # File channel invite link
STRING_SESSION = "BQHI4PQAMgetbNq7R28-73gRPH7-mK82KFy5Fh50iNYKc4-HXpFVl5uS6MWRefS0Q-q6AlmJXpQP1qGdfvECTlsDaVoGpA0Io5v_1sf2uh0kqBhwBeRW8AFAIOnwpHoB_nQNbUVcW6UlW7tx6Pi5OzK4Wr2pkYIzawV433XBlnRd4dZxcR2eMuvgH_Ib5YaWt1h3gOAi9UksVrd4FFnSg6g6J-e7HSTojN3lGKigDaXpU3yNtIOznhmqalZVdhfbvCzLYur4DWD_zemwnpIlFTe3w5_efS5igODXuHzv2oRJMafWuDcn_frr4sw-Yhk7btj2IA3hhj31Q9_c7b4C-XlJEVfAeQAAAABkI-HqAA"

# Pyrogram Client using String Session for file search
file_client = Client("FileSearchBot", session_string=STRING_SESSION)

# Stopwords to clean user input
STOPWORDS = {
    "movie", "dubbed", "kannada", "hindi", "english", "telugu", "malayalam", "tamil",
    "download", "full", "hd", "1080p", "720p", "480p", "bluray", "4k", "hdrip", "brrip",
    "web-dl", "season", "episode", "s01", "s02", "s03", "part"
}

async def check_and_join_channel():
    """
    Check if the string session user is a member of the file channel.
    If not, join using the invite link.
    Also, check if the bot is an admin in the file channel.
    """
    async with file_client:
        try:
            member = await file_client.get_chat_member(FILE_CHANNEL_ID, "me")
            print(f"✅ String session user is already a member of {FILE_CHANNEL_ID}")
        except UserNotParticipant:
            print("⚠️ String session user is not a member, attempting to join...")
            try:
                await file_client.join_chat(JOIN_LINK)
                print("✅ Successfully joined the file channel!")
            except Exception as e:
                print(f"❌ Failed to join file channel: {e}")

        # Check if bot is admin
        bot_member = await file_client.get_chat_member(FILE_CHANNEL_ID, (await file_client.get_me()).id)
        if bot_member.status not in ("administrator", "creator"):
            print("❌ Bot is not an admin in the file channel! Please make the bot an admin.")
        else:
            print("✅ Bot is an admin in the file channel.")

async def search_in_file_channel(movie_name):
    """
    Search for a movie file in the file channel using Pyrogram String Session.
    """
    async with file_client:
        try:
            async for msg in file_client.search_messages(chat_id=FILE_CHANNEL_ID, query=movie_name):
                # Generate the direct file link
                converted_id = msg.id * abs(FILE_CHANNEL_ID)
                string = f"get-{converted_id}"
                base64_string = await encode(string)
                return f"https://t.me/{Bot.username}?start={base64_string}"

        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception as e:
            print(f"❌ Error searching file channel: {e}")

    return None

def clean_movie_name(user_input):
    """
    Extract the correct movie name by removing unwanted words and stopwords.
    """
    words = re.findall(r'\b\w+\b', user_input.lower())  # Extract words
    cleaned_words = [word for word in words if word not in STOPWORDS]  # Remove stopwords
    return " ".join(cleaned_words)  # Return cleaned name

def fuzzy_match(movie_name):
    """
    Use fuzzy matching to find the closest movie name.
    """
    matches = difflib.get_close_matches(movie_name, [], n=1, cutoff=0.7)
    return matches[0] if matches else movie_name  # Return best match or original

@Bot.on_message(filters.text & filters.group & filters.incoming & ~filters.command(["verify", "connect", "id"]))
async def search_movie(bot, message):
    query = message.text.strip()

    # Extract and clean movie name
    extracted_name = clean_movie_name(query)
    fuzzy_name = fuzzy_match(extracted_name)  # Optional fuzzy correction

    # Display "Searching..." message
    searching_msg = await message.reply_text(f"🔍 **Searching for:** {fuzzy_name}", disable_web_page_preview=True)

    # Search only in the file channel
    file_link = await search_in_file_channel(fuzzy_name)

    # Delete "Searching..." message
    await searching_msg.delete()

    # Construct response message
    response = f"🎬 **Results for:** `{fuzzy_name}`\n\n"
    if file_link:
        response += f"📥 **Direct File:** [Click Here]({file_link})"
    else:
        response += "❌ No results found."

    # Send results message
    msg = await message.reply_text(response, disable_web_page_preview=True)

    # Auto-delete message after duration
    await asyncio.sleep(AUTO_DELETE_DURATION)
    await msg.delete()

@Bot.on_message(filters.private & filters.user(ADMINS) & ~filters.command(['start', 'users', 'broadcast', 'batch', 'genlink', 'stats']))
async def channel_post(client: Client, message):
    """
    Handle file uploads and generate direct download links.
    """
    reply_text = await message.reply_text("Please Wait...", quote=True)

    try:
        post_message = await message.copy(chat_id=client.db_channel.id, disable_notification=True)

        # Generate file link
        converted_id = post_message.id * abs(client.db_channel.id)
        string = f"get-{converted_id}"
        base64_string = await encode(string)
        link = f"https://t.me/{client.username}?start={base64_string}"

        # Send the link
        await message.reply_text(f"📥 **Direct File Link:** [Click Here]({link})", disable_web_page_preview=True)

        await reply_text.delete()
        return

    except Exception as e:
        print(e)
        await reply_text.edit_text("Something went wrong!")
        return

@Bot.on_message(filters.channel & filters.incoming & filters.chat(FILE_CHANNEL_ID))
async def new_post(client: Client, message):
    """
    Automatically add a share button to new file uploads.
    """
    converted_id = message.id * abs(client.db_channel.id)
    string = f"get-{converted_id}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]])

    try:
        await message.edit_reply_markup(reply_markup)
    except FloodWait as e:
        await asyncio.sleep(e.value)
    except Exception:
        pass

# Run auto-join check on startup
asyncio.run(check_and_join_channel())
