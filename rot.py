#!/usr/bin/python
# rot47 similar to rot13 used by this.py
# JL 09/28/17
# echo "The Quick Brown Fox Jumps Over The Lazy Dog" | tr '\!-~' 'P-~\!-O'
#========================================
import sys
if len(sys.argv) == 2: # one arg of string quote
  s = sys.argv[1]
else:
  s = "Why did the chicken cross the road?"

#Rotate by 47 (ASCII rot)
def rot47(s):
    x = []
    for i in range(len(s)):
        j = ord(s[i])
        if j >= 33 and j <= 126:
            x.append(chr(33 + ((j + 14) % 94)))
        else:
            x.append(s[i])
    return ''.join(x)

#Rotate by 13 (a-z  classic rot)
def rot13(s):
    for char in s:
        d = {}
        for c in (65, 97):
            for i in range(26):
                d[chr(i+c)] = chr((i+13) % 26 + c)
    return "".join([d.get(c, c) for c in s])

# main
print(rot47(s))
