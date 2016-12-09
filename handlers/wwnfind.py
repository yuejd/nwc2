#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   Jiadi Yue
#   E-mail  :   jiadi.yue@emc.com
#   Date    :   15/08/07 08:22:46
#   Desc    :   wwpn find handler
#

from base import BaseHandler
import sys
sys.path.append("..")
from lib.config import nodefind_switches

class WwnfindHandler(BaseHandler):
    def get(self):
        self.render("wwnfind.html")
    def post(self):
        wwn = self.get_argument("wwn")
        from lib.nodefind import wwn_nodefind
        rtn_nodefind = wwn_nodefind(wwn, nodefind_switches)
        print rtn_nodefind
        if rtn_nodefind:
            self.write(self.render_string("wwnfindresult.html",
                                          wwn = rtn_nodefind))
        else:
            self.write("<div class='alert alert-success' role='alert'>" + "no wwn find "+ "</div>")

routes = [
    (r"/wwnfind", WwnfindHandler)
]
