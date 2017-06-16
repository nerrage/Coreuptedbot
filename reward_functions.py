import irc_cfg
import sqlite3

db_conn = sqlite3.connect('bot.db')
conn_cursor = db_conn.cursor()
owner = irc_cfg.CHAN[1:]

def createreward(command, reward_name, chat_message, cost):
    #Create a user reward
    #Make sure exceptions get handled properly
    cost = int(cost)
    t = (command, reward_name, chat_message, cost)
    conn_cursor.execute("INSERT INTO rewards values(?,?,?,?);", t)
    db_conn.commit()

def deletereward(command):
    t = (command,)
    conn_cursor.execute("DELETE FROM rewards WHERE command = ?", t)
    db_conn.commit()
