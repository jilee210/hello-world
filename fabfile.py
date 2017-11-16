### http://docs.fabfile.org/en/1.13/tutorial.html
### Note: fab -h to see command line options
###       fab -Hhost1,host2,.. and/or -Rrole1,role2,...  -- sudo -u oracle "cmds; scripts; etc"
### double minus(--) means anoymous user fuction/command call NOT defined in this fabfile functions/tasks
###
### JL 08/07/17
###===============================================================================================
from fabric.api import *  
env.user = 'lee.98a'
env.warn_only = True # not abort by default, but warn only and move on to stopall: with settings(warn_only=True):
env.roledefs = {
  'prd': ['prd01', 'prd01'],
  'drrpt': ['prd02', 'prd02', 'prd03'],
  'tst': ['tst01', 'tst02', 'tst01', 'tst02', 'tst03'],
  'tst23': ['tst02', 'tst02', 'tst03'],
  'tst1': ['tst01', 'tst01'],
  'dmo': ['NO_SERVER'],
}

# Add custom global variables: use it in pythonic syntax!
# ps db list -- took out em8stg, fn8stg 
env.dblst = {
  'prd': ['fno','emo'],
  'drrpt': ['fnr','trn', 'trn1', 'trn2', 'trn3'],
  'tst': ['dmo','ev2','qa2','qad','dmo','dev2','qa2',
          'qa','qap','dev','devp','dev','qa'],
   'dmo':  ['dmo'],
}
#============ python functions below ===========
def pslst():
  """ pslst with -R or -H in parallel before/after opatch  """
  run("/oracledba/jlee/pslst")

def prompt_yn():   
  prompt("Do you really run this? (y/n)", "yn", default = "Y")
  if env.yn in ['n', 'N']: print("exiting without execution");exit()
def hello(greet="Hello", name="World"):   
  prompt_yn()
  print("%s %s!" % (greet, name))

@hosts('localhost')
def psctl(cmd='status', *dbgrp):
  """ localhost psctl:stop|start|status,dbgrp[fn8dmo,fn8qa,...|tst|tst23|tst1|drrpt|prd|dmo] """
  # dbgrp is tuple like ('tst1',) or ('fn8qa','em8qa')
  # print(dbgrp)
  if not dbgrp:
     print("Usage: psctl:stop|start|status,dbgrp[fn8dmo,fn8qa,...|tst|tst23|tst1|drrpt|prd|dmo]")
     return 1
  dbgrp = ' '.join(dbgrp) # redefine tuple to string
  if dbgrp in env.dblst.keys():
     #print("if %s" % dbgrp)
     dblst = ' '.join(env.dblst[dbgrp])
  else:
     #print("else: %s" % dbgrp)
     dblst = dbgrp
  print("* %s dblst= %s" % (cmd, dblst))
  sudo("/oracledba/jlee/patch/psctl %s %s" % (cmd, dblst), user="oracle")
#==============
import sys
def patch_home_launch_hive(*srv):
  """ to launch hive_mod.py:srv1,srv2,... to execute any command in parallel such as patch_home_clone_bo etc. """
  if len(srv) < 1:
    print "Usage: %s:srv1,srv2,..." % sys._getframe().f_code.co_name #  func_name in sys
    exit()
  else:
    print "srvlist = %s" % ' '.join(srv)
    local(". /home/lee.98a/bin/my_env_py_hive %s" % ' '.join(srv) )
def chk_opatch(oh='11g'):
  #sys.path.insert(0,'')
  #from fabfile_bo import chk_opatch
  """ use -R or -H chk_opatch:oh [12c|12c_clone|11g_clone] """
  sudo("/oracledba/jlee/patch/chk_opatch_local %s | egrep '^Patch|opatch lsinv'" % oh, user="oracle" )  

@parallel
def oemctl(cmd):
  """ oemctl cmd=stop|start|status: oemctl:cmd with -R or -H in parallel"""
  sudo("/oracle/middleware/agent12c/bin/emctl %s agent" % cmd, user="oracle")

@parallel
def da_stop():
  """ db_action.sh stop_all with -R or -H in parallel """
  sudo("/oracle/scripts/db_action.sh stop_all", user="oracle")

@parallel
def da_start():
  """ db_action.sh start_all with -R or -H in parallel """
  sudo("/oracle/scripts/db_action.sh start_all", user="oracle")

@parallel
def asm_stop():
  """ asm_util stopall with -R or -H in parallel """
  sudo("/oracle/scripts/asm_util stopall", user="oracle")
@parallel
def asm_start():
  """ asm_util startall with -R or -H in parallel """
  sudo("/oracle/scripts/asm_util startall", user="oracle")

@parallel
def crs_stop():
  """ crsctl stop has -R or -H in parallel """
  sudo("sudo /grid/12c102/bin/crsctl stop has", user="oracle")
@parallel
def crs_start():
  """ crsctl start has -R or -H in parallel """
  sudo("sudo /grid/12c102/bin/crsctl start has", user="oracle")
@parallel
def crs_check():
  """ crsctl check has -R or -H in parallel """
  sudo("sudo /grid/12c102/bin/crsctl check has", user="oracle")

def dgctl(cmd='status',*db):
  """ local dgctl off|on|status primary_db0|1: fab dgctl:on|off|status,fn8qa0,em8qa0,... """
  local("/home/lee.98a/bin/dgctl %s %s" % (cmd, ' '.join(db)) )

def stopall(role_arg):
  """ core function to stopall for OS patches: fab stopall:tst|tst1|tst23|drrpt|prd etc. ..."""
  #cmd = "status" # Test Note: comment asm_stop as well
  cmd = "stop" # REAL
  prompt("Do you REALLY STOPall? (y/n)", "yn", default = "Y")
  if env.yn in ['n', 'N']: print("exiting without execution"); exit()
  execute(oemctl, cmd, role=role_arg)
  execute(psctl, cmd, role_arg)
  execute(asm_stop, role=role_arg)
  #execute(crs_stop, role=role_arg) # OS Automatic
  execute(pslst, role=role_arg)

def startall(role_arg):
  """ core function to startall for OS patches: fab stopall:tst|tst1|tst23|drrpt|prd etc. ..."""
  #cmd = "status" # Test Note: uncomment asm_start as well 
  cmd = "start" # REAL
  prompt("Do you REALLY STARTall? (y/n)", "yn", default = "Y")
  if env.yn in ['n', 'N']: print("exiting without execution"); exit()
  #execute(crs_start, role=role_arg) # OS Automatic
  execute(asm_start, role=role_arg)
  execute(psctl, cmd, role_arg)
  execute(oemctl, cmd, role=role_arg)
  execute(pslst, role=role_arg)

def tomcat(cmd='status', *db):
  """ tomcat:status|stop|start|,db1,db2,..."""
  if not db:
    db=('wsdev',)
  local("/oracle/scripts/tomcat_action.sh --database %s --action %s" % (' '.join(db), cmd))
