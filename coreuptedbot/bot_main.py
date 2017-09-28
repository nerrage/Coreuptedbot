#bot_main.py
from chat_worker import *
from point_worker import *
from announcement_worker import *
import time

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
