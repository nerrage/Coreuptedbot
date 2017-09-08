# bot.py
import socket
import irc_cfg
import time
import re
import datetime
import os
import core_functions
import reward_functions
import sqlite3
from random import randint
from threading import Thread

# initial connection to irc

s = socket.socket()
s.connect((irc_cfg.HOST, irc_cfg.PORT))
s.send("PASS {}\r\n".format(irc_cfg.PASS).encode("utf-8"))
s.send("NICK {}\r\n".format(irc_cfg.NICK).encode("utf-8"))
s.send("JOIN {}\r\n".format(irc_cfg.CHAN).encode("utf-8"))
time.sleep(1)
print(s.recv(1024).decode("utf-8")) #Print inital irc connection
#Stops bot from giving points to itself or a non-existent tmi user

#db setup
db_conn = sqlite3.connect('bot.db', check_same_thread = False)
conn_cursor = db_conn.cursor()

#global variables
paused = False
announcecount = 0
last_chat_list = []

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

def givechatbonus(sock, username):
    #If it is the first time someone chats, give them points
    if core_functions.hasfirstbonus(username):
        bonus_given = core_functions.givefirstbonus(username)
        chat(sock, "Welcome to my chat, {}! You get {} bonus points for your first message of the stream and now have {} points".format(username, bonus_given, core_functions.getpoints(username)))

def processchat(chatlist):
    #This makes every message in the format of
    #[['username1','message1'], ['username2','message2']]
    #icky regex ahead
    trimmedchat = []
    for rawresponse in chatlist:
        name = re.search(r"\w+", rawresponse).group(0) 
        message = re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :").sub("", rawresponse)
        trimmedchat.append([name, message])
    return trimmedchat

def pausebot(sock, user):
    if core_functions.user_exists(user, 'admins'):
        global paused
        paused = True
        chat(sock, "Coreuptedbot is paused. Chat points paused. !unpausebot to restart")

def unpausebot(sock, user):
    if core_functions.user_exists(user, 'admins'):
        global paused
        paused = False
        chat(sock, "Coreuptedbot is unpaused. Come and get your points MrDestructoid")

def gamble(sock, user, points):
    #Clears out eligible gamblers from table
    #Checks if user is eligible to gamble
    #If eligible, insert into table which makes them ineligible
    #Timestamp is automatically appended
    if points < irc_cfg.MINIMUM_GAMBLE:
        chat(sock, "Must gamble at least {} points.".format(irc_cfg.MINIMUM_GAMBLE))
        return
    t2=(user,)
    conn_cursor.execute("DELETE FROM GAMBLERS where timestamp < DATETIME('now', '-%s second')" % irc_cfg.GAMBLE_RATE)
    db_conn.commit()
    if core_functions.user_exists(user, 'gamblers'):
        chat(sock, "You can only gamble once every {} seconds, {}".format(irc_cfg.GAMBLE_RATE, user))
        return
    if core_functions.cantakepoints(user, points) == False:
        chat(sock, "You don't have enough points to gamble that, {}".format(user))
        return
    core_functions.takepoints(user, points) #take their bet
    conn_cursor.execute("INSERT INTO GAMBLERS(username) values(?)", t2)
    db_conn.commit() #mark them as a gambler, timestamp is autmatically applied
    roll = randint(1,100)
    if roll < 60:
        chat(sock, "Rolled {}. {} lost {} points and now has {} points".format(roll,user,points,core_functions.getpoints(user)))
        return
    elif roll < 99:
        core_functions.givepoints(user, 2*points)
        chat(sock, "Rolled {}. {} won {} points and now has {} points".format(roll,user,2*points,core_functions.getpoints(user)))
    else: #99 or 100
        core_functions.givepoints(user, 3*points)
        chat(sock, "Rolled {}. {} won {} points and now has {} points".format(roll,user,3*points,core_functions.getpoints(user)))

def pong(username, message):
    if message == "PING :tmi.twitch.tv":
        #twitch pings us to check connection
        s.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
        print("Pong sent") #logging
        return True
    else:
        return False

def checkreward(first_chat_word):
    #Checks and sees if a !command exists as a reward
    #trim to only the first word
    if first_chat_word in reward_functions.getrewards():
        return True
    else:
        return False
    
 
