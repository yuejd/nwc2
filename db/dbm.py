#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   Jiadi Yue
#   E-mail  :   jiadi.yue@emc.com
#   Date    :   15/01/26 13:33:26
#   Desc    :   nwc database manager
#

import sys
sys.path.append("..")
import model
from tornado.options import define,options
from lib.utils import find_subclasses
from lib.config import *
from datetime import datetime

define("cmd", default = "syncdb", help = "command for nwc")
define("path", help = "file path with server/switch/array information")
define("ip", help = "ip address")
#python dbm.py --cmd=syncdb to recreate db

def syncdb():
    """
    to clean tables or recreate tables
    """
    mods = find_subclasses(model.BaseModel)
    for mod in mods:
        if mod.table_exists():
            mod.drop_table()
        mod.create_table()
        printd("created table: " + mod._meta.db_table + "\n")

def insert_from_file(file_path, tb = "server"):
    """
    insert server/switch/array info into table from credential file.
    file format:
    ipaddr, username, password, devtype, hostname 
    """
    with open(file_path, "r") as info_file:
        for info in info_file:
            ipaddr, username, password, devtype, hostname = info.strip().split()
            insert_server(ipaddr, hostname, username, password, devtype, scan = True, tb = tb)

def scan_server_wwn(ipaddr, server_info = None):
    """
    scan server wwns and flash into database
    """
    try:
        if not server_info:
            new_server = False
            server_info = model.ServerInfo.get(model.ServerInfo.ipaddr == ipaddr)
        else:
            new_server = True
        devtype = server_info.devtype.lower()
        if devtype == "linux":
            from lib.nwc_lib import get_linux_wwn as get_wwn
        elif devtype == "solaris":
            from lib.nwc_lib import get_solaris_wwn as get_wwn
        elif devtype == "vmware":
            from lib.nwc_lib import get_vmware_wwn as get_wwn
        else:
            printd("%s: device type not support auto-scan wwns \n" % ipaddr)
            return
        wwns = get_wwn(server_info.ipaddr, server_info.username, server_info.password)
        if wwns:
            del_server_wwn(ipaddr, server_info = server_info, simple_del = False)
            for wwn in wwns:
                model.NodeWWN.create(wwpn = wwn[0], hba_info = wwn[1], status = wwn[2],
                                     host = server_info, mdf_time = datetime.now())
            return True
    except Exception as ex:
        printd("%s: scan server wwn with issue: %s \n" % (ipaddr, ex.message))

def del_server_wwn(ipaddr, server_info = None, simple_del = True ):
    """
    delete server wwns from database
    """
    try:
        if not server_info:
            server_info = model.ServerInfo.get(model.ServerInfo.ipaddr == ipaddr)
        wwns = model.NodeWWN.select().where(model.NodeWWN.host == server_info)
        for wwn in wwns:
            wwn.delete_instance()
        if simple_del:
            printd("%s: delete server wwns successful\n" % ipaddr)
        return True
    except Exception as ex:
        if simple_del:
            printd("%s: delete server wwn not successful: %s \n" % (ipaddr, ex.message))

def scan_server_dev(ipaddr, server_info = None):
    """
    scan server info and flash into database
    """
    try:
        if not server_info:
            new_server = False
            server_info = model.ServerInfo.get(model.ServerInfo.ipaddr == ipaddr)
        else:
            new_server = True
        devtype = server_info.devtype.lower()
        if devtype == "linux":
            from lib.nwc_lib import get_linux_info as get_info
        elif devtype == "solaris":
            from lib.nwc_lib import get_solaris_info as get_info
        elif devtype == "vmware":
            from lib.nwc_lib import get_vmware_info as get_info
        else:
            printd("%s: device type not support auto-scan information \n" % ipaddr)
            return
        info_list = get_info(server_info.ipaddr, server_info.username, server_info.password)
        if info_list:
            server_info.vender = info_list[1]
            server_info.model = info_list[0]
            server_info.cpu = info_list[2]
            server_info.memory = info_list[3]
            #if len(info_list) == 5:
            #    server_info.os = info_list[4]
            server_info.os = info_list[4]
            server_info.mdf_time = datetime.now()
            server_info.save()
            if not new_server:
                printd("%s: rescan dev info successful\n" % ipaddr)
            return True
        else:
            printd("%s: not get dev info while update server dev \n" % ipaddr)
    except Exception as ex:
        printd("%s: update server dev with issues: %s \n" % (ipaddr, ex.message))

