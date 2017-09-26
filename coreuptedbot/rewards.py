#rewards.py
#This class will handle the creation and management of rewards
#Creation or retrival will be other functions within the class
#Rewards live in two tables: rewards, which is the list of created rewards
#This manages the list of rewards
#claims.py manages rewards claimed by users

from irc_cfg import *
from user import *
import sqlite3

class reward:

    def __init__(self, username, reward): #reward should be in the form of !reward
        self.username = username
        self.reward = reward

    db_conn = sqlite3.connect('bot.db')
    conn_cursor = db_conn.cursor()

    def reward_exists(self):
        t = (self.reward,)
        self.conn_cursor.execute("SELECT COUNT(*) FROM rewards WHERE command = ?", t)
        if self.conn_cursor.fetchone() > 0:
            return True
        return False

    #Always check if it exists before moving on to getting details

    def getrewarddetails(self):
        t = (self.reward,)
        self.conn_cursor.execute("SELECT reward_name, chat_message, cost FROM rewards where command = ?", t)
        result_list = self.conn_cursor.fetchall()
        self.reward_name = result[0]
        self.chat_message = result[1]
        self.cost = int(result[2])

    def createreward(self, new_reward_name, new_chat_message, new_cost):
        whisper = "This is a deprecated area but kept to avoid db changes"
        rewardtype = "N" #deprecated
        protected = "N" #deprecated
        t = (self.reward, new_reward_name, new_chat_message, whisper, new_cost, rewardtype, protected)
        self.conn_cursor.execute("INSERT INTO rewards(command, reward_name, chat_message, whisper, cost, type protected) values(?,?,?,?,?,?,?);", t)
        self.db_conn.commit()

    def claimreward(self, usermessage)
        getrewarddetails()
        claim_user = user(self.username)
        claim_string = "{} claimed with a message of {}".format(self.reward_name, usermessage)
        if claim_user.takepoints(self.cost):
            t = (self.username, self.reward, claim_string, self.cost)
            self.conn_cursor.execute("INSERT INTO rewards_queue(username, reward_name, message, cost) values(?,?,?,?);", t)
            self.db_conn.commit()
            return "{} claimed by {} for {} {}!".format(self.reward_name, self.username, self.cost, POINT_NAME)
        else:
            return "You don't have enough {} to claim {}, {} ({} required)".format(POINT_NAME, self.reward_name, self.username, self.cost)
