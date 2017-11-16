### JL 07/05/16 to automate fn/em dev/prd Oracle PSU
#   Usage: fab [-H h1,h2,h3 -R r1,r2,r3 -P (parallel, non-interactive option)] -f fabfile_of_choice_or_default task1 task2 ...
#   Usage: fab -h   fab -H fnsqltst01,fnsqltst02 -P -- any os commands [sudo /oracle/scripts/db_action.sh stop_all etc]
#   Note: seperate local cmd from parallel hosts due to multiple executons of local cmd
#   JL 07/22/16 Usage of execute meta task to control local and remote tasks: execute(task, *args,**kwargs)
#   JL 07/27/16 Usage of execute: not to use @roles but inside role='tst1' etc. to avoid repeatition of local cmd
#   JL 02/24/17 stopall_asm_crs commented crs section due to grid patch first before OS
#=============================================================================================================================
# Per-task, command-line host lists (fab mytask:host=host1) override absolutely everything else.
# Per-task, decorator-specified host lists (@hosts('host1')) override the env variables.
# Globally specified host lists set in the fabfile (env.hosts = ['host1']) can override such lists set on the command-line,
#  but only if you are not careful (or want them to.)
# Globally specified host lists set on the command-line (--hosts=host1) will initialize the env variables, but that's it.
#=========================================================================================================================
"""
*** Meta task with execute(task, *args,**kwargs)
*** For FN/eMAT Oracle Patching
*** To stopall_xxx calls local stop_dg_ps_xxx and then remote parallel stop_oem_asm_crs_xxx where xxx is @roles('tst'|'prd'|..) 
*** fab -w (to warning instead of abort) stopall_xxx  
"""
from fabric.api import *  
env.user = 'lee.98a'
env.warn_only = True # not abort by default, but warn only and move on to stopall: with settings(warn_only=True):
env.roledefs = {
  'prd': ['emsqlprd01', 'fnsqlprd01'],
  'drrpt': ['emsqlprd02', 'fnsqlprd02', 'fnsqlprd03'],
  'tst': ['emsqltst01', 'emsqltst02', 'fnsqltst01', 'fnsqltst02', 'fnsqltst03'],
  'tst23': ['emsqltst02', 'fnsqltst02', 'fnsqltst03'],
  'tst1': ['emsqltst01', 'fnsqltst01'],
  'dmo': ['NO_SERVER'],
}

# Add custom global variables: use it in pythonic syntax!
# ps db list
env.dblst = {
  'prd': ['fnosu','emosu'],
  'drrpt': ['fnrpt','fn8trn', 'fn8trn1', 'fn8trn2', 'fn8trn3'],
  'tst': ['fn8dmo','fn8stg','fn8dev2','fn8qa2','fn8qad','em8dmo','em8stg','em8dev2','em8qa2',
          'fn8qa','fn8qap','fn8dev','fn8devp','em8dev','em8qa'],
  'tst23': ['fn8dmo','fn8stg','fn8dev2','fn8qa2','fn8qad','em8dmo','em8stg','em8dev2','em8qa2'],
  'tst1':  ['fn8qa','fn8qap','fn8dev','fn8devp','em8dev','em8qa'],
  'dmo':  ['fn8dmo'],
}
# dg db list
env.dglst = {
  'prd': ['fnosu0','emosu0'],
  'drrpt': ['fnosu0','emosu0'],
  'tst': ['fn8qa0','em8qa0'],
  'tst1': ['fn8qa0','em8qa0'],
  'tst23': ['fn8qa0','em8qa0'],
  'dmo':  ['fn8qa0'],
}

# DO NOT use env.hosts except in a fixed case, which overwrites -H option in command line, it is better to user -R with roledefs
#env.hosts = ['fnsqltst01','fnsqltst02','emsqltst01','emsqltst02']

#=== import multiprocessing =============================
from multiprocessing import Process, Lock # Pool etc
import sys
#=== from fabfile_bo.py import tasks ... MAKE this LOCAL under funtion, not GLOBAL roledef being overwritten!!!
def chk_asm_dbsize():
  """ chk_asm_dbsize to run ocs/asm_report asm_diskgroup_stats with -H """
  print "running asm_report asm_diskgroup_stats to see dbsize on a host"
  sudo("/oracledba/cluster/scripts/asm_report asm_diskgroup_stats", user="oracle")
