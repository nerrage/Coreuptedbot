#announcement_worker.py
#connects to IRC, leaves a message from announcements table, then disconnects
#No need to stay connected, don't want to hog IRC connections
from irc_cfg import *
from irc_client import *
import sqlite3

class announcement_worker:

    def __init__(self, name):
        self.name = name
        self.db_conn = sqlite3.connect('bot.db')
        self.conn_cursor = self.db_conn.cursor()
        self.conn_cursor.execute("SELECT COUNT(*) FROM announcements;")
        self.num_announcements = self.conn_cursor.fetchone()[0]
        self.announce_count = 0

    def makeannouncement(self):
        chat_client = irc_client(self.name, NICK, PASS, CHAN)
        self.conn_cursor.execute("SELECT * FROM announcements")
        next_announcement = self.conn_cursor.fetchall()[0][self.announce_count]
        chat_client.connect()
        chat_client.chat(next_announcement)
        chat_client.disconnect()
        self.announce_count += 1
        self.announce_count %= self.num_announcements
