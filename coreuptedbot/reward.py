#rewards.py
#This class will handle the creation and management of rewards
#Creation or retrival will be other functions within the class
#Rewards live in two tables: rewards, which is the list of created rewards
#This manages the list of rewards
#claims.py manages rewards claimed by users

from irc_cfg import *
from irc_client import *
from user import *
import sqlite3

class reward:

    def __init__(self, reward, username): #reward should be in the form of !reward
        self.reward = reward
        self.username = username

    db_conn = sqlite3.connect('bot.db', check_same_thread = False)
    conn_cursor = db_conn.cursor()

    def isreward(self):
        t = (self.reward,)
        self.conn_cursor.execute("SELECT COUNT(*) FROM rewards WHERE command = ?", t)
        if self.conn_cursor.fetchone()[0] > 0:
            return True
        return False

    #Always check if it exists before moving on to getting details

    def getrewarddetails(self):
        t = (self.reward,)
        self.conn_cursor.execute("SELECT reward_name, chat_message, cost FROM rewards where command = ?", t)
        result_list = self.conn_cursor.fetchall()
        self.reward_name = result_list[0][0]
        self.chat_message = result_list[0][1]
        self.cost = int(result_list[0][2])

    def createreward(self, new_reward_name, new_chat_message, new_cost):
        whisper = "This is a deprecated area but kept to avoid db changes"
        rewardtype = "N" #deprecated
        protected = "N" #deprecated
        t = (self.reward, new_reward_name, new_chat_message, whisper, new_cost, rewardtype, protected)
        self.conn_cursor.execute("INSERT INTO rewards(command, reward_name, chat_message, whisper, cost, type protected) values(?,?,?,?,?,?,?);", t)
        self.db_conn.commit()

    def claimreward(self, param_list):
        self.getrewarddetails()
        claim_user = user(self.username)
        if not param_list: #empty
            return self.chat_message
        claim_string = " ".join(param_list)
        if claim_user.takepoints(self.cost):
            t = (self.username, self.reward, claim_string, self.cost)
            self.conn_cursor.execute("INSERT INTO reward_queue(username, reward_name, message, cost) values(?,?,?,?);", t)
            self.db_conn.commit()
            #A hack for now... Till the new bot gets runnin
            chatter = irc_client('newclient', NICK, PASS, CHAN)
            chatter.connect()
            chatter.chat("/w {} {} has claimed {} with a message of {} for {} {}. Bonus them for now if they need a refund.".format(CHAN[1:], self.username, self.reward_name, claim_string, self.cost, POINT_NAME))
            chatter.disconnect()
            return "{} claimed by {} for {} {}!".format(self.reward_name, self.username, self.cost, POINT_NAME)
        else:
            return "You don't have enough {} to claim {}, {} ({} required)".format(POINT_NAME, self.reward_name, self.username, self.cost)