def chk_gridhome():
  """ use -R or -H chk_gridhome contains /app/grid/12c102, OK with /grid/12c102 """
  sudo("/oracledba/jlee/patch/chk_gridhome", user="oracle" )  
def chk_opatch(oh='11g'):
  #sys.path.insert(0,'')
  #from fabfile_bo import chk_opatch
  """ use -R or -H chk_opatch:oh [12c|12c_clone|11g_clone] """
  sudo("/oracledba/jlee/patch/chk_opatch_local %s | egrep '^Patch|opatch lsinv'" % oh, user="oracle" )  
def chk_opatch_db(*db):
  """ chk_opatch_db:db1,db2,... """
  print "running run_chk_psu12c.sh for %s" % (' '.join(db))
  local("/home/lee.98a/bin/run_chk_psu.sh %s" % (' '.join(db)) )
def import_fabfile_task_test(*db):
  #pass
  print "*** BEFORE imported env.roledefs['tst'] from fabfile_bo: %s" % ' '.join(env.roledefs['tst'])
  sys.path.insert(0,'')
  #import fabfile_bo 
  #from fabfile_bo import * # ok with __all__ = ['chk_alert'] in fabfile_bo
  from fabfile_bo import chk_alert
  print "*** AFTER imported env.roledefs['tst'] from fabfile_bo: %s" % ' '.join(env.roledefs['tst'])
  print "*** imported from fabfile_bo *db: %s" % ' '.join(db)
  print "*** imported chk_alert task from fabfile_bo: how to use it?"
  dblst=' '.join(db) ### REDEFINE here OK
  chk_alert(dblst)   ### chk_alert(db) => seq item 0: xxpected string, tuple found error
  local('uptime')
def patch_home_launch_hive(*srv):
  """ to launch hive_mod.py:srv1,srv2,... to execute any command in parallel such as patch_home_clone_bo etc. """
  if len(srv) < 1:
    print "Usage: %s:srv1,srv2,..." % sys._getframe().f_code.co_name #  func_name in sys
    exit()
  else:
    print "srvlist = %s" % ' '.join(srv)
    local(". /home/lee.98a/bin/my_env_py_hive %s" % ' '.join(srv) )
#import multiprocessing
def multi_work_test(num):
  """ multiprocessing.Procss(target=multi_work_test, args=num) """
  print 'Multi worker:', num
  return
#=== core ps, dg, em functions for multiprocessing ==============
def exec_psctl_dblst(l, cmd, grp):
  l.acquire()
  try:
    execute(psctl_dblst, cmd, grp, host='localhost')
  finally:
    l.release()
def exec_dgctl(l=Lock(),cmd='status', grp='dmo'):
  l.acquire()
  execute(dgctl, cmd, ' '.join(env.dglst[grp]), host='localhost')
  l.release()
def exec_oemctl(l,cmd,role_arg):
  l.acquire()
  try:
    execute(oemctl, cmd, role=role_arg)
  #except EnvironmentError:
  #  print "*** IOError/OSError"
  except StandardError:
    print "*** StandardError" # no output so far
  except Warning:
    print "*** Warnings OK"   # no output so far
  finally:
    l.release()
#=== core ps, dg, em functions for multiprocessing ==============
def stopall_ps_dg_em(cmd="status",grp="tst1"):
  """ multiprocessing.Procss(target=stopall_ps_dg_em, args=tuple)
  multiprocessing.Procss(target=psctl|oemctl|dgctl, args=('xxx','yyy',...)) """
  lock = Lock() # synchronize the output
  ps = Process(target=exec_psctl_dblst, args=(lock,cmd,grp,))
  ps.start()
  #=== Logic Needed Here for dgctl for cmd, grp!!!
  dg = Process(target=exec_dgctl, args=(lock, cmd,grp,))
  dg.start()
  em = Process(target=exec_oemctl, args=(lock,cmd,grp,))
  em.start()
  dg.join(timeout=60) # from 30 sec
  em.join(timeout=60) # from 30 sec
  ps.join(timeout=180) # from 120 sec
  print '*** ps.is_alive() = ', ps.is_alive()
  print '*** timeout 3 min, terminating ps/em/dg ...'
  if ps.is_alive(): ps.terminate()
  if em.is_alive(): em.terminate()
  if dg.is_alive(): dg.terminate()
  print '*** Done with grp = %s OK' % (grp)
