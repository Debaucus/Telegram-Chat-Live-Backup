import os
from telethon import TelegramClient, events

import logging
logging.basicConfig(level=logging.ERROR)

from dotenv import load_dotenv
load_dotenv()

api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
session_name = os.getenv("SESSION_NAME")
target_channels = os.getenv("TARGET_CHANNELS").split(',')

client = TelegramClient(session_name, api_id, api_hash, retry_delay=2, connection_retries=5)

def get_export_dir(channel):
    export_dir = os.path.join('export', channel)
    media_dir = os.path.join(export_dir, 'media')
    os.makedirs(media_dir, exist_ok=True)
    return export_dir, media_dir

full_export_snippets = []

def load_existing_messages(export_dir):
    """Load previously exported messages by manually stripping the header and footer."""
    messages = []
    file_path = os.path.join(export_dir, "full_export.html")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            # Remove everything before the messages begin
            start_marker = "<h1>Full Chat Export</h1>"
            end_marker = "</body>"
            start_index = content.find(start_marker)
            end_index = content.rfind(end_marker)
            if start_index != -1 and end_index != -1:
                messages_block = content[start_index + len(start_marker):end_index]
                # Now split by the message container marker
                parts = messages_block.split('<div class="message-container">')
                for part in parts:
                    part = part.strip()
                    if part:
                        messages.append('<div class="message-container">' + part)
    return messages

def generate_message_snippet(export_dir, message_text, sender, date, message_id, media_filename=None, reply_snippet=""):
    channel_name = export_dir.replace("export\\", "", 1)
    snippet = f"""<div class="message-container">
        <div class="header">
            <span class="sender">{sender}</span>
            <span class="date">{date}</span>
            <span class="link"><a href="https://t.me/{channel_name}/{message_id}">https://t.me/{channel_name}/{message_id}</a></span>
        </div>
        {reply_snippet}
        <div class="content">
            <p>{message_text}</p>"""

    if media_filename:
        snippet += f"""<div class="media">
                <img src="media/{media_filename}" alt="Media content">
            </div>"""

    snippet += "</div></div>"
    return snippet.strip()


def update_full_export_file(export_dir, full_export_snippets):
    header = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Full Chat Export</title>
    <style>
       body {
            font-family: 'Arial', sans-serif;
            background-color: #e5ddd5;
            padding: 20px;
            color: #000;
        }
        p { margin: 0px; }
        .message-container {
            background-color: #fff;
            border-radius: 10px;
            padding: 10px 15px;
            margin-bottom: 15px;
            width: fit-content;
            max-width: 60%;
            box-shadow: 0 1px 1px rgba(0,0,0,0.2);
        }
        .header {
            font-size: 0.85em;
            color: #888;
            margin-bottom: 5px;
            display: flex;
            justify-content: space-between;
        }
        .sender { font-weight: bold; color: #075E54; }
        .date { font-size: 0.8em; }
        .link a { text-decoration: none; color: #34B7F1; }
        .content { font-size: 1em; line-height: 1.4; }
        .media img {
            max-width: 100%;
            height: auto;
            border-radius: 5px;
            margin-top: 10px;
        }
        .reply {
            background-color: #f0f0f0;
            padding: 8px;
            border-left: 3px solid #34B7F1;
            margin-bottom: 8px;
            border-radius: 5px;
        }
        .reply-header {
            font-weight: bold;
            font-size: 0.85em;
            color: #075E54;
        }
        .reply-content {
            font-size: 0.9em;
            color: #333;
        }
    </style>
</head>
<body>
<h1>Full Chat Export</h1>
"""
    footer = """
</body>
</html>"""
    content = "".join(full_export_snippets)
    full_html = header + content + footer
    with open(os.path.join(export_dir, "full_export.html"), "w", encoding="utf-8") as f:
        f.write(full_html)

def main():
    client.start()
    print("Client started. Monitoring channel for new messages...")
    print("Channel Monitor on for:", target_channels)

    
    @client.on(events.NewMessage(chats=target_channels))
    async def handler(event):
        try:
            channel = event.chat.username if event.chat.username else str(event.chat.id)
            export_dir, media_dir = get_export_dir(channel)
            full_export_snippets = load_existing_messages(export_dir)

            message = event.message
            sender_entity = await event.get_sender()
            sender = sender_entity.username or sender_entity.first_name or sender_entity.id
            date = message.date.strftime("%Y-%m-%d %H:%M:%S")
            message_text = message.raw_text or "[Non-text message]"
            media_filename = None
            message_id = message.id

            # Fetch reply message if exists
            reply_snippet = ""
            if message.reply_to:
                reply_message = await message.get_reply_message()
                if reply_message:
                    reply_sender_entity = await reply_message.get_sender()
                    reply_sender = reply_sender_entity.username or reply_sender_entity.first_name or reply_sender_entity.id
                    reply_text = reply_message.raw_text or "[Non-text message]"
                    reply_snippet = f"""<div class="reply">
                        <div class="reply-header">
                            <span class="reply-sender">{reply_sender}</span>
                        </div>
                        <div class="reply-content">
                            <p>{reply_text}</p>
                        </div>
                    </div>"""

            if message.media:
                media_path = await event.download_media(file=media_dir)
                if media_path:
                    media_filename = os.path.basename(media_path)

            print("[", date, "] - ", channel, " - ", message_text)

            snippet = generate_message_snippet(export_dir, message_text, sender, date, message_id, media_filename, reply_snippet)
            full_export_snippets.append(snippet)
            update_full_export_file(export_dir, full_export_snippets)

        except Exception as e:
            print(f"Error processing message: {e}")

    client.run_until_disconnected()

if __name__ == "__main__":
    main()
