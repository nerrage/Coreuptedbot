#irc_cfg.py
#This configures IRC connection info
#Replace all <BRACKETED INFO> with your own info
#Use only lowercase letters for usernames 
#e.g Coreupted would use CHAN = "#coreupted"
HOST = "irc.chat.twitch.tv"
PORT = 6667
NICK = "<YOUR BOT'S USERNAME>" #lowercase only
PASS = "oauth:<YOUR BOT ACCOUNT'S API KEY>" #Don't have oauth:ouath: here
CHAN = "#<YOUR CHANNEL>" #Lowercase only, leave # in front
POINT_NAME = "points" #Use a plural noun for announcements to make sense
TICK_RATE = 60 #How often to give viewers points, in seconds
POINTS_PER_TICK = 10
FIRST_CHAT_BONUS = 1 #Set to 0 to turn off
FIRST_CHAT_BONUS_POINTS = 1500
ANNOUNCEMENT_RATE = 300 #How often to make a scheduled announcement, in seconds
#If you do not want announcements, don't make an announcements.txt file
GAMBLE_RATE = 30 #How often a user can gamble, in seconds
MINIMUM_GAMBLE = 500 #Amount of points that must be gambled minimally
