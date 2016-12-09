#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   Jiadi Yue
#   E-mail  :   jiadi.yue@emc.com
#   Date    :   15/01/26 13:26:54
#   Desc    :   nwc database model for peewee
#

from peewee import *
DB_NAME = "nwc.db"

nwcdb = SqliteDatabase(DB_NAME, threadlocals=True)

class BaseModel(Model):
    class Meta:
        database = nwcdb

class ServerInfo(BaseModel):
    ipaddr = CharField()
    hostname = CharField()
    username = CharField()
    password = CharField()
    devtype = CharField()
    model = CharField(null=True)
    vender = CharField(null=True)
    cpu = CharField(null=True)
    memory = CharField(null=True)
    os = CharField(null=True)
    reserver = CharField(null=True)
    #release_date = CharField(null=True)
    comment = CharField(null=True)
    mdf_time = DateTimeField(null=True)

class ArrayInfo(BaseModel):
    ipaddr = CharField()
    hostname = CharField()
    username = CharField()
    password = CharField()
    devtype = CharField()
    model = CharField(null=True)
    mdf_time = DateTimeField(null=True)

class SwitchInfo(BaseModel):
    ipaddr = CharField()
    hostname = CharField()
    username = CharField()
    password = CharField()
    devtype = CharField()
    switchname = CharField(null=True)
    fabric_id = CharField(null=True)
    model = CharField(null=True)
    mdf_time = DateTimeField(null=True)

class Fabric(BaseModel):
    type = CharField()
    fabric_id = IntegerField()

class NodeWWN(BaseModel):
    wwpn = CharField()
    status = CharField()
    #hostname = CharField()
    #ipaddr = CharField()
    hba_info = CharField()
    mdf_time = DateTimeField(null=True)
    host = ForeignKeyField(ServerInfo)

class SwitchWWN(BaseModel):
    wwpn = CharField()
    #ipaddr = CharField()
    switchport = CharField()
    fc_oe = CharField()
    fabric_id = CharField(null=True)
    mdf_time = DateTimeField(null=True)
    switch = ForeignKeyField(SwitchInfo)
