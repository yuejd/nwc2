#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   Jiadi Yue
#   E-mail  :   jiadi.yue@emc.com
#   Date    :   15/01/26 13:36:52
#   Desc    :   some utilities for nwc
#

import os
import signal
import time
import re

def find_subclasses(klass, include_self=False):
    accum = []
    for child in klass.__subclasses__():
        accum.extend(find_subclasses(child, True))
    if include_self:
        accum.append(klass)
    return accum

def trans_wwn(wwn):
    if len(wwn) == 18 and "0x" == wwn[0:2]:
        wwn = wwn[2:]
    if len(wwn) == 16 and re.search(r"[a-fA-F0-9]{16}", wwn):
        wwn = wwn.lower()
        return ":".join([x+y for x, y in zip(wwn[::2], wwn[1::2])])
    else:
        return wwn.lower()

def get_file_names(file_path, inner):
    source_file = os.listdir(file_path)
    return filter(lambda x:x.find(inner) >= 0, source_file)
 
class Timeout():
    """Timeout class using ALARM signal."""
    class Timeout(Exception):
        message = "nwc paramiko ssh connect timeout"
        pass
 
    def __init__(self, sec):
        self.sec = sec
 
    def __enter__(self):
        signal.signal(signal.SIGALRM, self.raise_timeout)
        signal.alarm(self.sec)
 
    def __exit__(self, *args):
        signal.alarm(0)    # disable alarm
 
    def raise_timeout(self, *args):
        raise Timeout.Timeout()
 
