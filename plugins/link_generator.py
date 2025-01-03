import subprocess
from pyrogram.types import Message
import os

def extract_inner_metadata(file_path):
    """
    Extract metadata such as file name, year, quality, and language from the inner file structure.
    """
    try:
        # Use mediainfo to extract details
        command = ["mediainfo", "--Output=JSON", file_path]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            metadata = result.stdout
            # Parse metadata JSON (simplified example)
            # You can parse `metadata` JSON to extract more specific details
            file_name = os.path.basename(file_path)
            return {
                "name": file_name,
                "year": "Unknown",  # Add logic to extract year if available
                "quality": "Unknown",  # Add logic to extract quality
                "languages": "Unknown"  # Add logic to extract languages
            }
        else:
            print(f"Error extracting metadata: {result.stderr}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

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
                "❌ Error\n\nthis Forwarded Post is not from my DB Channel or this Link is taken from DB Channel",
                quote=True
            )
            continue

    while True:
        try:
            second_message = await client.ask(
                text="Forward the Last Message from DB Channel (with Quotes)..\n\nor Send the DB Channel Post link",
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
                "❌ Error\n\nthis Forwarded Post is not from my DB Channel or this Link is taken from DB Channel",
                quote=True
            )
            continue

    # Collect metadata for all files in the batch
    metadata_list = []
    for msg_id in range(f_msg_id, s_msg_id + 1):
        msg = await client.get_messages(chat_id=client.db_channel.id, message_ids=msg_id)
        if msg.document:
            # Download only the first part of the file for metadata extraction
            file_path = await client.download_media(msg.document.file_id, block=False)
            metadata = extract_inner_metadata(file_path)
            if metadata:
                metadata_list.append(metadata)
            os.remove(file_path)  # Clean up the downloaded file

    # Merge metadata
    if metadata_list:
        movie_name = metadata_list[0]["name"]
        year = metadata_list[0]["year"]
        quality = metadata_list[0]["quality"]
        languages = merge_languages([meta["languages"] for meta in metadata_list])

        # Generate batch link
        string = f"get-{f_msg_id * abs(client.db_channel.id)}-{s_msg_id * abs(client.db_channel.id)}"
        base64_string = await encode(string)
        link = f"https://t.me/{client.username}?start={base64_string}"

        # Prepare reply
        caption = (
            f"<b>Movie Name:</b> {movie_name}\n"
            f"<b>Year:</b> {year}\n"
            f"<b>Quality:</b> {quality}\n"
            f"<b>Languages:</b> {languages}\n\n"
            f"<b>Batch Link:</b> {link}"
        )
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]])

        # Send reply
        await second_message.reply_text(caption, reply_markup=reply_markup)
    else:
        await message.reply("❌ No valid metadata found in the batch.")