def commandlist(username,message):
#todo: smaller functions
    first_word = message.split(' ', 1)[0]
    if first_word in reward_functions.getrewards():
    #first word matches a reward
        if reward_functions.canredeemreward(username, first_word):
            try:
              chat_messages = reward_functions.redeemreward(username, first_word, message.split(' ', 1)[1])
              chat(s, chat_messages[0])
              time.sleep(.5)
              chat(s, chat_messages[1])
            except:
                chat(s, reward_functions.rewardinfo(first_word))
        else:
            chat(s, "You don't have enough points to redeem that!")
    if re.match("!newstream", message):
        resetbonuspoints(s, username)
    if message == "!rewards":
        chat(s, "Coreuptedbot rewards list: {}".format(irc_cfg.REWARDS_URL))
    if message == "!commands":
        chat(s, "Coreuptedbot command list: {}".format(irc_cfg.COMMANDS_URL))
    if re.match("!setbonus", message):
        #!setbonus nerrage 2000
        #Sets first time chat bonus
        try:
            if core_functions.user_exists(username, 'admins'):
                split_string = message.split()
                setpoint_name = split_string[1]
                setpoint_points = split_string[2]
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
    if re.match("!pausebot", message):
        pausebot(s,username)
    if re.match("!unpausebot", message):
        unpausebot(s,username)
    if re.match("!rewardqueue", message):
        if username == irc_cfg.CHAN[1:]:
            chat(s, "/w {} REWARD QUEUE STARTS HERE".format(irc_cfg.CHAN[1:]))
            for i in reward_functions.getrewardsqueue():
                whisper_message = i[3]
                cost = i[4]
                reward_id = i[0]
                chat(s, "{} for {} points. The reward id is {}. Say !rewardcomplete {} in chat after the reward has been completed. Say !rewardrefund {} to refund the points for this reward.".format(whisper_message,cost,reward_id,reward_id,reward_id))
                time.sleep(.5)
            chat(s, "/w {} REWARD QUEUE ENDS HERE".format(irc_cfg.CHAN[1:]))
        else:
            chat(s, "Only the channel owner can use this function")
    if re.match("!rewardcomplete", message):
        if username == irc_cfg.CHAN[1:]:
            try:
                split_string = message.split()
                reward_id = int(split_string[1])
                if reward_functions.completeredemption(reward_id):
                    chat(s, "/w {} reward id {} complete. Removing from queue".format(irc_cfg.CHAN[1:], reward_id))
                else:
                    chat(s, "/w reward id {} not found".format(irc_cfg.CHAN[1:], reward_id))
            except:
                chat(s, "!rewardcomplete <reward_id>")
        else:
            chat(s, "Only the channel owner can use this function")
    if re.match("!rewardrefund", message):
        if username == irc_cfg.CHAN[1:]:
            try:
                split_string = message.split()
                reward_id = int(split_string[1])
                if reward_functions.refundredemption(reward_id):
                    chat(s, "/w {} reward id {} refunded. Removing from queue and returning points".format(irc_cfg.CHAN[1:], reward_id))
                else:
                    chat(s, "/w {} reward id {} not found".format(irc_cfg.CHAN[1:], reward_id))
            except:
                chat(s, "!rewardrefund <reward_id>")
        else:
            chat(s, "Only the channel owner can use this function")
    if re.match("!addmod", message):
        #mods do bonus points only
        try:
            split_string = message.split()
            new_mod = split_string[1]
        except:
            chat(s, "!addmod <username>")
        if core_functions.user_exists(username,'admins'):
            if core_functions.user_exists(new_mod,'mods'):
                chat(s,"{} is already a mod".format(new_mod))
            else:
                core_functions.addmod(new_mod)
                chat(s,"{} added as a moderator!".format(new_mod))
        else:
            chat(s,"Only admins may add a mod")
    if re.match("!removemod", message):
        #mods do bonus points only
        try:
            split_string = message.split()
            old_mod = split_string[1]
        except:
            chat(s, "!removemod <username>")
        if core_functions.user_exists(username,'admins'):
            if core_functions.user_exists(old_mod,'mods'):
                core_functions.rmmod(old_mod)
                chat(s,"{} removed from moderators".format(old_mod))
            else:
                chat(s,"{} is not a mod".format(old_mod))
        else:
            chat(s,"Only admins may remove a mod")
    if re.match("!addadmin", message):
        try:
            split_string = message.split()
            new_admin = split_string[1]
        except:
            chat(s, "!addadmin <username>")
        if core_functions.user_exists(username,'admins'):
            if core_functions.user_exists(new_admin,'admins'):
                chat(s,"{} is already an admin".format(new_admin))
            else:
                core_functions.addadmin(new_admin)
                chat(s,"{} added as an administrator!".format(new_admin))
        else:
            chat(s,"Only admins may add an admin")
    if re.match("!removeadmin", message):
        try:
            split_string = message.split()
            old_admin = split_string[1]
            old_admin = old_admin.lower()
        except:
            chat(s, "!removeadmin <username>")
        if username == irc_cfg.CHAN[1:]:
            if old_admin == irc_cfg.CHAN[1:]: #channel owner
                chat(s,"Channel owner cannot be removed from admins")
            elif core_functions.user_exists(old_admin,'admins'):
                core_functions.rmadmin(old_admin)
                chat(s,"{} removed from admins".format(old_admin))
            else:
                chat(s,"{} is not an admin".format(old_admin))
        else:
            chat(s,"Only the channel owner may remove an admin")
    if re.match("!points", message):
        try:
            split_string = message.split()
            check_user = split_string[1]
            print check_user
        except:
            check_user = username
        if core_functions.user_exists(check_user,'chat_points') == 0:
            if check_user == username:
                core_functions.givepoints(username, 0)
            chat(s,"{} does not exist or hasn't been in this channel before".format(check_user))
            return
        points_owned = core_functions.getpoints(check_user)
        chat(s, "{} currently has {} points".format(check_user,points_owned))
    if re.match("!rank", message):
        try:
            split_string = message.split()
            check_user = split_string[1]
            print check_user
        except:
            check_user = username
        if core_functions.user_exists(check_user,'chat_points') == 0:
            if check_user == username:
                core_functions.givepoints(username, 0)
            chat(s,"{} does not exist or hasn't been in this channel before".format(check_user))
            return
        current_rank = core_functions.getrank(check_user)
        chat(s, "{} is currently rank {}".format(check_user,current_rank))
    if re.match("!top5", message):
        top5 = core_functions.gettoppoints(5)
        chat_string = ""
        for i in top5:
            chat_string += "{} is rank {} with {} points, ".format(i[0], int(i[2]) + 1, i[1])
        chat_string = chat_string[:-2]
        chat_string += "!"
        chat(s, chat_string)
    if re.match("!top10", message):
        top10 = core_functions.gettoppoints(10)
        chat_string = ""
        for i in top10:
            chat_string += "{} is rank {} with {} points, ".format(i[0], int(i[2]) + 1, i[1])
        chat_string = chat_string[:-2]
        chat_string += "!"
        chat(s, chat_string)
    if re.match("!gamble", message):
        try:
            split_string = message.split()
            gamble_points = int(split_string[1])
            gamble(s, username, gamble_points)
        except:
            chat(s, "!gamble <points to bet> Roll a 60 or above to double your points. Roll a 99 or 100 to triple them!")
    if re.match("!bonus ", message):
        if core_functions.user_exists(username,'mods') or core_functions.user_exists(username,'admins'):
            try:
                split_string = message.split()
                bonus_user = split_string[1]
                bonus_points = int(split_string[2])
                core_functions.givepoints(bonus_user, bonus_points)
                if bonus_points >= 0:
                    chat(s, "{} points have been given to {} and they now have {}".format(bonus_points, bonus_user, core_functions.getpoints(bonus_user)))
                else: #negative
                    chat(s, "{} points have been taken from {} and they now have {}".format(-1*bonus_points, bonus_user, core_functions.getpoints(bonus_user)))
            except:
                chat(s, "!bonus <username> <points>")
        else:
            chat(s, "Hey, you're not allowed to give a bonus! Stop cheating Kappa")
            shorttimeout(s, username)
    if re.match("!bonusall", message):
        if core_functions.user_exists(username,'mods') or core_functions.user_exists(username,'admins'):
            try:
                split_string = message.split()
                bonus_to_all = int(split_string[1])
                try:
                    all_chatters = core_functions.getchatlist()
                    for i in all_chatters:
                        core_functions.givepoints(i, bonus_to_all)
                    chat(s, "{} points have been given to everybody in chat!".format(bonus_to_all))
                except:
                    chat(s, "Unfortunately, the twitch API didn't return a list of all users in chat, so I cannot give everyone a bonus :( Please try this again later")
            except:
                chat(s, "!bonusall <points>")
        else:
            chat(s, "Hey, you're not allowed to give a bonus! Stop cheating Kappa")
            shorttimeout(s, username)

