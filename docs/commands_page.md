#Coreuptedbot Commands

There are four levels of user in coreuptedbot: General viewer (everybody who is not the streamer by default), Mods, Admins, and Streamer. All levels beyond General viewer have extra commands. Streamers have all of the permissions and more commands available than admins, Admins have all mod permissions plus additional commands, and Mods have additional commands.

#General Commands usable by everyone

**!commands:** Show this list. This can be configured in irc\_cfg.py, but points to the master github repo by default. You are welcome to copy and put this list on your own website. If you are currently at the master github repository, be aware that if your version of Coreuptedbot is out of date, this list might contain commands your version of the bot does not support. 

**!gamble \<amount to gamble\>:** Roll a random number between 1 and 100. If you roll higher than 60, you win double your points. If you roll higher than 98, you triple your points! Streamers, you can set a minimum amount of points and how often users can gamble in irc\_cfg.py

**!pingbot:** Checks to see if Coreuptedbot is currently in your chat and if it is currently paused or not.

**!points:** \<username\> Show the amount of points you or another viewer have.

**!rank:** \<username\> Show your current ranking (or another user's ranking) in the channel by the number of points you currently have

**!rewards:** Show the list of rewards available. The link to your rewards list can be changed in irc\_cfg.py similar to !commands.

**!top5 !top10:** Show the top 5 or top 10 most loyal viewers by points in the channel.

#Mod and above Commands

**!bonus \<user\> \<points\>:** Give a person a bonus of however many points you choose

**!bonusall \<points\>:** Give all users currently in chat a bonus of however many points you choose

#Admin and above Commands

**!addadmin \<user\>:** Add another user with admin level privileges. Only the stream owner can remove an admin.

**!addmod \<user\>:** Add another user with mod level privileges

**!newstream:** Clears out users who have chatted for the first time so they can get their bonus again

**!setbonus \<user\> \<points\>:** Sets the first chat message bonus to an amount different than the default in irc\_cfg.py

**!pausebot:** Pause the bot. This will stop announcements, stop giving out ambient points for being in chat, and stop giving out bonus points for the first chat message.

**!removemod \<user\>:** Revokes mod privileges from a moderator

**!unpausebot:** Unpauses the bot.

#Streamer commands

Remember that you have all admin and mod privileges as the streamer.

**!removeadmin \<user\>:** Revokes admin priviliges from a user

**!rewardcomplete \<reward id\>:** Say this in chat to take redeemed reward out of your queue. The bot should whisper you the reward id when it is claimed.

**!rewardqueue:** Have the bot whisper you a list of rewards awaiting to be claimed still

**!rewardrefund \<reward id\>:** Remove a reward from your queue and refund the points spent on that reward.
