#bot_main.py
from chat_worker import *
from point_worker import *
from announcement_worker import *
from pause_watcher import *
import time
from threading import Thread, Lock

class bot_main:

    def __init__(self, name):
        self.name = name
        self.paused = False

    botlock = Lock()

    def processchat(self):
        process_chat_worker = chat_worker(self.name)
        while True:
            time.sleep(2)
            self.botlock.acquire()
            process_chat_worker.processchat(self.paused)
            self.botlock.release()

    def makeannouncements(self):
        make_announcement_worker = announcement_worker(self.name)
        while True:
            time.sleep(ANNOUNCEMENT_RATE)
            if self.paused == False:
                self.botlock.acquire()
                make_announcement_worker.makeannouncement()
                self.botlock.release()

    def givepoints(self): #specifically passive points for being in chat
        give_point_worker = point_worker(self.name)
        while True:
            time.sleep(TICK_RATE)
            if self.paused == False:
                self.botlock.acquire()
                give_point_worker.givepassivepoints()
                self.botlock.release()

    def watchforpause(self):
        watch_pause_worker = pause_watcher(self.name)
        while True:
            time.sleep(2)
            self.botlock.acquire()
            self.paused = watch_pause_worker.watchforpause(self.paused)
            self.botlock.release()
            #This doesn't switch unless the bot is told to (un)pause
            #otherwise it just returns its current state
    
    def runbot(self):
        t1 = Thread(target = self.processchat)
        t2 = Thread(target = self.makeannouncements)
        t3 = Thread(target = self.givepoints)
        t4 = Thread(target = self.watchforpause)

        t1.setDaemon(True)
        t2.setDaemon(True)
        t3.setDaemon(True)
        t4.setDaemon(True)

        #start yer engines
        t1.start()
        t2.start()
        t3.start()
        t4.start()
