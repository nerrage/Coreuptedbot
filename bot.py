# bot.py
import socket
import irc_cfg
import time
import re
import datetime
import os
import core_functions
import sqlite3

# initial connection to irc

s = socket.socket()
s.connect((irc_cfg.HOST, irc_cfg.PORT))
s.send("PASS {}\r\n".format(irc_cfg.PASS).encode("utf-8"))
s.send("NICK {}\r\n".format(irc_cfg.NICK).encode("utf-8"))
s.send("JOIN {}\r\n".format(irc_cfg.CHAN).encode("utf-8"))
#s.send("PRIVMSG {} : coreuptedbot is online and giving points MrDestructoid\r\n".format(irc_cfg.CHAN))
time.sleep(1)
print(s.recv(1024).decode("utf-8")) #Print inital irc connection
#Stops bot from giving points to itself or a non-existent tmi user

#db setup
db_conn = sqlite3.connect('bot.db')
conn_cursor = db_conn.cursor()

#global variables
paused = False
announcecount = 0

#time variables for timestamps

ts = time.time()
st = datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d_%H%M%S')
announcetime = ts #static storage of timestamp

#functions

def chat(sock, msg):
    #send as a message
    sock.send("PRIVMSG {} :{}\r\n".format(irc_cfg.CHAN, msg))

def ban(sock, user):
    #drops the banhammer
    chat(sock, ".ban {}".format(user))

def shorttimeout(sock, user, secs=120):
    #gives twitch timeout for secs
    chat(sock, ".timeout {}".format(user, secs))


def resetbonuspoints(sock, admin_name):
    #Activates after a designated user says !newstream
    #This empties the list of people who chatted
    if core_functions.user_exists(admin_name, 'admins'):
        chat(sock, "Chat bonus has been reset for all! Enjoy your chatting Kappa")
        conn_cursor.execute("DELETE FROM chatted_today")
        db_conn.commit()
    else:
        chat(sock, "You are not authorized to reset the chat")

def processchat(chatlist):
    #This makes every message in the format of
    #[['username1','message1'], ['username2','message2']]
    #icky regex ahead
    trimmedchat = []
    chatcounter = 0
    for rawresponse in chatlist:
        name = re.search(r"\w+", rawresponse).group(0) 
        message = re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :").sub("", rawresponse)
        trimmedchat.append([name, message])
    return trimmedchat

def pausebot(sock, user):
    if core_functions.user_exists(admin_name, admins):
        global paused
        paused = True
        chat(sock, "Coreuptedbot is paused. Chat points paused. !coreuptedbot unpause to restart")

def unpausebot(sock, user):
    if core_functions.user_exists(admin_name, admins):
        global paused
        paused = False
        chat(sock, "Coreuptedbot is unpaused. Come and get your points MrDestructoid")

def commandlist(username,message):
#todo: smaller functions
    if message == "PING :tmi.twitch.tv":
        #twitch pings us to check connection
        s.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
        print("Pong sent") #logging
    if re.match("!newstream", chatmessage[1]):
        resetbonuspoints(s, username)
    if re.match("!setbonus", message):
        #!coreuptedbot setpoints nerrage 2000
        try:
            if core_functions.user_exists(admin_name, admins):
                split_string = message.split()
                setpoint_name = split_string[2]
                setpoint_points = split_string[3]
                core_functions.setchatbonus(setpoint_name, setpoint_points)
                chat(s, "Chat bonus for {} set to {}".format(setpoint_name, setpoint_points))
            else:
                chat(s, "You are not authorized to set bonus points")
        except:
            chat(s, "!setbonus <user> <points>")
    if re.match("!pingbot", message):
        if paused:
            chat(s, "Coreuptedbot is PAUSED MrDestructoid")
        else:
            chat(s, "Coreuptedbot is ONLINE MrDestructoid")
    if re.match("!coreuptedbot pause", message):
        pausebot(s,username)
    if re.match("!coreuptedbot unpause", message):
        unpausebot(s,username)

def announcements(sock):
    global announcecount
    print("making announcement!")
    announcelist = ["Follow coreupted @ https://facebook.com/Coreupted/ (gaming) https://facebook.com/actoralexblackwell/ (acting) https://twitter.com/_alexblackwell_ https://instagram.com/always_acting_alex https://www.youtube.com/channel/UCcy2uV-fhgUPfHGfdybHLrQ", "Check out my new coaching website at https://coreuptedgaming.com", "You get 1500 bonus points for your first message in chat each stream! Be sure to follow to never miss bonus points and also get 1500 more for following!", "Check me out on GamerSensei: https://www.gamersensei.com/senseis/coreupted Get $5 OFF your first session with Coupon code 'Coreupted'!"]
    chat(sock, announcelist[announcecount])
    announcecount += 1
    announcecount %= 4

#main bot loop

while True:
    try:
        response = s.recv(1024).decode("utf-8")
        print(response) #logging
    except:
        continue
    response_list = response.splitlines()
    trimmed_responses = processchat(response_list)
    print(trimmed_responses) #logging
    #format [['username1', 'chat message1'], ['user2','chat2]...]
    for chatmessage in trimmed_responses:
	username = chatmessage[0]
        message = chatmessage[1]
        commandlist(username, message)
    print("Timestamp: {}, announcetime {} ".format(float(time.time()), announcetime))
    if (announcetime <= float(time.time()) - 300 and paused == False): #5 mins since last announcement
       announcements(s)
       announcetime = float(time.time()) 
    time.sleep(2)
