#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import cx_Oracle
"""
主要定义了一些常用的类
1、连接中间件qhinfo库的类：ConnectDB，其中的方法都可以以属性的形式进行调用，可以使用默认的属性，也可以修改属性值
2、连接F5并执行命令的类，返回执行shell脚本的结果
"""
class ConnectDB():
    def __init__(self, host, port, username, password, sid):
        self.__host = host
        self.__port = port
        self.__username = username
        self.__password = password
        self.__sid = sid
    @property
    def getconn(self):
        tns = cx_Oracle.makedsn(self.__host, self.__port, self.__sid)
        conn = cx_Oracle.connect(self.__username, self.__password, tns)
        return conn

class SshF5():
    def __init__(self, f5_ip, cmd):
        self.f5_ip = f5_ip
        self.cmd = cmd

    @property
    def getssh(self):
        source_data = os.popen("sh vs_f5.sh %s \"%s\"" % (self.f5_ip, self.cmd))
        return source_data