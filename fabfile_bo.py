from fabric.api import * # run etc
from fabric.contrib.console import confirm 
from fabric.operations import prompt 
from fabric.context_managers import quiet
import sys # sys._getframe().f_code.co_name is func_name!!! cf. sys.argv[0] => fab, so sys.argv[1] for function name!
from multiprocessing import Process as P # used in patchall_pt ### hanging issue
from multiprocessing import Lock  # sync output 
from multiprocessing import Pool  # user of pool.map for better output display
from multiprocessing.dummy import Pool as ThreadPool # to avoid wasqlprd03 datapatch hanging OK
from functools import partial # to pass more param to pool.map
import re
import commands as c # stty echo with ThreadPool not hanging but stty echo needed
#from multiprocessing.dummy import Process as P # used in patchall_pt, user multithreading
#from multiprocessing.dummy import Lock  # sync output 
#======== patchall_pt multiprocessing error, not executing run_datapatch
# No handlers could be found for logger "paramiko.transport"
# Success for unrequested channel! [??]
#import logging
#logging.getLogger('paramiko.transport').addHandler(logging.StreamHandler())
# import pdb # debug test role vs roles in execute(pslst, role(s)=rolearg)

#=========== do not export env but only some tasks in all=[...]
#__all__ = ['chk_alert'] # still env imported
#__all__ = [] # No export at all but env imported
#========================================
env.user = 'lee.98a'
env.warn_only = True # not abort by default, but warn only and move on to stopall: with settings(warn_only=True):
env.roledefs = {
  'prd': ['wasqlprd01', 'wasqlprd03', 'wasqlprd02'],
  'tst': ['wasqltst01', 'wasqltst02', 'wasqltst03'],
  'tst1': ['wasqltst01'],
  'tst2': ['wasqltst02'],
  'tst3': ['wasqltst03'],
  'dmo': ['wasqltst01'],
}
# custom patch db list
env.dblst = {
  'prd': ['waosu0','wahrosu0'],
  'tst': ['wsdev','wsqa','wapt','wahrpt'],
  'tst1':  ['wsdev'],
  'tst2':  ['wsqa'],
  'tst3':  ['wapt','wahrpt'],
  'dmo':  ['wsdev'],
}
# for patch_db execute for multiple hosts case as well as a single host # TODO 
env.host_dblst = {
  'wasqltst01': ['wsdev'],
  'wasqltst02': ['wsqa'],
  'wasqltst03': ['wapt','wahrpt'],
  'wasqlprd01': ['waosu0'],
#  'wasqlprd02': ['waosu9','wahrosu9'],
  'wasqlprd03': ['wahrosu0']
}

#### patch_home_bo select prompt not showing due to this!!! localize? or debug or tee to a logfile if need for now
#sys.path.insert(0,'')
#import log   ### log.py to output to screen and logfile.log being reused, even for fab -l

#env.hosts = ['wasqlprd01','wasqlprd03','wasqlprd02']
#env.hosts = ['fnsqltst01','fnsqltst02','emsqltst01','emsqltst02']
# fabric.contrib.console.confirm vs. var = fabric.operations.prompt("What is your name?")
#@runs_once
############## TEST 
@parallel
def uptime():
  run("uptime")
  #return run("uptime")
  #result = run("uptime")
  #print "normal result.return_code = %d" % result.return_code
  #print "result =\n%s" % result
#def test(*rolearg):
def test_exec(cmd='status',rolearg='tst1'):
  #execute(dg_mount,cmd,hosts='wasqlprd02') # conflict with @hosts('wasqlprd02') on dg_mount? No, OK with host/hosts
  execute(oemctl,cmd, hosts=env.roledefs[rolearg]) # test host vs hosts for oemctl execute model

