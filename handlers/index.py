#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   Jiadi Yue
#   E-mail  :   jiadi.yue@emc.com
#   Date    :   15/04/20 23:13:04
#   Desc    :   Index handler
#
from base import BaseHandler

class IndexHandler(BaseHandler):
    def get(self):
        self.render("index.html")



routes = [
    (r"/", IndexHandler)
]
