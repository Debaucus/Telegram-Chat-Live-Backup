# Telegram Chat Live Backup

Backup Telegram chats live as messages come in. Huge credit goes to [Telethon](https://github.com/LonamiWebs/Telethon) for the package that makes this whole project possible.

Note from Telethon Github.

Important

If you have code using Telethon before its 1.0 version, you must read Compatibility and Convenience to learn how to migrate. As with any third-party library for Telegram, be careful not to break [Telegram's ToS](https://core.telegram.org/api/terms) or [Telegram can ban the account.](https://docs.telethon.dev/en/stable/quick-references/faq.html#my-account-was-deleted-limited-when-using-the-library)

## What is this for?

Telegram channels have both the ability to delete after X amount of time, some chats are heavily monitored. This tool allows a live download of any chat you are already in (more on that later). Videos and Photos are also downloaded.

The output is a HTML file which shows the messages in a Telegram format.

### Supported so far:

- [x] Chat messages
- [x] Reply messages
- [x] Video messages
- [x] Photo messages
- [] Stickers (downloads but not displayed)

# How to use

- Create a venv.
  `python -m venv venv`
- Activate the virtual envrioment.
  `.\venv\Scripts\Activate`
- Install requirements.
  `pip install -r requirements.txt`
- Copy `example.env` to `.env` and fill in details.

# .env explained.

`API_ID` and `API_HASH` are used by Telethon to use your account. To use this script you will need to go to [My Telegram](https://my.telegram.org), under API development you will need to create an application that gives you these values.

`SESSION_NAME` gives the session file name something to use. Any string is acceptable.

`TARGET_CHANNELS` is a list of channels/groups, that you are in, which the are monitored for messages. Being in the chat _should_ reduce ban risk as you are in the chat reading messages much like any other client.

````API_ID=0
API_HASH=""
SESSION_NAME="" # Any name.
TARGET_CHANNELS="example_1,example_2" # Channels/Groups you wish to backup.```
````