def test(rolearg='dmo'): # cf 'dmo' vs ['dmo'] vs ('dmo',)
  """test uptime with roles"""
  #sys.path.insert(0,'')
  #import log
  #if confirm("Do you want to run this: uptime?", default=True):
  #prompt("Do you want to run this: uptime? (y/n)",'ans', default='N')
  print "rolearg=%s len=%d" % ( rolearg, len(env.roledefs[rolearg]) ) # OK here, why dmo/tst1 has problem, not multiple tst?
  prompt("Do you want to run this: pslst? (y/n)",'ans', default='N')
  print "ans = %s" % env.ans
  if env.ans == 'y' or env.ans == 'Y':
    #print "OK? rolearg = %s" % ','.join(rolearg)
    if not rolearg:
      rolearg=('dmo',) # tuple/list or ['dmo']
      print "default rolearg = %s" % rolearg
    #pdb.set_trace()
    if len(env.roledefs[rolearg]) > 1: # HOW to do this here? NOT HERE but LOGIC and role vs roles below: d m o or t s t 2 not dmo, tst
       print "rolearg=%s multiple hosts!" % rolearg
       execute(uptime, role=rolearg)        # OK with role, role for only one role
       print "DO NOT USE patch_home_bo for hosts = %s" % ' '.join(env.roledefs[rolearg])
       #execute(patch_home_bo, role=rolearg) # serial execution one host after another -- no benefit
       print "launching hive for hosts = %s" % ' '.join(env.roledefs[rolearg])
       patch_home_launch_hive(' '.join(env.roledefs[rolearg])) # OK parallel 
       print "After launching hive parallel exeution ... exit" 
       exit()  # if not exit here, then go to next
    #result = execute(uptime, roles=rolearg)        # OK with roles, role for only one role
    #result = execute(pslst, host='dba01')        # OK with roles, role for only one role
    with quiet():
      result = execute(pslst, role=rolearg)        # FIXED HERE:  Not OK with roles:d m o, role=dmo
      #result = execute(pslst, roles=rolearg)        # PROBLEM HERE:  Not OK with roles:d m o, role=dmo
    print "execute result without .return_code unlike local,run.sudo = \n%s" % result
    for k in result:
      #if result[k] == "": # not None but '' here in pslst
      if "OK" in result[k]: #  from pslst echo "*** OK to apply OracleHome Patch"
        print "None returned on host = %s" % k
      else:
        print "host = %s : %s" %( k, result[k])
    #print "result.return_code = %d" % result.return_code
    #execute(uptime, roles=['dev','prd'] # OK list, not tuple here
  else:
    print "No execution since ans = %s" % env.ans
############## 
def stopall_bo(cmd='status',rolearg='dmo'):
  """ stopall_bo:cmd(status|stop),rolearg(tst[123],prd) for stopall tomcat, oem, dg, db for OS patches """
  if not confirm("Do you want to stopall:cmd=%s,rolearg=%s?" % (cmd,rolearg), default=True):
     print "*** NOT Confirmed, return"
     return
  if rolearg == 'dmo':
    db='wsdev'
    cmd='status'
  elif rolearg == 'tst1':
    db='wsdev'
  elif rolearg == 'tst2':
    db='wsqa'
  elif rolearg == 'tst3':
    db='wapt wahrpt'
  elif rolearg == 'tst': # changed from 'dev' to 'tst'
    db='wsdev wsqa wapt wahrpt'
  elif rolearg == 'prd':
    db='waosu wahrosu'
  print "cmd= %s rolearg= %s db= %s" % (cmd, rolearg, db)
  # skip tomcat shutdown for OS monthly patch test 5/8/17
  # Not skip tomcat shutdown for OS monthly patch test 8/31/17 too many alerts
  execute(tomcat,cmd, db, host='localhost') 
  #return  # TEST for now
  if rolearg == 'prd':
    execute(oemctl,cmd, hosts=env.roledefs[rolearg]) # Dan added oem to the other servers as well 8/31/17
    #execute(oemctl,cmd, host='wasqlprd03')
    # better off though all three servers shutdown/startup, Dan fixed db_action script
    execute(dgctl,cmd, 'waosu0 wahrosu0', host='localhost') 
  if cmd == 'status':
    print "\n*** SKIP execute(da_stop, role=%s)" % rolearg
  elif cmd == 'stop':
    #return # TEST now
    print "\n*** execute(da_stop, role=%s)" % rolearg
    execute(da_stop,role=rolearg)
    # skip dg_mount since Dan's fix of db_action.sh script to automate dg
    #if rolearg == 'prd':
    #  print "\n*** execute(dg_mount,%s, role=%s)" % (cmd,rolearg) # cmd => %s!!!
    #  execute(dg_mount,cmd)
    #  #execute(dg_mount,cmd, host='wasqlprd02') # @hosts on dg_mount
  print "*** Final Check by execute(pslst,role=%s)" % (rolearg)
  execute(pslst, role=rolearg)
