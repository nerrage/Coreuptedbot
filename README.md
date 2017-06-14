# Coreuptedbot: Open Source Revlo Replacement

Coreuptedbot is a simple python program that works with SQLite to create a loyalty bot for Twitch Streamers

### Features:

* Points given out for first time chatters
* Reward Redemption
* Gives points to viewers
* The commands from Revlo that you know and love e.g. "!bonus", "!gamble", etc

## Caution: You are hosting all point values on your computer. Make a backup of the database from time to time.

After you run db\_setup.py, you'll notice that there's a new file created called "bot.db". **This is your database of all point values, mods, etc**. You should make copies of this file and upload it to Google Drive, Dropbox, save to USB stick, etc. **If you lose your copy of bot.db and don't have a backup all of your points will be lost**.

# Getting Started (WIP)

Download this repo.

Ensure you have [Python](https://www.python.org/) running and installed.

Create a bot account on twitch.

Generate a chat token while logged in as your bot: https://www.twitchtools.com/chat-token

Use a text editor like Notepad to add your username, bot's username, and bot's chat token to example\_irc\_cfg.py. Rename this to irc\_cfg.py

Run bot.py in python