#==== MOD needed above for cmd, grp etc ======================
def multiproc_test(cmd='status',grp='tst1'):
  """ multiprocessing.Procss(target=multi_work_test, args=num)
  multiprocessing.Procss(target=psctl|oemctl|dgctl, args=('xxx','yyy',...)) """
#  jobs = []
#  for i in range(3):
#    p = multiprocessing.Process(target=multi_work_test, args=(i,))
#    jobs.append(p)
#    p.start()
#    p.join(timeout=60) # p.join(timeout=600) to wait to finish 
  lock = Lock() # synchronize the output
  ps = Process(target=exec_psctl_dblst, args=(lock,cmd,grp,))
  ps.start()
  dg = Process(target=exec_dgctl, args=(lock, cmd,'fn8qa0 em8qa0',))
  dg.start()
  #em = execute(multiprocessing.Process(target=oemctl, args=('status',)), host='fnsqltst01')
  em = Process(target=exec_oemctl, args=(lock,cmd,grp,))
  em.start()
  dg.join(timeout=30)
  print '*** ps.is_alive() = %s' % ps.is_alive()
  ps.join(timeout=120)
  print '*** ps.is_alive() = ', ps.is_alive()
  em.join(timeout=30)
  print '*** Done with grp = %s OK' % (grp)
#===============================================
#@roles('tst1')
def env_test(name='Joe'):
  """ set env var with shell_env usage """
  with shell_env(A='a', B='b', C='c'):
    local("echo A is $A %s" % name)
def env_dblst_test(grp='tst'):
  """ custom dblst test """
  #print "env.dblst groups: %s" % env.dblst
  #print "tst group: %s" % env.dblst['tst']
  #print "prd group: %s" % env.dblst['prd']
  #print "arg group: %s %s" % (grp, env.dblst[grp])
  print "dblst[%s]: %s" % (grp, ' '.join(env.dblst[grp]))
def env_dblst(grp='dmo'):
  """ custom dblst called by psctl """
  print "%s" % ' '.join(env.dblst[grp])

@parallel
#@roles('tst1')
def uptime():
  """test uptime with roles with @parallel"""
  #run("uptime; whoami")
  sudo("uptime;whoami", user="oracle")
#@runs_once
@hosts('localhost')
def psctl_stat_dblst(grp='dmo'):
  """ localhost psctl_stat_dblst:tst1|tst23|drrpt|prd """
  sudo("/oracledba/jlee/patch/psctl status %s" % (' '.join(env.dblst[grp])), user="oracle")
@hosts('localhost')
def psctl_stat(*db):
  """ localhost psctl_stat:db1,db2,, """
  sudo("/oracledba/jlee/patch/psctl status %s" % (' '.join(db)  ), user="oracle")
#@roles('tst1') #####<<<<===== this REPEATS the local cmd -- PROBLEM HERE!!! 
def exec_local_remote_test(role_arg='tst1'):
  """Test local/remote to simulate stopall_xxx: Problem prompted with connection host for local when no host/role defined """
  execute(uptime, role=role_arg) # remote function with @roles('tst1')
  #execute(oemctl,"status", role=role_arg) # remote function with @roles('tst1')
  execute(crs_check, host='fnsqltst01')
  execute(pslst,role='tst23') # remote function with @roles('tst1')
  #execute(chk_dg,"fn8qa", host='localhost') # local function 
  execute(psctl,"status","fn8qa") # OK local function
  #execute(psctl_stat,"fn8qa", host='localhost') # OK-local function
  #execute(env_test) # local function 
