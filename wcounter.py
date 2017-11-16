#!/usr/bin/python
# JL 081017 to simulate wordcount.py with High Performace collections container Counter availble >= version 2.7
# Note: python 2.7 and 3.x, Counter not available in 2.6
# ======================================================
import sys
from collections import Counter as C

if len(sys.argv) < 2:
  print 'usage: ./counter.py file [topcount]'
  sys.exit(1)
text = open(sys.argv[1]).read()
if text:
  wc = C(text.lower().split())
  #wc = C(text.split())
else:
  print("text/file empty")
  sys.exit(2)

if len(sys.argv) == 3:
  topcount = int(sys.argv[2])
else:
  topcount = 5

print("* most_common topcount %d: %s" % (topcount, wc.most_common(topcount))) # wc.most_common()  will sort all by freq highest first
print("* complete count up to maxcnt 50 to limit output")
maxcnt = 0
for i in sorted(wc, key=wc.get, reverse=True):
  # help(dict.get): D.get(k[,d]) -> D[k] if k in D, else d.  d defaults to None.
  # the below two: print i as tuples(not dict) and wc[i] to 0, so need to print("{} {}".format(i[0], i[1]))
  # for i in wc.most_common(): 
  # for i in sorted(wc.items(), key=lambda t: t[1], reverse=True):  # cf. wc as dict vs wc.items() tuple like most_common
  #print('{} {}'.format(i, wc[i]))
  print("%s : %d" % (i, wc[i]))
  maxcnt += 1
  if maxcnt == 50: break
