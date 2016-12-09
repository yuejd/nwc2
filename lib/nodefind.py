#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   Jiadi Yue
#   E-mail  :   jiadi.yue@emc.com
#   Date    :   15/04/16 06:57:19
#   Desc    :   find server node in switch online
#

import nwc_lib
import threading
from utils import trans_wwn
from config import printd

class Nodefind(threading.Thread):
    def __init__(self, ip, username, password, sw_type, wwns, connections):
        threading.Thread.__init__(self)
        self.ip = ip
        self.username = username
        self.password = password
        self.wwns = wwns
        self.connections = connections
        if sw_type == "cisco":
            self.nodefind = nwc_lib.nodefind_cis
        elif sw_type == "brocade":
            self.nodefind = nwc_lib.nodefind_brc
        else:
            printd("%s - %s: device type not support nodefind \n" % (ip, sw_type))
            return
    def run(self):
        rtn = self.nodefind(self.ip, self.username, self.password, self.wwns)
        if rtn:
            for i in xrange(len(rtn)):
                if len(self.connections[i]) < 4 and rtn[i]:
                    self.connections[i].extend(rtn[i])
        else:
            return

def server_nodefind(ser_ip, ser_username, ser_password, dev_type, switches):
    if dev_type == "linux":
        get_wwn = nwc_lib.get_linux_wwn
    elif dev_type == "solaris":
        get_wwn = nwc_lib.get_solaris_wwn
    elif dev_type == "vmware":
        get_wwn = nwc_lib.get_vmware_wwn
    elif dev_type == "hpux":
        get_wwn = nwc_lib.get_hpux_wwn
    elif dev_type == "aix":
        get_wwn = nwc_lib.get_aix_wwn
    else:
        printd("%s - %s: device type not support server_nodefind \n" % (ser_ip, dev_type))
        return
    wwns = get_wwn(ser_ip, ser_username, ser_password)
    if wwns:
        single_wwns = [wwn[0] for wwn in wwns]
        node_connections = [list(wwn) for wwn in wwns]
        # to store the return value of thread
        nodefind_threads = []
        for switch in switches:
            t = Nodefind(*(switch + [single_wwns, node_connections]))
            nodefind_threads.append(t)
        for t in nodefind_threads:
            t.start()
        for t in nodefind_threads:
            t.join(30)
        return node_connections

def wwn_nodefind(wwn, switches):
    wwn = [trans_wwn(wwn)]
    #return nwc_lib.nodefind_brc(*(switches[0][0:3] + [wwn]))
    nodefind_threads = []
    for switch in switches:
        t = Nodefind(*(switch + [wwn, [wwn]]))
        nodefind_threads.append(t)
    for t in nodefind_threads:
        t.start()
    for t in nodefind_threads:
        t.join(30)
    return wwn


if __name__ == "__main__":
    from tornado.options import define, options
    define("wwn", help = "wwn to find")
    options.parse_command_line()
    # would print ssh info if add above lines
    from config import nodefind_switches
    #print server_nodefind("10.103.118.119", "root", "dangerous", "hpux", nodefind_switches)
    #print server_nodefind("10.108.106.71", "root", "#1Danger0us", "linux", nodefind_switches)
    #print server_nodefind("10.108.119.72", "root", "1bmaix", "aix", nodefind_switches)
    #print server_nodefind("10.103.118.153", "root", "dangerous", "hpux", nodefind_switches)
    #print server_nodefind("10.108.106.99", "root", "#1Danger0us", "linux", nodefind_switches)
    #print wwn_nodefind("21:00:00:0e:1e:09:fg:bd", nodefind_switches)
    #import pdb
    #pdb.set_trace()
    #print wwn_nodefind("50:06:01:6c:08:e0:10:b0", nodefind_switches)
    if options.wwn:
        print wwn_nodefind(options.wwn, nodefind_switches)

