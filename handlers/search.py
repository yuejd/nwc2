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
        checkbox = {}
        checkbox["fid40"] = self.get_argument("fid40chk")
        checkbox["fid5"] = self.get_argument("fid5chk")
        checkbox["fid10"] = self.get_argument("fid10chk")
        checkbox["fid98"] = self.get_argument("fid98chk")
        checkbox["fid100"] = self.get_argument("fid100chk")
        checkbox["vsan5"] = self.get_argument("vsan5chk")
        checkbox["vsan6"] = self.get_argument("vsan6chk")
        search_fabric = [fabric for fabric, is_checked in checkbox.iteritems() if is_checked == "true" ]
        print checkbox
        print search_fabric
        fabric_list = map(lambda x, y: x+y, switches_info, nodefind_switches)
        #from lib.nodefind import server_nodefind
        #rtn_nodefind = server_nodefind(ip, username, passwd, devtype, nodefind_switches)
        #print rtn_nodefind
        #if rtn_nodefind:
        #    self.write(self.render_string("nodefindresult.html",
        #                                  wwns = rtn_nodefind))
        #else:
        #    self.write("<div class='alert alert-success' role='alert'>" + "no wwns find, please check your hosts" + "</div>")
        self.write("<div class='alert alert-success' role='alert'>" + "search test" + "</div>")

routes = [
    (r"/search", SearchHandler)
]
