# bot.py
import socket
import irc_cfg
import time
import re
import datetime
import os
import core_functions

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


def resetpoints(sock, user):
    #Activates after a designated user says !newstream
    #This empties the list of people who chatted
    if user == 'nerrage' or user == 'coreupted':
        os.rename("chatted_today", "chatted_today{}".format(st))
        chat(sock, "Chat bonus has been reset for all! Enjoy your chatting Kappa")
        print("points reset")

def purgepresetcustompoints(user):
    #Deletes any lines with that user's username
    pointsfile = open("custompoints.csv", "r+")
    pointslines = pointsfile.readlines()
    pointsfile.seek(0)
    for line in pointslines:
        points_split = line.split()
        points_username = points_split[0]
        print(points_username+" is username")
        if user != points_username:
            pointsfile.write(line) #keep unaltered user lines
    pointsfile.truncate()
    pointsfile.close()

def setcustompoints(sock, user, user_to_set, points):
    if user == 'nerrage' or user == 'coreupted':
        if RepresentsInt(points): 
            purgepresetcustompoints(user_to_set)
            print("writing points")
            pointsfile = open("custompoints.csv", "a+")
            pointsfile.write(user_to_set+" "+points+"\n")
            chat(sock, "Point bonus set to {} for user {}".format(points,user_to_set))
            print("points for {} set to {}".format(user_to_set,points))
        else:
            chat(sock, "MrDestructoid Are you trying to kill me? {} isn't a number".format(points))

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
    if user == 'nerrage' or user == 'coreupted':
        global paused
        paused = True
        chat(sock, "Coreuptedbot is paused. Chat points paused. !coreuptedbot unpause to restart")
        print("Pause initiated")

def unpausebot(sock, user):
    if user == 'nerrage' or user == 'coreupted':
        global paused
        paused = False
        chat(sock, "Coreuptedbot is unpaused. Come and get your points MrDestructoid")
        print("Bot unpaused")

def commandlist(username,message):
#todo: smaller functions
    if message == "PING :tmi.twitch.tv":
        #twitch pings us to check connection
        s.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
        print("Pong sent") #logging
    if re.match("!coreuptedbot reset", chatmessage[1]):
        resetpoints(s, username)
    if re.match("!coreuptedbot setbonus", message):
        #!coreuptedbot setpoints nerrage 2000
        try:
            split_string = message.split()
            setpoint_name = split_string[2]
            setpoint_points = split_string[3]
            setcustompoints(s, username, setpoint_name, setpoint_points)
        except:
            chat(s, "!coreuptedbot setbonus <user> <points>")
    if re.match("!coreuptedbot ping", message):
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
        if paused == False:
            #only give points when not paused
            givepoints(s, username)
    print("Timestamp: {}, announcetime {} ".format(float(time.time()), announcetime))
    if (announcetime <= float(time.time()) - 300 and paused == False): #5 mins since last announcement
       announcements(s)
       announcetime = float(time.time()) 
    time.sleep(2)