def tomcat(cmd='status', *db):
  if not db:
    db=('wsdev',)
  local("/oracle/scripts/tomcat_action.sh --database %s --action %s" % (' '.join(db), cmd))
@hosts('wasqlprd02')  
def dg_mount(cmd='status'):
  """ dataguard databases (wa[hr]osu9) not up/down by da_stop|start due to /etc/oratab set to N """
  if cmd != 'start' or cmd != 'stop':
     print "Usage: fab dg_mount:stop|start for waosu9/wahrosu9"
     pslst()
     return
  else:
    sudo("/oracledba/jlee/patch/mount_dg_wa %s waosu9 wahrosu9" % cmd, user="oracle")
@parallel
def da_stop():
  sudo("/oracle/scripts/db_action.sh stop_all", user="oracle")
def da_start():
  sudo("/oracle/scripts/db_action.sh start_all", user="oracle")
def patch_home_bo():
  sudo("/oracledba/jlee/patch/patch_home_bo", user="oracle")
def patch_home_clone_bo():
  sudo("/oracledba/jlee/patch/patch_home_clone_bo", user="oracle")
def patch_home_bo_prd_hive():
  """ to launch hive_mod.py for bo prd servers to execute any command in parallel such as patch_home_bo etc. """
  local(". /home/lee.98a/bin/my_env_py_bo")
def patch_home_launch_hive(*srv):
  """ to launch hive_mod.py:srv1,srv2,... to execute any command in parallel such as patch_home_clone_bo etc. """
  if len(srv) < 1:
#    if sys.argv[1] in ['-H','-R']:
#      print "Usage: patch_home_launch_hive:srv1,srv2,..."
#      #func_name = sys.argv[2] # -R tst wrong etc
#    else:
#      func_name = sys.argv[1]  # sys.argv[0] is fab itself
#      print "Usage: %s:srv1,srv2,..." % func_name # 
    print "Usage: %s:srv1,srv2,..." % sys._getframe().f_code.co_name #  func_name in sys
    exit()
  else:
    print "srvlist = %s" % ' '.join(srv)
    local(". /home/lee.98a/bin/my_env_py_hive %s" % ' '.join(srv) )
def exec_patch_id(srv):
  """ exec_patch_id:srv for get_datapatch_id to avoid hang with fab interactive multiprocessing in patchall_pt """
  return execute(patch_id, host=srv)
def exec_patch_db(srv):
  """ exec_patch_db:srv for run_datapatch[_noprompt] due to hang with fab interactive multiprocessing in patchall_pt """
  execute(patch_db,"%s" % ' '.join(env.host_dblst[srv]), host=srv)
#def exec_patch_db_noprompt(lock,srv):
def exec_patch_db_noprompt(srv):
  """ exec_patch_db_noprompt:srv for run_datapatch[_noprompt] due to hang with fab interactive multiprocessing in patchall_pt """
  ###lock = Lock() # should from parent process, not here -- how to pass lock in pool.map(func, list)?
  #lock.acquire()
  try:
    result = execute(patch_db_noprompt,"%s" % ' '.join(env.host_dblst[srv]), host=srv)
    return result
  finally:
    pass
    #lock.release()
def patch_id():
  """ patch_id to get_datapatch_id 12c with -R or -H """
  return sudo("/oracledba/jlee/patch/get_datapatch_id", user="oracle")
def patch_db(*db):
  """ patch_db:db,... for run_datapatch 12c with -R or -H """
  sudo("/oracledba/jlee/patch/run_datapatch %s" % ' '.join(db), user="oracle")
def patch_db_noprompt(*db):
  """ patch_db_noprompt:db,... for run_datapatch 12c with -R or -H """
  return sudo("/oracledba/jlee/patch/run_datapatch_noprompt %s" % ' '.join(db), user="oracle")
