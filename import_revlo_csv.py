#import_revlo_csv.py
#This is a one-time script to move points in from revlo to coreuptedbot
#Usage is "python import_revlo_csv.py revlofile.csv"
import csv
import core_functions
import sys
import collections
import sqlite3

if len(sys.argv) != 2:
    print "Usage: import_revlo_csv.py <path_to_csv_file>"
    quit()

print "Loading points..."


try: #make sure it runs cleanly, else catch and do nothing 
    csv_file = sys.argv[1]
    with open(csv_file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            user = row['Username']
            points = row['Current Points']
            core_functions.givepoints(user, points)
    print "Points loaded into database!"
    print "Do NOT run this again if users have their points! It will give them points again."
except sqlite3.OperationalError:
    print "It appears the Coreuptedbot database doesn't exist. Run db_setup.py to create it!"
except:
    print "The provided file doesn't look like a Revlo CSV!"
    print "Please double-check the provided file"