#Main bot loops

def make_announcements():
    #Make an announcement from announcements.txt
    while True:
        global announcecount
        time.sleep(irc_cfg.ANNOUNCEMENT_RATE)
        global paused
        if not paused:
            print("making announcement!")
            raw_announce_list = open("announcements.txt").readlines()
            announcelist = [x for x in raw_announce_list if not x.startswith('#')]
            chat(s, announcelist[announcecount])
            announcecount += 1
            announcecount %= len(announcelist) #Start from 0 if at end of list

def tickpoints():
    #Give people in chat points for staying a full tick
    #Default is once per minute
    #They must be there at the end of the tick before to get points
    #The twitch API doesn't return JSON as we like sometimes
    tickpoints = irc_cfg.POINTS_PER_TICK
    while True:
        time.sleep(irc_cfg.TICK_RATE)
        global last_chat_list
        global paused
        if not paused:
            try:
                current_chat_list = core_functions.getchatlist()
                for j in [i for i in current_chat_list if i in last_chat_list]:
                    core_functions.givepoints(j, tickpoints)
                last_chat_list = current_chat_list
                tickpoints = irc_cfg.POINTS_PER_TICK
            except: #twitch API didn't return JSON
                tickpoints += irc_cfg.POINTS_PER_TICK
                #increase points to give next tick until error doesn't happen

def process_chat():
    while True:
        time.sleep(2)
        try: #weird characters break the loop
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
            if pong(username, message):
                continue
            if core_functions.containschatcommand(message): #using slash commands
                continue #ignore
            commandlist(username, message)
            if not paused:
                givechatbonus(s, username)

#Run the three loops all together now!

if __name__ == "__main__":
    #Put each worker as a seperate thread (to share the globals)
    t1 = Thread(target = tickpoints)
    t2 = Thread(target = make_announcements)
    t3 = Thread(target = process_chat)

    #daemonize the threads so we can ^C
    t1.daemon = True
    t2.daemon = True
    t3.daemon = True

    #start yer engines
    t1.start()
    t2.start()
    t3.start()
    
    #Main thread continues until here so we sleep it forever (till ^C)
    while True:
        time.sleep(1)
