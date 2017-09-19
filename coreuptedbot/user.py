#user.py
#this only requires a username to init the object
#any other information can be gleaned from our sqlite db
from irc_cfg import *
import sqlite3
class user:

    def __init__(self, username):
        self.username = username
    #get db connection
    db_conn = sqlite3.connect('bot.db')
    conn_cursor = db_conn.cursor()
    #twitch irc names are all lowercase
    #for some reason some users cant be .lower()'d
    #that's why there's exception handling around it

    def user_exists_in_table(self, tablename):
        #Returns 1 if user is in table
        #Returns 0 otherwise
        try:
            irc_username = self.username.lower()
        except:
            print("{} could not be cast to lower".format(self.username))
        t = (irc_username,)
        self.conn_cursor.execute("SELECT COUNT(*) FROM "+tablename+" WHERE username = ?", t)
        result = self.conn_cursor.fetchone()
        return result[0]
    
    def givepoints(self, points_to_give):
        try:
            irc_username = self.username.lower()
        except:
            print("{} could not be cast to lower".format(self.username))
            return
        t = (points_to_give, irc_username)
        if self.user_exists_in_table('chat_points'):
            self.conn_cursor.execute("UPDATE chat_points SET points = points + ? WHERE username = ?", t)
            self.db_conn.commit()
        else:
            self.conn_cursor.execute("INSERT INTO chat_points(points,username) values(?,?)", t)
            self.db_conn.commit()
        return
    
    def getpoints(self):
        try:
            irc_username = self.username.lower() #Twitch IRC usernames are all lowercase
        except:
            print("{} could not be cast to lower".format(username))
            return None
        if self.user_exists_in_table('chat_points'):
            t = (irc_username,)
            self.conn_cursor.execute("SELECT points FROM chat_points WHERE username = ?", t)
            return self.conn_cursor.fetchone()[0]
        else:
            self.givepoints(0)
            return self.getpoints()

    def takepoints(self, points_to_take):
        if points_to_take > self.getpoints():
            return False #can't take points 
        else:
            self.givepoints(-points_to_take)
            return True #points taken successfully 

    def give_first_chat_bonus(self):
        try:
            irc_username = self.username.lower()
        except:
            print("{} could not be cast to lower".format(username))
            return None
        if self.user_exists_in_table('chatted_today'): #no soup for you
            return False
        else:
            print "tadays bonus is " + str(FIRST_CHAT_BONUS_POINTS)
            self.givepoints(FIRST_CHAT_BONUS_POINTS)
            t = (irc_username,) 
            self.conn_cursor.execute("INSERT INTO chatted_today VALUES (?)", t)
            self.db_conn.commit()
            return True

    def ismod(self):
        return self.user_exists_in_table('mods')

    def isadmin(self):
        return self.user_exists_in_table('admins')

    def isowner(self):
        try:
            irc_username = self.username.lower()
        except:
            print("{} could not be cast to lower".format(username))
            return None
        if irc_username == CHAN[1:]:
            return True
        else:
            return False
