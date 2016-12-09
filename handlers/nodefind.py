#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   Jiadi Yue
#   E-mail  :   jiadi.yue@emc.com
#   Date    :   15/04/21 00:12:03
#   Desc    :   NodeFind handler
#

from base import BaseHandler
import sys
sys.path.append("..")
from lib.config import nodefind_switches

class NodefindHandler(BaseHandler):
    def get(self):
        self.render("nodefind.html")
    def post(self):
        ip = self.get_argument("ipaddr")
        username = self.get_argument("username")
        passwd = self.get_argument("passwd")
        devtype = self.get_argument("devtype")
        from lib.nodefind import server_nodefind
        rtn_nodefind = server_nodefind(ip, username, passwd, devtype, nodefind_switches)
        print rtn_nodefind
        if rtn_nodefind:
            self.write(self.render_string("nodefindresult.html",
                                          wwns = rtn_nodefind))
        else:
            self.write("<div class='alert alert-success' role='alert'>" + "no wwns find, please check your hosts" + "</div>")

routes = [
    (r"/nodefind", NodefindHandler)
]
