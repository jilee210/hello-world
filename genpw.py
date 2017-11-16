#!/usr/bin/python -tt
import sys, os, random, string

charset = string.ascii_letters + string.digits + '$#_'
N = int(sys.argv[1]) if len(sys.argv) == 2 else 30
firstchar=random.SystemRandom().choice(string.ascii_lowercase)
pw = firstchar + ''.join(random.SystemRandom().choice(charset) for _ in range(N-1))
print pw
