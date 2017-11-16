#!/usr/bin/python
# strip comments from python program files
# JL 08/02/17
# JL 08/03/17 fixed the case of quoted '#' vs regular # in the same line with assumption with space#
#        new_line = line.split(" #")[0].rstrip() # NOTE space before # to solve this problem!
# Note: this program can be used to remove commments # from shell, python files
#===================================================================================================
""" =============== start of long comments
https://www.rosettacode.org/wiki/Strip_comments_from_a_string#Python

>>> marker, line = '#', 'apples, pears # and bananas'
>>> line[:line.index(marker)].strip()
'apples, pears'

def remove_comments(line, sep):
    for s in sep:
        line = line.split(s)[0]
    return line.strip()
 
# test
print remove_comments('apples ; pears # and bananas', ';#')

import re
 
m = re.match(r'^([^#]*)#(.*)$', line)
if m:  # The line contains a hash / comment
    line = m.group(1)

=========================================
TODO: how to remove long comments as well
docstr = re.sub(r'\"\".*\"\"',r'', str)
=============== end of long comments
"""

import sys, re # sys for argv, re for doc string removal
if len(sys.argv) < 2:
  filename =  "hello.py"
else:
  filename = sys.argv[1]

try:
  f = open(filename, "r")
# how to remove any doc string with """ xxxx """
  docstr = ""  # flag for docstr start/end
  cnt = 0  # flag for docstr start/end
  for line in f:
    if line.startswith('#!'): print(line.rstrip()); continue
    if line  == '\n': continue # skip empty lines
    #if line.isspace(): continue
    #if line.lstrip().startswith('#'): continue  ### skip any lines starting with \s*# except #! below
    #print("docstr, org line", docstr, line)
    #T = bool(re.search(r'"""', line))
    #print("TEST OK? bool = %s" % T)
    if re.match(r'"""', line): ### PROBLEM HERE for docstr END 2nd one!!!
      if re.match(r'""".*"""', line): #### skip single line doc string
         continue
      cnt = cnt + 1 # cnt += 1
      docstr = "start" if cnt % 2 == 1 else "end"
      ###      if cnt % 2 == 1: ### starting """
      ###        docstr = "start"
      ###      else:            ### ending """ <== cnt % 2 == 0 whenever even numbers
      ###        #print("* docstr_END ")
      ###        docstr = "end"
      continue 
    elif docstr == "start":
      continue
    else: 
      ### how to handle with quoted "#" case like this program?!
      if line.lstrip().startswith('#'):
        continue  ### skip any lines starting with \s*#
      quoted = re.search(r'[\'\"]#.?[\'\"]', line)  ### check whether has "#" or '#!' in line
      if not quoted:
        new_line = line.split("#")[0].rstrip()
      else: ### MOD HERE, quoted, chop off not quoted # portion -- How?
        new_line = line.split(" #")[0].rstrip() # NOTE space before # to solve this problem!
        #new_line = line # still not perfect with line like sep = '#' xxxx # comment at the same line! cf. [py]minify
      if new_line: ### not empty after # split line processing
        print(new_line.rstrip())
except IOError as e:
  print("An error occured trying to read the file", e)
