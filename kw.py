#!/usr/bin/python -tt
# Google's Python Class
# http://code.google.com/edu/languages/google-python-class/
# python.org: wiki.python.org/moin/BeginnersGuide/Programmers
# JL 062917 for all keywords example
# JL 070317 Developing examples as needed 
# version 2: 31 keywords (exec, print are removed in version 3; they become functions)
# version 3: 33 keywords (Added: False/True/None/nonlocal as keyword: 31 - 2 + 4 = 33)
# this example for verson 2 but can be easily modified by adding new keywords in the kw_ex_map function
#======================================

# A Python program to introduce and deomonstrate keywords by minimal examples

import sys, keyword

kw_all = keyword.kwlist
prog = sys.argv[0]
args = sys.argv[1:]
cnt = len(args)
argv_len = len(sys.argv)

print "prog=%s argv_len=%d, args=%s cnt=%d \nkw_all = %s, \nkw_all_cnt = %d" %(prog, argv_len, args, cnt, kw_all, len(kw_all))

# Define a main() function that prints keyword and its example 
def main():
  # Get the args from the command line if any
  if len(sys.argv) == 1:
    print "kw_all = %s" % kw_all
    kw = kw_all
  else:
    kw = args

  print "kw_args = %s"  %(kw)
  kw_example(kw)

def kw_example(k):
    for i in k:
      if i not in kw_all:
        print "%s is not a python keyword" % i
      else:
        kw_ex_map(i)

def kw_ex_map(d):  # Mod from https://learnpythonthehardway.org/book/ex37.html
  kmap = {
    'and': "True and False == 0",
    'as': "with X as Y: pass OR with open('somefile', 'r') as f: f.readline() OR import some_pkg_module as alias", 
    'assert': "assert False, \"Error!\"",
    'break': "while True: break OR for i in range(1, 100): break", 
    'class': "class Person(object)",
    'continue': "while True: continue",
    'def': "def f(): pass",
    'del': "del dict[k]",
    'elif': "if False: X; elif True: Y; else: J",
    'else': "if 0: False; elif 0: False: else: True",
    'except': "except ValueError, e: print e",
    'exec': "exec 'print \"hello\"' NOTE: no longer keyword in version 3",
    'finally': "finally: pass OR try: print \"OK\"; except: print \"Error\"; finally: print \"Always\"",
    'for': "for X in Y: pass OR for i in range(10): print 'Useful for-loop: %d' %i",
    'from': "from X import Y",
    'global': "global X OR s = 5; def f(): global s; return s += s NOTE nonlocal new keyword in version 3",
    'if': "if: X; elif: Y; else: J",
    'import': "import os OR import os, sys OR import some_pkg_module as alias",
    'in': "for X in Y: pass OR 1 in [1, 2] == True",
    'is': "1 is 1 == True OR a = [1, 2, 3]; b = a; a is b cf. a == b for value equality vs refrence/identify test" ,
    'lambda': "s = lambda y: y ** y; s(3)",
    'not': "not True == False",
    'or': "True or False == True",
    'pass': "def empty(): pass",
    'print': "print 'this string'; print('NOTE') NOTE  print(str) as function, not keyword in version 3; cf. pyformat.info",
    'raise': "raise ValueError(\"No\")",
    'return': "def X(): return Y",
    'try': "try: pass OR try: print 'this'; except: print 'that'; finally: print 'End'",
    'while': "while X: pass OR x = 0; while True: print 'do this'; if x >= 9: break; else: x += 1",
    'with': "with X as Y: pass",
    'yield': "def X(): yield Y; X().next() OR next(X)"  
  }
  if d in kmap:
     print "=" * 80
     print "Example for %s: %s" %(Color.BOLD + d, Color.BOLD + Color.BLUE + kmap[d] + Color.END )
  else:
     print "example for %s: not in kw_ex_map dictionary yet" %d
     
  pass

class Color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

# This is the standard boilerplate that calls the main() function.
if __name__ == '__main__':
  main()
