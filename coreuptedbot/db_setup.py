# This file will create the database file necessary for the bot
# Please run this only once

import sqlite3
import irc_cfg
db_conn = sqlite3.connect('bot.db', check_same_thread = False)
conn_cursor = db_conn.cursor()
owner = irc_cfg.CHAN[1:]
t = (owner,)

#Create tables
conn_cursor.execute("CREATE TABLE chat_points (username varchar(255) PRIMARY KEY, points int);")
conn_cursor.execute("CREATE INDEX user_chatpoints on chat_points (points);")
conn_cursor.execute("CREATE TABLE bonus_chat_points (username varchar(255) PRIMARY KEY, points int);")
conn_cursor.execute("CREATE TABLE chatted_today (username varchar(255) PRIMARY KEY);")
conn_cursor.execute("CREATE TABLE mods (username varchar(255) PRIMARY KEY);")
conn_cursor.execute("CREATE TABLE admins (username varchar(255) PRIMARY KEY);")
conn_cursor.execute("CREATE TABLE gamblers (username varchar(255) PRIMARY KEY, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP);")
conn_cursor.execute("CREATE TABLE rewards (command varchar(255) PRIMARY KEY, reward_name varchar(255), chat_message varchar(255), whisper_message varchar(255), cost int, type varchar(1), protected varchar(1));")
conn_cursor.execute("CREATE TABLE reward_queue (username varchar(255), reward_name varchar(255), message varchar(255), cost int)")
conn_cursor.execute("CREATE TABLE announcements (announcement varchar(255))")
conn_cursor.execute("CREATE TABLE version (version varchar(255))")
conn_cursor.execute("CREATE TABLE ignored_users (username varchar(255))")

#Add first admin as streamer, irc channel name
conn_cursor.execute("INSERT INTO admins values(?);", t)
#Add the current version to version table to identify future migrations if needed
conn_cursor.execute("INSERT INTO version values('v0.02')")
#Insert some default announcements
conn_cursor.execute("INSERT INTO announcements values ('Thanks for checking out my stream. You earn 10 points per minute! Use !points to check your total.')")
conn_cursor.execute("INSERT INTO announcements values ('You get 1500 bonus points for your first chat message per stream!')")
conn_cursor.execute("INSERT INTO announcements values ('Check out my full list of rewards and commands with !rewards and !commands')")
conn_cursor.execute("INSERT INTO announcements values ('This bot is powered by Coreuptedbot, a free and open source bot. Check me out on GitHub: https://github.com/nerrage/Coreuptedbot/')")
db_conn.commit()
#Give the bot 1337 points :D
t1 = (irc_cfg.NICK, 1337)
conn_cursor.execute("INSERT INTO chat_points values(?,?);", t1)
db_conn.commit()
