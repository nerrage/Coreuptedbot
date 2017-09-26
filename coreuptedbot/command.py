#command.py
#These are hard-coded functions of coreuptedbot
#object maps !commands into its appropriate action
#uses a dictionary of available commands to work the proper function
#returns what the bot should say
#if return false, do nothing
from user import *
from irc_cfg import * 
import sqlite3
import requests
from random import randint

class command:

    def __init__(self, command, user, usertext):
        self.command = command
        self.user = user
        self.text = usertext
        self.wordlist = usertext.split()

    db_conn = sqlite3.connect('bot.db')
    conn_cursor = db_conn.cursor()
  
    #This directs us to the correct function to execute
    #input !foobar as self.command => go to and execute foobar_function
    def execute_command(self):
        #dispatch !commands to commands_function()
        method_name = self.command[1:] + "_function"
        method = getattr(self, method_name, False)
        #if it doesn't exist, will return False
        #if false just ignore; invalid command
        return method()
    
    #To add a new command for !foo, make a foo_function that does what you want
    #These are in alphabetical order, please keep it that way :)
    def addadmin_function(self):
        function_user = user(self.user)
        if function_user.isadmin() or function_user.isowner():
            try:
                newadmin = str(self.wordlist[0]).lower()
            except:
                return "!addadmin <user>"
            if user(newmod).isadmin():
                return "{} is already an admin".format(newadmin)
            else:
                t = (newadmin,)
                self.conn_cursor.execute("INSERT INTO admins values (?)",t)
                self.db_conn.commit()
                return "{} added as an administrator!".format(newadmin)
        else:
            return "Only an admin or stream owner can use !addadmin"

    def addmod_function(self):
        function_user = user(self.user)
        if function_user.isadmin() or function_user.isowner():
            try:
                newmod = str(self.wordlist[0]).lower()
            except:
                return "!addmod <user>"
            if user(newmod).ismod():
                return "{} is already a moderator".format(newmod)
            else:
                t = (newmod,)
                self.conn_cursor.execute("INSERT INTO mods values (?)",t)
                self.db_conn.commit()
                return "{} added as a moderator!".format(newmod)
        else:
            return "Only an admin or stream owner can use !addmod"

    def bonus_function(self): #!bonus nerrage 1500
        function_user = user(self.user)
        if function_user.ismod() or function_user.isadmin() or function_user.isowner():
            try: #validate the inputs
                bonus_target = str(self.wordlist[0]).lower() 
                bonus_to_give = int(self.wordlist[1])
            except:
                return "!bonus <user> <{} to give>".format(POINT_NAME)
            recipient_user = user(bonus_target)
            recipient_user.givepoints(bonus_to_give)
            return "{} has been given {} {} and now has {} {}".format(bonus_target, bonus_to_give, POINT_NAME, recipient_user.getpoints(), 
        else:
            return "Only a moderator, administrator, or stream owner can user !bonus" 

    def bonusall_function(self):
        if function_user.ismod() or function_user.isadmin() or function_user.isowner():
            try: #validate number
                bonus_to_give = int(self.wordlist[0])
            except:
                return "!bonusall <{} to give to all>".format(POINT_NAME) 
            #big thanks to bad_hombres on twitch for helping with this
            r = requests.get('http://tmi.twitch.tv/group/user/%s/chatters' % owner)
            bad_hombres = json.loads(r.text)
            chat_list = bad_hombres["chatters"]["moderators"]
            chat_list.extend(bad_hombres["chatters"]["staff"])
            chat_list.extend(bad_hombres["chatters"]["admins"])
            chat_list.extend(bad_hombres["chatters"]["global_mods"])
            chat_list.extend(bad_hombres["chatters"]["viewers"])
            for chatter in chat_list:
                bonus_recipient = user(chatter)
                bonus_recipient.givepoints(bonus_to_give)
            return "{} {} have been given to everyone in chat!".format(bonus_to_give, POINT_NAME)
        else:
            return "Only a moderator, administrator, or stream owner can user !bonusall" 
    
    def commands_function(self):
        return "Coreuptedbot commands: " + str(COMMANDS_URL)

    def gamble_function(self):
        gamble_amount = self.wordlist[0] #!gamble 500
        gambler = user(self.user)
        print gambler.getpoints()
        print gamble_amount
        try:
            gamble_amount = int(gamble_amount)
        except:
            return "!gamble <{} to bet or ALL> Roll a 60 or above to double your {}. Roll a 99 or 100 to triple them!".format(POINT_NAME,POINT_NAME)
        if gamble_amount == 'all':
            gamble_amount = gambler.getpoints()
        if gamble_amount < MINIMUM_GAMBLE:
            return "Must gamble at least {} {}".format(MINIMUM_GAMBLE,POINT_NAME)
        if gambler.getpoints() < gamble_amount:
            return "You don't have enough {} to gamble that many, {}".format(POINT_NAME,self.user)
        #Update eligible gamblers
        self.conn_cursor.execute("DELETE FROM GAMBLERS where timestamp < DATETIME('now', '-%s second')" % GAMBLE_RATE)
        self.db_conn.commit()
        if gambler.user_exists_in_table('gamblers'):
            return "You can only gamble once every {} seconds, {}".format(GAMBLE_RATE, self.user) 

        #Good to gamble if they've made it past here
        t = (self.user,)
        self.conn_cursor.execute("INSERT INTO GAMBLERS(username) VALUES(?)", t)
        self.db_conn.commit()
        gambler.takepoints(gamble_amount) #take wager
        roll = randint(1,100)
        if roll < 60: #you lose
            return "Rolled {}. {} lost {} {} and now has {} points".format(roll, self.user, gamble_amount, POINT_NAME, gambler.getpoints())
        elif roll < 99:
            gambler.givepoints(2*gamble_amount)
            return "Rolled {}. {} won {} {} and now has {} points".format(roll, self.user, 2*gamble_amount, POINT_NAME, gambler.getpoints())
        else: #99 or 100
            gambler.givepoints(3*gamble_amount)
            return "Rolled {}. {} won {} {} and now has {} points".format(roll, self.user, 3*gamble_amount, POINT_NAME, gambler.getpoints())
        return "Something went wrong while gambling!" #should not get here

    def gambleall_function(self): #!gambleall
        self.wordlist = ['all']
        return self.gamble_function()

    def pingbot_function(self): #!pingbot
        return "Coreuptedbot is ONLINE MrDestructoid"

    def points_function(self): #!points
        if wordlist = []: #no args from user after !points
           user_to_query = self.user 
        else:
           user_to_query = wordlist[0]
        querieduser = user(user_to_query)
        if querieduser.user_exists_in_table('chat_points'):
            return "{} currently has {} {}".format(user_to_query, queried_user.getpoints(), POINT_NAME)
        else:
            return "{} does not exist or hasn't been in this channel before".format(user_to_query)

    def rank_function(self): #!rank
        if wordlist = []: #no args from user after !rank
           user_to_query = self.user 
        else:
           user_to_query = wordlist[0].lower()
        querieduser = user(user_to_query)
        if querieduser.user_exists_in_table('chat_points'):
        self.conn_cursor.execute("SELECT (SELECT COUNT(*) FROM chat_points as t2 WHERE t2.points > t1.points) AS PointRank FROM chat_points AS t1 WHERE t1.username = ?", t)
        query_result = conn_cursor.fetchone()
        result = int(query_result[0] + 1)
        return "{} is currently rank {}".format(user_to_query, result)
        else:
            return "{} does not exist or hasn't been in this channel before".format(user_to_query)

     def removeadmin_function(self):
        function_user = user(self.user)
        if function_user.isowner():
            try:
                oldadmin = str(self.wordlist[0]).lower()
            except:
                return "!removeadmin <user>"
            if user(olmod).isadmin():
                t = (oldmod,)
                self.conn_cursor.execute("DELETE FROM admins where username = ?",t)
                self.db_conn.commit()
                return "{} removed from admins".format(oldmod)
            else:
                return "{} is not an admin".format(oldmod)
        else:
            return "Only the stream owner can use !removeadmin"

   def removemod_function(self):
        function_user = user(self.user)
        if function_user.isadmin() or function_user.isowner():
            try:
                oldmod = str(self.wordlist[0]).lower()
            except:
                return "!removemod <user>"
            if user(oldmod).ismod():
                t = (oldmod,)
                self.conn_cursor.execute("DELETE FROM mods where username = ?",t)
                self.db_conn.commit()
                return "{} removed from moderators".format(oldmod)
            else:
                return "{} is not a moderator".format(oldmod)
        else:
            return "Only an admin or stream owner can use !removemod"


    def rewards_function(self):
        return "Coreuptedbot rewards: " + str(REWARDS_URL)

    def top5_function(self): #!top5
        self.conn_cursor.execute("SELECT t1.*, (SELECT count(*) FROM chat_points AS t2 WHERE t2.points > t1.points) AS PointRank FROM chat_points AS t1 ORDER BY points DESC LIMIT 5")
        result_list = self.conn_cursor.fetchall()
        response = ''
        for result in result_list:
            response += "{} is rank {} with {} {}, ".format(result[0], int(result[2]) + 1, result[1], POINT_NAME) 
        response = response[:-2] #remove last ", "
        response += "!"
        return response

    def top10_function(self): #!top10
        self.conn_cursor.execute("SELECT t1.*, (SELECT count(*) FROM chat_points AS t2 WHERE t2.points > t1.points) AS PointRank FROM chat_points AS t1 ORDER BY points DESC LIMIT 10")
        result_list = self.conn_cursor.fetchall()
        response = ''
        for result in result_list:
            response += "{} is rank {} with {} {}, ".format(result[0], int(result[2]) + 1, result[1], POINT_NAME) 
        response = response[:-2] #remove last ", "
        response += "!"
        return response

test = command('!gamble', 'nerrage', '700')
print test.execute_command()