def exec_call_test(arg="tst23"):
  """ call exec_local_remote_test with arg -- default arg="tst23" """
  exec_local_remote_test(arg)
#================================= PROBLEM to FIX: seperate local vs remote cmds ==============
#@roles('tst1')
def chk_dg(*db):
  """ local chk_dg:db,db2 """
  local("/home/lee.98a/bin/chk_dg %s" % ' '.join(db)) # with -P, this executes multiple times
  #uptime() ### test with -P with local
#================================= PROBLEM ==============
def psctl_stat_tst1():
  """ test func arg passing to psctl(cmd,*db): psctl("status", "fn8dev fn8qa")
  psctl_stat("fn8dev fn8qa") or psctl_stat("fn8dev","fn8qa")
  better yet psctl("status", "fn8dev fn8qa") 
  """
  #psctl("status", "fn8dev fn8qa") # or psctl_stat("fn8dev","fn8qa")
  execute(psctl_dblst,"status", "dmo", host='localhost') # or psctl_stat("fn8dev","fn8qa")
def oemctl_stat():
  """ oemctl:status"""
  oemctl("status")
def oemctl_local(cmd,*srv):
  """ oemctl:status test with local my script similar to psctl: oemctl_local:cmd,srv,srv2,..."""
  local("/home/lee.98a/bin/oemctl %s %s" % (cmd, ' '.join(srv)))
#============================= TEST functions above =====================

#=== Local Functions: psctl chk_dg dgctl ===============================
@hosts('localhost')
def psctl(cmd,*db):
  """ localhost psctl:stop|start|status,db1,db2,, """
  sudo("/oracledba/jlee/patch/psctl %s %s" % (cmd, ' '.join(db)  ), user="oracle")
@hosts('localhost')
def psctl_dblst(cmd='status',grp='dmo'):
  """ localhost psctl:stop|start|status,grp[tst|tst23|tst1|drrpt|prd|dmo] """
  sudo("/oracledba/jlee/patch/psctl %s %s" % ( cmd, ' '.join(env.dblst[grp]) ), user="oracle")
def chk_dg(*db):
  """ local chk_dg:db,db2 """
  local("/home/lee.98a/bin/chk_dg %s" % ' '.join(db)) 
def dgctl(cmd,*db):
  """ local dgctl off|on dblst: dgctl:on|off,dblst """
  local("/home/lee.98a/bin/dgctl %s %s" % (cmd, ' '.join(db)) )
def dgctl_off_prd():
  """ dgctl off fnosu0 emosu0 """
  dgctl("off","fnosu0 emosu0")
def dgctl_on_prd():
  """ dgctl on fnosu0 emosu0 """
  dgctl("on","fnosu0 emosu0")
def dgctl_off_tst():
  """ dgctl off fn8qa0 em8qa0 """
  dgctl("off","fn8qa0 em8qa0")
def dgctl_on_tst():
  """ dgctl on fn8qa0 em8qa0 """
  dgctl("on","fn8qa0 em8qa0")

#=== Remote Functions: da_stop/start oemctl pslst asm_stop/start crs_stop/start/check ==========
def da_stop():
  """ db_action.sh stop_all with -R roles or -H hostlist """
  sudo("/oracle/scripts/db_action.sh stop_all", user="oracle")
def da_start():
  sudo("/oracle/scripts/db_action.sh start_all", user="oracle")
@parallel
def oemctl(cmd):
  """ oemctl cmd=stop|start|status: oemctl:cmd with -R or -H in parallel"""
  sudo("/oracle/middleware/agent12c/bin/emctl %s agent" % cmd, user="oracle")
def chk_ohlib_perm(oh="11g"):
  """ after opatch, chk_ohlib_perm:oh[11g,11g_clone,12c,12c_clone] for psoft scheduler """
  sudo("/oracledba/jlee/patch/chk_ohlib_perm %s" % oh, user="oracle")
def chk_pslst(*srv):
  """ chk_pslst srvlst  """
  local("/home/lee.98a/bin/chk_pslst %s" % ' '.join(srv))
@parallel
def pslst():
  """ pslst with -R or -H in parallel before/after opatch  """
  run("/oracledba/jlee/pslst")
