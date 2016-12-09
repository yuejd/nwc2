#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   Jiadi Yue
#   E-mail  :   jiadi.yue@emc.com
#   Date    :   15/04/17 13:36:29
#   Desc    :   base handler
#

import tornado.web
import sys
sys.path.append("..")
from db.model import nwcdb

class BaseHandler(tornado.web.RequestHandler):
    def on_finish(self):
        if not nwcdb.is_closed():
            nwcdb.close()
