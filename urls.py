#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   Jiadi Yue
#   E-mail  :   jiadi.yue@emc.com
#   Date    :   15/04/17 15:27:24
#   Desc    :   handler map to urls
#

from handlers import index, nodefind, wwnfind, zone, search, delete

routes = []
routes.extend(index.routes)
routes.extend(nodefind.routes)
routes.extend(wwnfind.routes)
routes.extend(zone.routes)
routes.extend(search.routes)
routes.extend(delete.routes)