def insert_server(ipaddr, hostname, username, password, \
        devtype, tb = "server", scan = False):
    """
    insert a credential info of server/switch/array into databash
    if scan is True, will scan for wwn... info and add to db.
    """
    if tb == "array":
        nwc_model = model.ArrayInfo
    elif tb == "switch":
        nwc_model = model.SwitchInfo
    else:
        nwc_model = model.ServerInfo
    try:
        nwc_model.get((nwc_model.hostname == hostname) & (nwc_model.username == username))
        printd("%s: %s already exists in database" % (hostname, tb))
    except nwc_model.DoesNotExist:
        info = nwc_model.create(ipaddr = ipaddr, hostname = hostname, \
                                username = username, password = password, \
                                devtype = devtype)
        if scan and tb == "server":
            ret = scan_server_dev(ipaddr, info)
            if ret:
                printd("%s: insert server info \n" % ipaddr)
            ret = scan_server_wwn(ipaddr, info)
            if ret:
                printd("%s: insert server wwn \n" % ipaddr)
        elif scan and tb == "switch":
            ret = scan_switch(ipaddr, info)
            if ret:
                printd("%s: insert switch wwn \n" % ipaddr)

def update_server_credential(ipaddr, hostname, username, password,\
        devtype, reserver = None, comment = None):
    """
    """
    try:
        server_info = model.ServerInfo.get(model.ServerInfo.hostname == hostname)
        server_info.ipaddr = ipaddr
        server_info.username = username
        server_info.password = password
        server_info.devtype = devtype
        server_info.reserver = reserver
        server_info.comment = comment
        server_info.save()
        printd("%s: update server info with credential\n" % hostname)
    except:
        printd("%s: update server info with credential not successful\n" % hostname)

def del_server(ipaddr):
    """
    delete server and it's wwns from db
    """
    try:
        server_info = model.ServerInfo.get(model.ServerInfo.ipaddr == ipaddr)
        del_server_wwn(ipaddr, server_info)
        server_info.delete_instance()
        printd("%s: server %s information delete from database\n" % (ipaddr, server_info.hostname))
    except:
        printd("%s: server information delete not successful\n" % hostname)

def del_switch(ipaddr):
    try:
        switchs = model.SwitchInfo.select().where(model.SwitchInfo.ipaddr == ipaddr)
        for switch in switchs:
            del_switch_wwn(ipaddr, switch)
            switch.delete_instance()
        printd("%s: switch %s information delete from database\n" % (ipaddr, switch.hostname))
    except:
        printd("%s: switch information delete with issues\n" % hostname)

def del_switch_wwn(ipaddr, switch, simple_del = True):
    """
    delete switch wwns from database
    """
    try:
        if not switch:
            switch = model.SwitchInfo.get(model.SwitchInfo.ipaddr == ipaddr)
        wwns = model.SwitchWWN.select().where(model.SwitchWWN.switch == switch)
        for wwn in wwns:
            wwn.delete_instance()
        if simple_del:
            printd("%s: delete switch wwns successful\n" % ipaddr)
        return True
    except Exception as ex:
        if simple_del:
            printd("%s: delete switch wwn with issues: %s \n" % (ipaddr, ex.message))

def scan_switch(ipaddr, switch = None):
    """
    scan switch info/wwn and update db
    """
    try:
        if not switch:
            new_switch = False
            switch = model.SwitchInfo.get(model.SwitchInfo.ipaddr == ipaddr)
        else:
            new_switch = True
        devtype = switch.devtype.lower()
        if "brocade" in devtype:
            from lib.nwc_lib import get_brocade_info as get_info
        elif "cisco" in devtype:
            from lib.nwc_lib import get_cisco_info as get_info
        else:
            printd("%s: switch type not support auto-scan information \n" % ipaddr)
            return
        info_list = get_info(switch.ipaddr, switch.username, switch.password)
        if info_list:
            switch.switchname = info_list[0]
            switch.fabric_id = info_list[1]
            switch.save()
            del_switch_wwn(ipaddr, switch, simple_del = False)
            for wwn in info_list[2]:
                model.SwitchWWN.create(switchport = wwn[0],
                                       fc_oe = wwn[1],
                                       fabric_id = wwn[2],
                                       wwpn = wwn[3],
                                       mdf_time = datetime.now(),
                                       switch = switch)
            return True
    except Exception as ex:
        printd("%s: scan switch with issues: %s \n" % (ipaddr, ex.message))

if __name__ == '__main__':
    options.parse_command_line()
    if options.cmd == "syncdb":
        syncdb()
    elif options.cmd == "insert_server":
        if options.path:
            insert_from_file(options.path)
        else:
            printd("need to add --path=/your/path/to/file option")
    elif options.cmd == "insert_switch":
        if options.path:
            insert_from_file(options.path, tb = "switch")
        else:
            printd("need to add --path=/your/path/to/file option")
    elif options.cmd == "rescan_server":
        if options.ip:
            scan_server_dev(options.ip)
            scan_server_wwn(options.ip)
        else:
            printd("need to add option --ip=ip address")
    elif options.cmd == "rescan_switch":
        if options.ip:
            scan_switch(options.ip)
        else:
            printd("need to add option --ip=ip address")
    elif options.cmd == "delete_server":
        if options.ip:
            del_server(options.ip)
        else:
            printd("need to add option --ip=ip address")
    elif options.cmd == "delete_switch":
        if options.ip:
            del_switch(options.ip)
        else:
            printd("need to add option --ip=ip address")
