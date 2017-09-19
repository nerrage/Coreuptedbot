#command.py
#These are hard-coded functions of coreuptedbot
#object maps !commands into its appropriate action
#uses a dictionary of available commands to work the proper function
#returns what the bot should say
#if return false, do nothing
from user import *
from irc_cfg import * 
import sqlite3
from random import randint

class command:

    def __init__(self, command, user, usertext):
        self.command = command
        self.user = user
        self.text = usertext
        self.wordlist = usertext.split()

    db_conn = sqlite3.connect('bot.db')
    conn_cursor = db_conn.cursor()

    def execute_command(self):
        #dispatch !commands to commands_function()
        method_name = self.command[1:] + "_function"
        method = getattr(self, method_name, False)
        #if false just ignore; invalid command
        return method()

    #To add a new command for !foo, make a foo_function that does what you want
    def commands_function(self):
        return COMMANDS_URL

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
            return "Rolled {}. {} lost {} points and now has {} points".format(roll, self.user, gamble_amount, gambler.getpoints())
        elif roll < 99:
            gambler.givepoints(2*gamble_amount)
            return "Rolled {}. {} won {} points and now has {} points".format(roll, self.user, 2*gamble_amount, gambler.getpoints())
        else: #99 or 100
            gambler.givepoints(3*gamble_amount)
            return "Rolled {}. {} won {} points and now has {} points".format(roll, self.user, 3*gamble_amount, gambler.getpoints())
        return "Something went wrong while gambling!" #should not get here

    def gambleall_function(self): #!gambleall
        self.wordlist = ['all']
        return self.gamble_function()


test = command('!gamble', 'nerrage', '700')
print test.execute_command()
