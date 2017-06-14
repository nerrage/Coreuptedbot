# This file will create the database file necessary for the bot
# Please run this only once

import sqlite3
import irc_cfg
db_conn = sqlite3.connect('bot.db')
conn_cursor = db_conn.cursor()
owner = irc_cfg.CHAN[1:]
t = (owner,)

#Create tables
conn_cursor.execute("CREATE TABLE chat_points (username varchar(255) PRIMARY KEY, points int);")
conn_cursor.execute("CREATE TABLE bonus_chat_points (username varchar(255) PRIMARY KEY, points int);")
conn_cursor.execute("CREATE TABLE chatted_today (username varchar(255) PRIMARY KEY);")
conn_cursor.execute("CREATE TABLE mods (username varchar(255) PRIMARY KEY);")
conn_cursor.execute("CREATE TABLE admins (username varchar(255) PRIMARY KEY);")
conn_cursor.execute("CREATE TABLE gamblers (username varchar(255) PRIMARY KEY, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP);")

#Add first admin as streamer, irc channel name
conn_cursor.execute("INSERT INTO admins values(?);", t)
db_conn.commit()
