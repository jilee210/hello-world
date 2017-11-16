#!/usr/bin/python -tt
# to log output to screen and a logfile
# JL 091917 mod from internet
# Usage: copy this at the top of your python program
#        or import log [without .py extension]
#================================================
import sys
if sys.argv[0]:
  logfile=sys.argv[0] + ".log"
else: logfile="logfile.log"

class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open(logfile, "w")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)  

    def flush(self):
        #this flush method is needed for python 3 compatibility.
        #this handles the flush command by doing nothing.
        #you might want to specify some extra behavior here.
        pass    

sys.stdout = Logger()

print "*** Start logging output to console and %s" % logfile
#for i in range(10):
#  print("Hello %d" % i)
