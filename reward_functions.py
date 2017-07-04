import irc_cfg
import sqlite3
import core_functions

db_conn = sqlite3.connect('bot.db')
conn_cursor = db_conn.cursor()
owner = irc_cfg.CHAN[1:]

def createreward(command, reward_name, chat_message, cost):
    #Create a user reward
    #Make sure exceptions get handled properly
    #These are not protected (they can be deleted by the user)
    cost = int(cost)
    t = (command, reward_name, chat_message, cost, 'N') #N for not protected
    conn_cursor.execute("INSERT INTO rewards(command, reward_name, chat_message, cost, protected) values(?,?,?,?,?);", t)
    db_conn.commit()

def candeletereward(command):
    #Lets you know if the reward is protected
    #Protected rewards are built in, usually require some computation
    #returns 1 if command exists + is not protected, else returns 0
    t = (command,)
    conn_cursor.execute("SELECT COUNT(*) FROM rewards WHERE command = ? AND protected='N'", t)
    result = conn_cursor.fetchone()
    return result[0]

def deletereward(command):
    t = (command,)
    conn_cursor.execute("DELETE FROM rewards WHERE command = ?", t)
    db_conn.commit()

def rewardinfo(command):
    #Gives info about the reward itself from table
    #uses chat_message, which is public info for chatters
    t = (command,)
    conn_cursor.execute("SELECT chat_message FROM rewards WHERE command = ?", t)
    reward_info = conn_cursor.fetchone()
    return reward_info[0]

def canredeemreward(user, command):
    t = (command,)
    conn_cursor.execute("SELECT whisper_message, cost FROM rewards WHERE command = ?",t)
    result = conn_cursor.fetchall()
    print result
    whisper = result[0][0]
    cost = result[0][1]
    if core_functions.cantakepoints(user, cost):
        return True
    else:
        return False

def redeemreward(user, command, message):
    t = (command,)
    conn_cursor.execute("SELECT whisper_message, cost FROM rewards WHERE command = ?",t)
    result = conn_cursor.fetchall()
    whisper = result[0][0]
    cost = result[0][1]
    whisper = "/w " + irc_cfg.CHAN[1:] + " " + user + " " + whisper + " " + message
    core_functions.takepoints(user, cost)
    t = (user, command, whisper, cost)
    conn_cursor.execute("INSERT INTO reward_queue VALUES(?, ?, ?, ?)",t)
    db_conn.commit()
    t = (user,)
    conn_cursor.execute("SELECT rowid FROM reward_queue WHERE username = ? ORDER BY rowid DESC LIMIT 1",t)
    pointsnumber = conn_cursor.fetchone()
    pointsnumber = pointsnumber[0]
    whisper = whisper + " The reward code is " + str(pointsnumber)
    return whisper 

def completeredemption(rewardid):
    #Deletes from the queue, signalling it's done
    #returns False if reward id doesn't exist
    t = (rewardid,)
    conn_cursor.execute("SELECT COUNT(*) FROM reward_queue WHERE row_id = ?", t)
    result = conn_cursor.fetchone()
    if result[0] == 0:
        return False
    else:
        conn_cursor.execute("DELETE FROM reward_queue where rowid = ?", t)
        return True
    
def refundredemption(rewardid):
    #same as completing, but gives the points back
    t = (rewardid,)
    conn_cursor.execute("SELECT COUNT(*) FROM reward_queue WHERE row_id = ?", t)
    result = conn_cursor.fetchone()
    if result[0] == 0:
        return False
    else:
        conn_cursor.execute("SELECT username, cost FROM reward_queue where rowid = ?", t)
        refund = conn_cursor.fetchall()
        core_functions.givepoints(refund[0][1],refund[0][0])
        conn_cursor.execute("DELETE FROM reward_queue where rowid = ?", t)
        return True

def getrewards():
    #return list of commands
    conn_cursor.execute("SELECT command FROM rewards")
    data = conn_cursor.fetchall()
    columns = [elt[0] for elt in data]
    return columns

