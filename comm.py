#!/usr/bin/python 
# commands utility to execute python or any external scripts
# JL 091917 os.system("script args") gives only exit status, not output
# Note: name cmd.py already exists with python install so custom scripts should not get in the way
# so changed name from cmd.py to comm.py etc. Otherwise, you will get a magic error???
# also remove com.pyc compiled bytecode as well!!!
# sys.path will hit the current dir first
#===================================================================
import log # to log output optional
import commands as c
out = c.getoutput("hello.py dan joe")
print(out)

print dir(c)
out2 = c.getstatusoutput("uptime")
print(out2)