@parallel
def asm_stop():
  """ asm_util stopall with -R or -H in parallel """
  sudo("/oracle/scripts/asm_util stopall", user="oracle")
@parallel
def asm_start():
  sudo("/oracle/scripts/asm_util startall", user="oracle")
@parallel
def crs_stop():
  """ crsctl stop has -R or -H in parallel """
  sudo("sudo /grid/12c102/bin/crsctl stop has", user="oracle")
@parallel
def crs_check():
  """ crsctl check has -R or -H in parallel """
  sudo("sudo /grid/12c102/bin/crsctl check has", user="oracle")
@parallel
def crs_start():
  """ crsctl start has -R or -H in parallel """
  sudo("sudo /grid/12c102/bin/crsctl start has", user="oracle")

#========== App Functions ========================================
def patch():
  """ Not Yet Implemented: pass arg and use execute method """
  pass
def patch_home_mod(fun="fn_em",oh="11g_clone"):
  """ Usage:fn_em|bo 11g|11g_clone|12c|12c_clone for single host patch due to interactive prompts; use hive_mod.py for parallel patching """
  sudo("/oracledba/jlee/patch/patch_home.mod %s %s" % (fun,oh), user="oracle")
def patch_home():
  """ single host patch due to interactive prompts; use hive_mod.py for parallel patching """
  sudo("/oracledba/jlee/patch/patch_home", user="oracle")
def patch_home_clone():
  """ single host patch due to interactive prompts; use hive_mod.py for parallel patching """
  sudo("/oracledba/jlee/patch/patch_home_clone", user="oracle")
def patch_db(*db):
  """ patch_db:db,... with -H """
  sudo("/oracledba/jlee/patch/patch_db %s" % ' '.join(db), user="oracle")
@hosts('fnsqlprd03')
def patch_fnrpt_trn():
  sudo("/oracledba/jlee/patch/patch_db fnrpt fn8trn fn8trn1 fn8trn2 fn8trn3", user="oracle")
@hosts('fnsqlprd01')
def patch_fnosu0():
  sudo("/oracledba/jlee/patch/patch_db fnosu0", user="oracle")
@hosts('emsqlprd01')
def patch_emosu0():
  sudo("/oracledba/jlee/patch/patch_db emosu0", user="oracle")
#### =================  stopall_xxx calls local stop_dg_ps_xxx and then remote stop_oem_asm_crs_xxx ===
def stop_dg_ps_prd():
  """ stop dg, ps/as local functions first for prd """ 
  dgctl("off","fnosu0 emosu0")
  psctl("stop","fnosu emosu") 
@roles('prd')
@parallel
def stop_oem_asm_crs_prd():
  """ stop oem/asm/crs for prd in @parallel on prd servers as in @roles('prd') """ 
  oemctl("stop")
  asm_stop()
  crs_stop()
def stopall_prd():
  """ stop everything: oem, dg, ps/as, asm, crs for OS Patches given -R(oles for hosts) """ 
  stop_dg_ps_prd()
  stop_oem_asm_crs_prd()

def stop_dg_ps_tst():
  """ stop dg, ps/as local functions first for tst """ 
  dgctl("off","fn8qa0 em8qa0")
  psctl("stop","fn8dev fn8devp fn8qa fn8qap em8dev em8qa fn8dev2 fn8dmo fn8qa2 fn8stg fn8qad em8dev2 em8dmo em8qa2 em8stg") 
@roles('tst')
@parallel
def stop_oem_asm_crs_tst():
  """ stop oem/asm/crs for tst in @parallel on tst servers as in @roles('tst') """ 
  oemctl("stop")
  asm_stop()
  crs_stop()
def stopall_tst():
  """ stop everything: oem, dg, ps/as, asm, crs for OS Patches given -R(oles for hosts) """ 
  stop_dg_ps_tst()
  stop_oem_asm_crs_tst()

def stopall_tst_fast():
  """ stop everything: oem, dg, ps/as, asm, crs for OS Patches given -R(oles for hosts) """ 
  stopall_ps_dg_em("stop","tst")
  stopall_asm_crs("tst")

