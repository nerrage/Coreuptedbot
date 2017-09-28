from bot_main import *
from threading import Thread

#Main Bot for now
#Run a thread for each process the bot should be doing (they all run in infinite loops)

coreuptedbot = bot_main('Coreupted')

#t1 = Thread(target = coreuptedbot.processchat())
t2 = Thread(target = coreuptedbot.makeannouncements())
t3 = Thread(target = coreuptedbot.givepoints())

#daemonize the threads so we can ^C
#t1.daemon = True
t2.daemon = True
t3.daemon = True

#start yer engines
#t1.start()
t2.start()
t3.start()

#Main thread continues in here so we sleep it forever (till we ^C)
while True:
    time.sleep(1)
