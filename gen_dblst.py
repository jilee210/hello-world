#!/usr/bin/python
# mass run of sqls to all these databases based on tnsnames.ora file
# JL 091317
#==================================================
import re
s=open("/etc/tnsnames.ora").read()
db = sorted(re.findall(r'(^\w+)\.WORLD\s=', s, re.M)) # M for MULTILINE
print("TNS: %d" % len(db), db)
print("\n*** tnsanmes dblst in lowercase")
for d in db:
  print d.lower(), # notice comma, print continue with one space
  if d.endswith(('9','3')): # old dg 3, new dg 9
    # remove dg, leave only primaries
    db.remove(d)
    try:
      db.remove(d[:-1])  # chopoff 9 or 3, leaving 0 or 1 db only
    except: pass  # to avoid value error
print("\n\n*** filtered new dblst after removing dg -- only primaries and removing also many dan's dbs")
newdb = [d for d in db if not re.findall(r'.*dan.*', d, re.I)] # I for IGNORE case; remove dan's dbs
for d in newdb:
  print d.lower() # no comma, print at each line
