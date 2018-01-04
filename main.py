#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   Jiadi Yue
#   E-mail  :   jiadi.yue@emc.com
#   Date    :   15/04/17 13:14:19
#   Desc    :   main app
#

import tornado.httpserver
import tornado.ioloop
import tornado.web
import os
import sys


class Application(tornado.web.Application):
    def __init__(self):
        settings = dict(
            blog_title = u"NWC WEB V2",
            template_path = os.path.join(os.path.dirname(__file__), "templates"),
            static_path = os.path.join(os.path.dirname(__file__), "static"),
            #ui_modules = {"Entry1": EntryModule, "topx": TopXModule},
            #xsrf_cookies = True,
            #cookie_secret = "tjNXzvzDSOeNZucdZsW9KvmBAmTCH0a0okEyJCeA7EQ=",
            debug = True,
            #login_url = "/login"
        )
        from urls import routes as handlers
        tornado.web.Application.__init__(self, handlers, **settings)


def main(port = 8888):
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(int(sys.argv[1]))
    else:
        main()
