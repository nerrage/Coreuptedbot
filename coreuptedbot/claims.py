#claims.py
#This interacts with individual claims within the rewards_queue table
import sqlite3

class claims:

    def __init__(self, claim_id):
        self.claim_id = claim_id

    db_conn = sqlite3.connect('bot.db')
    conn_cursor = db_conn.cursor()

    def getclaimdetails(self):
        t = (self.claim_id,)
        self.conn_cursor.execute("SELECT username, reward_name, message, cost FROM reward_queue WHERE rowid = ?", t)
        results = conn_cursor.fetchall()
        self.username = results[0]
        self.reward_name = results[1]
        self.message = results[2]
        self.cost = results[3]

    def completeredemption(self):
        t = (self.claim_id,)
        self.conn_cursor.execute("DELETE FROM reward_queue WHERE rowid = ?", t)
        self.db_conn.commit()
        #points are already taken so we're done

    def refundredemption(self):
        getclaimdetails()
        t = (self.claim_id,)
        refund_user = user(self.username)
        refund_user.givepoints(int(cost))
        self.conn_cursor.execute("DELETE FROM reward_queue WHERE rowid = ?", t)
        self.db_conn.commit()
