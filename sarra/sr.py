#!/usr/bin/env python3
#
# This file is part of sarracenia.
# The sarracenia suite is Free and is proudly provided by the Government of Canada
# Copyright (C) Her Majesty The Queen in Right of Canada, Environment Canada, 2008-2015
#
# Questions or bugs report: dps-client@ec.gc.ca
# sarracenia repository: git://git.code.sf.net/p/metpx/git
# Documentation: http://metpx.sourceforge.net/#SarraDocumentation
#
# sr.py : python3 program starting an environment of sarra processes
#         found under ~/.config/sarra/*
#
#
# Code contributed by:
#  Michel Grenier - Shared Services Canada
#  Last Changed   : Sep 22 10:41:32 EDT 2015
#  Last Revision  : Sep 22 10:41:32 EDT 2015
#
########################################################################
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, 
#  but WITHOUT ANY WARRANTY; without even the implied warranty of 
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307  USA
#
#
import logging, os, os.path, shutil, subprocess, sys, time

try :    
         from sr_config          import *
         from sr_poll            import *
         from sr_post            import *
         from sr_report          import *
         from sr_sarra           import *
         from sr_sender          import *
         from sr_shovel          import *
         from sr_subscribe       import *
         from sr_watch           import *
         from sr_winnow          import *
except : 
         from sarra.sr_config    import *
         from sarra.sr_poll      import *
         from sarra.sr_post      import *
         from sarra.sr_report    import *
         from sarra.sr_sarra     import *
         from sarra.sr_sender    import *
         from sarra.sr_shovel    import *
         from sarra.sr_subscribe import *
         from sarra.sr_watch     import *
         from sarra.sr_winnow    import *

cfg    = sr_config()
action = sys.argv[-1]

#cfg.configure()
#cfg.loglevel = logging.DEBUG
#cfg.setlog()

# instantiate each program  with its configuration file
# and invoke action if one of cleanup,declare,setup

def instantiate(dirconf,pgm,confname,action):

    # c stuff always requiere to spawn a call

    if pgm in ['cpost','cpump'] :
       cfg.logger.debug("%s %s %s" % ("sr_" + pgm,action,confname))
       subprocess.check_call([ "sr_" + pgm, action, confname])
       return

    #print(dirconf,pgm,confname,action)

    config      = re.sub(r'(\.conf)','',confname)
    orig        = sys.argv[0]

    sys.argv[0] = 'sr_' + pgm

    try:
            inst  = None
            cfg.logger.debug("inst %s %s %s" % (pgm,config,action))
            if    pgm == 'poll':      inst = sr_poll     (config,[action])
            elif  pgm == 'post':      inst = sr_post     (config,[action])
            elif  pgm == 'sarra':     inst = sr_sarra    (config,[action])
            elif  pgm == 'sender':    inst = sr_sender   (config,[action])
            elif  pgm == 'shovel':    inst = sr_shovel   (config,[action])
            elif  pgm == 'subscribe': inst = sr_subscribe(config,[action])
            elif  pgm == 'watch':     inst = sr_watch    (config,[action])
            elif  pgm == 'winnow':    inst = sr_winnow   (config,[action])
            elif  pgm == 'report':    inst = sr_report   (config,[action])
            else: 
                  print("code not configured for process type sr_%s" % pgm)
                  sys.exit(1)

            if    action == 'cleanup': inst.cleanup()
            elif  action == 'declare': inst.declare()
            elif  action == 'setup':   inst.setup()

            elif  action == 'remove':  inst.exec_action('remove',False)

            sys.argv[0] = orig

    except:
            print("could not instantiate and run sr_%s %s %s" % (pgm,action,confname))
            sys.exit(1)

      

# invoke each program with its action and configuration file

def invoke(dirconf,pgm,confname,action):

    program = 'sr_' + pgm
    config  = re.sub(r'(\.conf)','',confname)

    try :
             # anything but sr_post
             if program != 'sr_post' :
                cfg.logger.debug("%s %s %s" % (program,action,config))
                subprocess.check_call([program,action,config])
                return

             # sr_post needs -c with absolute confpath

             confpath = dirconf + os.sep + pgm + os.sep + confname
             post = sr_post(confpath)

             cfg.logger.debug("INVOKE %s %s %s %s" % (program,'-c',confpath,action))
             subprocess.check_call([program,'-c',confpath,action])
             return

    except :
             (stype, svalue, tb) = sys.exc_info()
             print("sr/invoke Type: %s, Value: %s" % (stype, svalue))


# check number of config files

def nbr_config(dirconf):
    n = 0

    if not os.path.isdir(dirconf)       : return 0

    for confname in os.listdir(dirconf) :
        if not '.conf' in confname      : continue
        n += 1
 
    return n

# recursive scan of ~/.config/sarra/* , invoking process according to
# the process named from the parent directory

def scandir(dirconf,pgm,action):

    path = dirconf + os.sep + pgm

    if not os.path.isdir(path) : return
    for confname in os.listdir(path) :
        if len(confname) < 5                 : continue
        if not '.conf' in confname[-5:]      : continue
        cfg.logger.info("%s %s %s" % (pgm,confname,action))
        if action in ['cleanup','declare','setup']:
              instantiate(dirconf,pgm,confname,action)
        else:
              invoke(dirconf,pgm,confname,action)


# ===================================
# MAIN
# ===================================

def main():

    # actions supported
    actions_supported = ['start', 'stop', 'status', 'restart', 'reload', 'cleanup', 'declare', 'setup', 'remove']

    # actions extended (actions on config)
    actions_supported.extend( ['list'] )

    actstr = str(actions_supported)
    actstr = actstr.replace(", ","|")

    # validate action
    if len(sys.argv) == 1 or sys.argv[1] not in actions_supported :
       print("USAGE: %s %s (version: %s) " % (sys.argv[0],actstr,sarra.__version__) )
       sys.exit(1)

    action = sys.argv[1]
    config = None

    if len(sys.argv) == 3 : config = sys.argv[2]

    # action list

    if action == 'list' :
       if config :
             result = cfg.find_conf_file(config)
             if  not result :
                 print("no file named %s found in all sarra configs" % config )
                 sys.exit(1)
             cfg.list_file(result)
       else:
             cfg.print_configdir("packaged plugins",           cfg.package_dir     +os.sep+ 'plugins')
             for d in sorted(cfg.programs):
                 cfg.print_configdir("configuration examples", cfg.package_dir     +os.sep+ 'examples' +os.sep+ d)
             cfg.print_configdir("user plugins",               cfg.user_config_dir +os.sep+ 'plugins')
             cfg.print_configdir("general",                    cfg.user_config_dir )
             for d in sorted(cfg.programs):
                 cfg.print_configdir("user configurations",    cfg.user_config_dir + os.sep + d)

       sys.exit(0)

    # sarracenia program that may start without config file
    REPORT_PROGRAMS=['audit']
    for d in REPORT_PROGRAMS:
        pgm = d
        if nbr_config(cfg.user_config_dir+os.sep+d) != 0 :
           scandir(cfg.user_config_dir,pgm,action)
        else :
           cfg.logger.info("%s %s" % ('sr_'+ d,sys.argv[-1]))
           subprocess.check_call(['sr_'+pgm,action])

    for d in cfg.programs:
        pgm = d
        scandir(cfg.user_config_dir,pgm,action)

    sys.exit(0)

# =========================================
# direct invocation
# =========================================

if __name__=="__main__":
   main()
