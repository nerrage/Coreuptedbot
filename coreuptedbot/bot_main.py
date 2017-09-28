#bot_main.py
from chat_worker import *
from point_worker import *
from announcement_worker import *
import time
from threading import Thread

class bot_main:

    def __init__(self, name):
        self.name = name
        self.paused = False

    def processchat(self):
        process_chat_worker = chat_worker(self.name)
        while True:
            time.sleep(2)
            process_chat_worker.processchat()

    def makeannouncements(self):
        make_announcement_worker = announcement_worker(self.name)
        while True:
            if self.paused == False:
                time.sleep(ANNOUNCEMENT_RATE)
                make_announcement_worker.makeannouncement()

    def givepoints(self): #specifically passive points for being in chat
        give_point_worker = point_worker(self.name)
        while True:
            if self.paused == False:
                time.sleep(TICK_RATE)
                give_point_worker.givepassivepoints()
    
    def runbot(self):
        t1 = Thread(target = self.processchat)
        t2 = Thread(target = self.makeannouncements)
        t3 = Thread(target = self.givepoints)

        t1.setDaemon(True)
        t2.setDaemon(True)
        t3.setDaemon(True)

        #start yer engines
        t1.start()
        t2.start()
        t3.start()