#### =================  call stop_dg_ps_xxx and then stop_oem_asm_crs_xxx ===========================
#### =================  call exec_stopall_remote after local cmds ===========================
@parallel
def exec_stopall_remote(role_arg):
  """ core function to stop oem/asm/crs in parallel being called by stopall_xxx with role_argument """
  execute(oemctl, "stop", role=role_arg)
  execute(asm_stop, role=role_arg)
  #execute(crs_stop, role=role_arg) # OS Automatic
  execute(pslst, role=role_arg)
@parallel
def stopall_asm_crs(role_arg='dmo'):
  """ core function to stop asm/crs in parallel being called by stopall_xxx with role_argument """
  if role_arg == "dmo":
    print "invalid role_arg = ", role_arg
    return
  else:
    execute(asm_stop, role=role_arg)
    #execute(crs_stop, role=role_arg) # OS automatic
    execute(pslst, role=role_arg)
####===============================================
#@roles('drrpt') # DO NOT use due to repeation of local cmd; define role='drrpt' in execute method
def stopall_drrpt():
  """ stop everything: oem, dg, ps/as, asm, crs for OS Patches given -R(oles for hosts) """ 
  execute(dgctl_off_prd, host='localhost')
  #execute(psctl,"stop","fnrpt fn8trn fn8trn1 fn8trn2 fn8trn3 fn8trn4", host='localhost') 
  execute(psctl_dblst,"stop","drrpt", host='localhost') 
  exec_stopall_remote("drrpt")
def stopall_drrpt_fast():
  """ stop everything: ps/as, dg, em in parallel first, and  asm, crs for OS Patches given -R(oles for hosts) """ 
  stopall_ps_dg_em("stop","drrpt")
  stopall_asm_crs("drrpt")
def stopall_prd_fast():
  """ stop everything: ps/as, dg, em in parallel first, and  asm, crs for OS Patches given -R(oles for hosts) """ 
  stopall_ps_dg_em("stop","prd")
  stopall_asm_crs("prd")
def stopall_prd():
  """ stop everything: oem, dg, ps/as, asm, crs for OS Patches given -R(oles for hosts) """ 
  execute(dgctl_off_prd, host='localhost')
  execute(psctl,"stop","fnosu emosu", host='localhost') 
  exec_stopall_remote("prd")
def stopall_tst1():
  """ stop everything: oem, dg, ps/as, asm, crs for OS Patches given -R(oles for hosts) """ 
  execute(dgctl_off_tst, host='localhost')
  execute(psctl,"stop","fn8dev fn8devp fn8qa fn8qap em8dev em8qa", host='localhost') 
  exec_stopall_remote("tst1")
def stopall_tst1_fast():
  """ stop everything: ps/as, dg, em in parallel first, and  asm, crs for OS Patches given -R(oles for hosts) """ 
  stopall_ps_dg_em("stop","tst1")
  stopall_asm_crs("tst1")
def stopall_tst23():
  """ stop everything: oem, dg, ps/as, asm, crs for OS Patches given -R(oles for hosts) """ 
  execute(dgctl_off_tst, host='localhost')
  execute(psctl,"stop","fn8dev2 fn8dmo fn8qa2 fn8stg fn8qad em8dev2 em8dmo em8qa2 em8stg", host='localhost') 
  exec_stopall_remote("tst23")
def stopall_tst23_fast():
  """ stop everything: ps/as, dg, em in parallel first, and  asm, crs for OS Patches given -R(oles for hosts) """ 
  stopall_ps_dg_em("stop","tst23")
  stopall_asm_crs("tst23")
def stopall_tst():
  """ stop everything: oem, dg, ps/as, asm, crs for OS Patches given -R(oles for hosts) """ 
  execute(dgctl_off_tst, host='localhost')
  execute(psctl,"stop","fn8dev fn8devp fn8qa fn8qap em8dev em8qa fn8dev2 fn8dmo fn8qa2 fn8stg fn8qad em8dev2 em8dmo em8qa2 em8stg") 
  exec_stopall_remote("tst")

