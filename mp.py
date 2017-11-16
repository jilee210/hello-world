#!/usr/bin/python
from multiprocessing import Process as P
import time
def mp(worker="Joe", sleeptime=5):
  print(worker, "sleeping: %d sec" % sleeptime)
  time.sleep(sleeptime)
  print(worker, "Done")

w1 = P(target=mp, args=('A', 2))
w2 = P(target=mp, args=('B', 40))
w3 = P(target=mp, args=())
start_time = time.time()
print("Starting w1 = P(target=mp, args=('A', 2)) and w2 = P(target=mp, args=('B', 40)) and w3=P(target=mp)")
w1.start(); w2.start(); w3.start()
print("Joining w1.join(timeout=3); w2.join(timeout=4); w3.join(timeout=6)")
w1.join(timeout=3); w2.join(timeout=4); w3.join(6)
if w1.is_alive(): print "w1 Timeout"; terminate(); w1.join()
if w2.is_alive(): print "w2 Timeout"; w2.terminate(); w2.join()
if w3.is_alive(): print "w3 Timeout"; w3.terminate(); w3.join()
print("Time took to join/terminate in sec:%.2f" % (time.time() - start_time))
