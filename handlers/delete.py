#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   Jiadi Yue
#   E-mail  :   jiadi.yue@emc.com
#   Date    :   16/12/09 09:56:20
#   Desc    :   delete zone handler
#


from base import BaseHandler
import sys
sys.path.append("..")
from lib.config import nodefind_switches, switches_fab
from lib.utils import trans_wwn

class DeleteZoneHandler(BaseHandler):
    def get(self):
        self.render("delete.html")
    def post(self):
        zonename = self.get_argument("zonename")
        fid_vsan = self.get_argument("fid_vsan")
        
        zonename = zonename.strip()
        for fab_info in switches_fab:
            if fab_info[0] == fid_vsan:
                fabric = fab_info[2]
                switch_ip = fab_info[1]
                break
            else: continue
        for switch in nodefind_switches:
            if switch[0] == switch_ip:
                switch_user = switch[1]
                switch_passwd = switch[2]
                switch_type = switch[3]
                break
            else: continue

        if "cisco" == switch_type:
            vsan = fid_vsan[4:]
            from lib.nwc_lib import del_zone_cis
            del_zone_func = del_zone_cis
        else:
            vsan = None
            from lib.nwc_lib import del_zone_brc
            del_zone_func = del_zone_brc
        
        rtn_del_zone = del_zone_func(switch_ip, switch_user, switch_passwd, zonename, fabric, vsan)
        if rtn_del_zone:
            if rtn_del_zone[0]:
                div_class = "success"
                result = "delete zone success."
            else:
                div_class = "warning"
                result = "delete zone failed."
            self.write(self.render_string("zoneresult.html", div_class = div_class, result = result, log = rtn_del_zone[1]))
        else:
            self.write("<div class='alert alert-danger' role='alert'>" + "delete zone failed, please check the switch." + "</div>")

routes = [
    (r"/delete", DeleteZoneHandler)
]
