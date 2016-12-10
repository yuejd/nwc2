#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   Jiadi Yue
#   E-mail  :   jiadi.yue@emc.com
#   Date    :   15/01/19 00:19:31
#   Desc    :   configuration for library
#               method printd message
#
from datetime import datetime

NORMAL = 0
DEBUG = 1
LOG = 2
Division = "@#$"

#NORMAL mode: the same as print to stdout
#DEBUG mode: print message to debug log file and stdout with date time stamp
#LOG mode: print message to debug log file with date time stamp
LOG_EVENT = DEBUG

def print_nor(msg):
    print msg

def print_debug(msg):
    prt_msg = print_log(msg)
    print prt_msg

def print_log(msg):
    now = datetime.now()
    dt_stamp = now.strftime('%Y%m%d %H:%M:%S - ')
    prt_msg = dt_stamp + msg
    debug_log = open("./debug.log", "a")
    debug_log.write(prt_msg)
    debug_log.close()
    return prt_msg


if LOG_EVENT == NORMAL:
    printd = print_nor
elif LOG_EVENT == DEBUG:
    printd = print_debug
elif LOG_EVENT == LOG:
    printd = print_log

# switches for nodefind
nodefind_switches = (["10.108.104.124", "user_platform", "password", "brocade"], #fid40
                      ["10.108.104.123", "user_vplexa", "password", "brocade"], #fid5
                      ["10.108.178.95", "adminA", "Elab0123", "brocade"], #HP fid5 for zone
                      ["10.108.104.122", "user_vplexb", "password", "brocade"], #fid10
                      ["10.108.178.94", "adminB", "Elab0123", "brocade"], #HP fid10 for zone
                      ["10.108.104.121", "user_symmetrix", "password", "brocade"], #fid128 in x86
                      ["10.108.179.35", "admin", "Elab0123", "brocade"], #fid128 in unix for zone
                      ["10.103.116.49", "cd", "password", "brocade"], #fid98
                      ["10.108.179.33", "hp", "password", "brocade"], #fid100
                      ["10.108.104.13", "emc", "Emc12345", "cisco"], #cisco x86
                      ["10.108.104.14", "emc", "Emc12345", "cisco"], #cisco x86
                      ["10.103.116.38", "emc", "Emc12345", "cisco"], #cisco aix vsan 110
                      ["10.108.178.27", "emc", "Emc12345", "cisco"], #cisco hp 100
                      ["10.108.238.32", "admin", "Elabxha2016", "cisco"], #cisco xha
                      ["10.108.238.29", "admin", "Elabxha2016", "cisco"], #cisco xha
                      ["10.108.238.21", "admin", "Elabxha2016", "brocade"], #brocade xha
                      ["10.246.51.213", "emc", "Emc12345", "cisco"], #cisco lab10
                      ["10.103.116.33", "admin", "2baerosmith", "cisco"]) #cisco hp vsan 1

# switches information
switches_fab = (["fid40", "10.108.104.124", "PLATFORM_SILO", "x86"],
                 ["fid5", "10.108.178.95", "BRCD_INV_FabricA", "core VPLEXA"],
                 ["fid10", "10.108.178.94", "INV_VPLEX_Fabric_B", "core VPLEXB"],
                 ["fid128", "10.108.179.35", "Brcd_Large_Symm", "core SYMMETRIX"],
                 ["fid98", "10.103.116.49", "Brocade_fabric", "cd fabric"],
                 ["fid100", "10.108.179.33", "HPQ_cfg", "hp fabric"],
                 ["vsan5", "10.108.104.14", "VPLEX-A", "core cisco vsan 5"],
                 ["vsan6", "10.108.104.14", "VPLEX-B", "core cisco vsan 6"],
                 ["vsan2140", "10.108.104.14", "WLSV_SILO_A", "x86 cisco vsan 2140"],
                 ["vsan20", "10.108.238.29", "RP_Large", "ibm xha vsan 20"],
                 ["vsan100", "10.108.178.27", "Fabric-A", "hp vsan 100"],
                 ["vsan110", "10.103.116.38", "eLabIBM", "ibm vsan 110"],
                 ["vsan143", "10.108.238.29", "xHA_HPQ_Durham", "xha vsan 143"],
                 ["fid101", "10.108.238.21", "xHA_HQP_Durham", "xha fid101"],
                 ["vsan80", "10.246.51.213", "NDM", "lab10 vsan80"])
