#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   Jiadi Yue
#   E-mail  :   jiadi.yue@emc.com
#   Date    :   15/04/21 00:12:03
#   Desc    :   zone handler
#

from base import BaseHandler
import sys
sys.path.append("..")
from lib.config import nodefind_switches, switches_fab
from lib.utils import trans_wwn

class ZoneHandler(BaseHandler):
    def get(self):
        self.render("zone.html")
    def post(self):
        zonename = self.get_argument("zonename")
        wwns = self.get_argument("wwns")
        fid_vsan = self.get_argument("fid_vsan")
        def trans_wwns(wwn):
            return trans_wwn(wwn.strip())
        
        zonename = zonename.strip()
        wwns = map(trans_wwns, wwns.split(";"))
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
            from lib.nwc_lib import zone_cis
            zone_func = zone_cis
        else:
            vsan = None
            from lib.nwc_lib import zone_brc
            zone_func = zone_brc
        
        rtn_zone = zone_func(switch_ip, switch_user, switch_passwd, zonename, wwns, fabric, vsan)
        if rtn_zone:
            if rtn_zone[0]:
                div_class = "success"
                result = "zone success."
            else:
                div_class = "warning"
                result = "zone failed."
            self.write(self.render_string("zoneresult.html", div_class = div_class, result = result, log = rtn_zone[1]))
        else:
            self.write("<div class='alert alert-danger' role='alert'>" + "zone failed, please check the switch." + "</div>")

routes = [
    (r"/zone", ZoneHandler)
]