#===================================================================================
def patchall_pt(cmd='status',rolearg='tst3'):
  """ patchall(cmd,rolearg): stopall_bo(stop,tst3), pslst, patch_home_bo, patch_db:wapt,wahrpt for run_datapatch 12c """
  execute(stopall_bo, cmd, rolearg) # cmd 'status' to 'stop' for REAL
  with quiet(): # supress everything due to redundant from stopall_bo/pslst
    result = execute(pslst, role=rolearg) # NOT roles for d m o abort; stopall_bo runs pslst at the end, but want to capture only pslst
  #if rolearg == 'prd':
  if len(env.roledefs[rolearg]) > 1: # multiple hosts
    print "*** NOTICE for rolearg= %s has multiple hosts: Exiting before opatch -- DO production/multiple hosts; USE hive_mod.py for parallel!" % rolearg
    print "launching hive for hosts = %s" % ' '.join(env.roledefs[rolearg])
    prompt("Do you want to exit now (y/n)",'ans', default='Y')
    if env.ans == 'y' or env.ans == 'Y':
      exit() # exit for multiple hosts like 'prd'
    else:
      print "ToDoList: TESTing needed with execute(cmd,args, role=rolearg when multiplehosts?, exiting anyway sorry!"
      use_hive = 'Yes' # set flag for multiple hosts patch_home etc. instead of patch_home_bo single host
      hostlst = env.roledefs[rolearg]
      print "*** Continuing with use_hive = %s for %s ..." % (use_hive, hostlst)
  else:
    use_hive = 'No'
    hostlst = env.roledefs[rolearg]
  #exit()
  #for k in result:  # BUG: multiple prompts for rolearg='prd' three hosts! so exit above for multiple hosts case
  # use result.values() with: if"CHECK" in result.values() all values should be "OK", none should with "CHECK"
  # excute result is dict for each host and return value while run,local,sudo has .return_code extra
  #if "OK" not in result[k]: ### TEST everthing down; from pslst: echo "*** OK to apply OracleHome Patch"
  #if "OK" in result[k]: ### REAL everthing down; from pslst: echo "*** OK to apply OracleHome Patch"
  # COMENT/UNCOMENT HERE BELOW to TEST/REAL
  print "*** pslst result.values: %s" % result.values() # To Verfify
  if "CHECK" in str(result.values()): ### convert to str first!!!
     print "CHECK in str(result.values()) = YES covert to str works!"
  else:
     print "CHECK in result.values() = WHY NO"
  if "CHECK" not in str(result.values()): ### REAL everthing down; from pslst: echo "*** OK to apply OracleHome Patch"
  #if "CHECK" in str(result.values()): ### TEST everthing NOT down; from pslst: echo "*** CHECK xxx ..."
    print "*** OK to Patch OH and 12c datapatch" # % str(result.values())
    prompt("Do you want to run patch_home_bo or patch_home_launch_hive and run_datapatch? (y/n)",'ans', default='N')
    print "ans = %s" % env.ans
    if env.ans == 'y' or env.ans == 'Y':
      print "HERE OK? ..."
      #print "Will start run_datapatch ... exit"
      #exit()
      if use_hive == 'Yes':
        print "*** Starting patch_home_launch_hive ..."
        patch_home_launch_hive(' '.join(env.roledefs[rolearg]))
      else:
        print "*** Starting patch_home_bo ..."
        execute(patch_home_bo, role=rolearg)
      oh="12c"
      print "*** chk_opatch for oh=%s  ..." % oh
      execute(chk_opatch, oh, role=rolearg)
      print "*** Starting run_datapatch for %s on %s" % (' '.join(env.dblst[rolearg]), ' '.join(hostlst))
      prompt("*** Continue with run_datapatch without further prompts in parallel (last chance, no harm though)? (y/n)",'ans', default='Y')
      print "ans = %s" % env.ans
      if env.ans == 'y' or env.ans == 'Y':
        #print "*** Starting run_datapatch %s" % ' '.join(env.dblst[rolearg])
        if len(hostlst) >= 2:
          #lock = Lock()
          #func = partial(exec_patch_db_noprompt, lock) # bug fixed in 2.7.5 on wasqltst01, dba01: 2.6.6 got an error
          ### use Pool.map
          if 'wasqlprd02' in hostlst: # remove dg server for datapatch if in hostlst, otherwise wait status in pool worker
            hostlst.remove('wasqlprd02')
          print "datapatch hostlst = %s" % ' '.join(hostlst) # wasqlprd03: channel?? issue why here only, not in tst
          #pool = Pool(len(hostlst))
          pool = ThreadPool(len(hostlst)) # need stty echo 
          try:
            results = pool.map(exec_patch_db_noprompt, hostlst) # return result
            #results = pool.map(func, hostlst)
          finally:
            pool.close()
            pool.join()
            print "*** display SUMMARY results ===================\n\n",
            for item in results:
              #print item
              for h in item:
                print h,':====\n' 
                sum = re.findall(r'Executing .+\r\n|OK Match .+\r\n|PROBLEM .+\r\n', item[h])
                for line in sum:
                  print line
                #print h,':\n', item[h].splitlines()[0],'\n', item[h].splitlines()[-2] # list first and second last lines or [-2:] 
            c.getstatusoutput('stty echo') # reclaim stty echo after ThreadPool running datapatch?!
          #pool.terminate()

        else:
            h = hostlst[0]
            print "*** Starting run_datapatch %s on %s in sigle process" % (' '.join(env.host_dblst[h]), h)
            execute(patch_db,"%s" % ' '.join(env.host_dblst[h]), host=h)
        #execute(patch_db,"%s" % ' '.join(env.dblst[rolearg]), role=rolearg)
        #execute(patch_db,"wapt wahrpt", role=rolearg)
    else:
      print "*** No execution since ans = %s" % env.ans
  else:
     for k in result:
       print "*** CHECK pslst host = %s:\n%s" % (k, result[k]) # exit, manually patch OH/dbs
