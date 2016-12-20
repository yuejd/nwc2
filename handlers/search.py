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

class SearchHandler(BaseHandler):
    def get(self):
        self.render("search.html")
    def post(self):
        keyword = self.get_argument("keyword")
        fid_vsan = self.get_argument("fid_vsan")

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
            from lib.nwc_lib import zone_search_cis
            zone_search_func = zone_search_cis
        else:
            vsan = None
            from lib.nwc_lib import zone_search_brc
            zone_search_func = zone_search_brc
        
        rtn_zone_search = zone_search_func(switch_ip, switch_user, switch_passwd, keyword, vsan)
        if rtn_zone_search:
            print "=========================###################search finished################+++++++++++++++++++++++++++++++++"
            self.write(self.render_string("zonesearchresult.html",
                                          zones = rtn_zone_search))
        else:
            self.write("<div class='alert alert-danger' role='alert'>" + "no zone found, please check the switch" + "</div>")


routes = [
    (r"/search", SearchHandler)
]
