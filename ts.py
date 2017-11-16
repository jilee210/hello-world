#!/usr/bin/env python
# https://stackoverflow.com/questions/3589214/generate-multiple-random-numbers-to-equal-a-value-in-python
# 10/17/17
#=======================
import random, sys
#def constrained_sum_sample_pos(n, total):
"""
Return a randomly chosen list of n positive integers summing to total.
Each such list is equally likely to occur.
"""

def timesht(n, total=40):
  dividers = sorted(random.sample(xrange(1, total), n - 1))
  return [a - b for a, b in zip(dividers + [total], [0] + dividers)]

taskn = int(sys.argv[1]) if len(sys.argv) > 1 else 6
total = int(sys.argv[2]) if len(sys.argv) > 2 else 8
print("%d tasks sum %d * 5 = %d" % (taskn, total, total*5)) 
wkday = {1:"M", 2:"T", 3:"W", 4:"R", 5:"F"}
for i in range(1,6):
  print(wkday[i]),(timesht(taskn, total))