#===================================================================================
@hosts('wasqlprd01')
def patch_waosu0():
  sudo("/oracledba/jlee/patch/run_datapatch waosu0", user="oracle")
@hosts('wasqlprd03')
def patch_wahrosu0():
  sudo("/oracledba/jlee/patch/run_datapatch wahrosu0", user="oracle")
def dgctl(cmd,*db):
  """ local dgctl off|on|status dblst: dgctl:on|off|status,dblst """
  local("/home/lee.98a/bin/dgctl %s %s" % (cmd, ' '.join(db)) )
def dgctl_off_wa():
  """ dgctl off waosu0 wahrosu0 """
  local("/home/lee.98a/bin/dgctl off waosu0 wahrosu0")
def dgctl_on_wa():
  """ dgctl on waosu0 wahrosu0 """
  local("/home/lee.98a/bin/dgctl on waosu0 wahrosu0")
@parallel
@hosts('wasqlprd01','wasqlprd02','wasqlprd03')
def pslst_waprd():
  run("/oracledba/jlee/pslst")
@parallel
def pslst():
  return run("/oracledba/jlee/pslst") # patchall_pt() uses the result dict
  #run("/oracledba/jlee/pslst")
def chk_alert(*db):
  """ chk_alert:db1,db2,... """
  print "Today's chk_alert log for %s" % (' '.join(db))
  local("/home/lee.98a/bin/chk_alert %s" % (' '.join(db)) )
@parallel
def chk_opatch_ssh(oh,*srv):
  """ chk_opatch_ssh:oh,srv1,srv2,... """
  local("/home/lee.98a/bin/chk_opatch_ssh %s %s" % (oh,' '.join(srv)) )
def chk_opatch_db(*db):
  """ chk_opatch_db:db1,db2,... """
  print "running run_chk_psu12c.sh for %s" % (' '.join(db))
  local("/home/lee.98a/bin/run_chk_psu12c.sh %s" % (' '.join(db)) )
@parallel
def chk_opatch(oh):
  """ use -R or -H chk_opatch:oh [12c|12c_clone|11g_clone] """
  sudo("/oracledba/jlee/patch/chk_opatch_local %s | egrep '^Patch|opatch lsinv'" % oh, user="oracle" )
@parallel
def oemctl(cmd):
  """ oemctl cmd=stop|start|status: oemctl:cmd with -R or -H in parallel"""
  sudo("/oracle/middleware/agent13c/agent_13.1.0.0.0/bin/emctl %s agent" % cmd, user="oracle")
  #sudo("/oracle/middleware/agent12c/bin/emctl %s agent" % cmd, user="oracle")
