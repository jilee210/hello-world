#!/usr/bin/python -tt
# my mod 02/21/13 from aboutscript.com
# diff two text files to overcome unix diff limit and python diff.py
# this is similar to sublst.pl
#====================================================================
import sys
if len(sys.argv) != 3:
  print "Usage: %s file1 file2" % sys.argv[0]
  sys.exit(1)

try:
  file1 = open(sys.argv[1]) 
  file2 = open(sys.argv[2])
except IOError, e:
  print "file not found: %s" % e
  sys.exit(2)

old_lines = file1.read().split('\n')
new_lines = file2.read().split('\n')
file1.close()
file2.close()
 
old_lines_set = set(old_lines)
new_lines_set = set(new_lines)

old_added = old_lines_set - new_lines_set
old_removed = new_lines_set - old_lines_set

for line in old_lines:
    if line in old_added:
        print '-', line.strip()
    elif line in old_removed:
        print '+', line.strip()

for line in new_lines:
    if line in old_added:
        print '-', line.strip()
    elif line in old_removed:
        print '+', line.strip()
