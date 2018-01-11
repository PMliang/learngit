#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import os
from common_tools import ConnectDB, SshF5

def getVsName(f5_ip):
    vs_list_all = []
    cmd = 'show ltm virtual all | grep Ltm::Virtual'
    vs_data_all = SshF5(f5_ip, cmd).getssh
    for vs_line_all in vs_data_all.readlines():
        if vs_line_all:
            vs_line = vs_line_all.strip()
            if vs_line.find("Ltm") == 0:
                vs_name = re.split(" +", vs_line)[2]
                vs_list_all.append(vs_name)
    vs_tuple = tuple(vs_list_all)
    return vs_tuple

def getPoolName(f5_ip):
    pool_list_inner = []
    pool_list_outer = []
    vs_tuple = getVsName(f5_ip)
    for vs_name in vs_tuple:
        cmd_pool_name = 'show ltm virtual detail %s | grep Ltm::Pool:' % vs_name
        pool_data_all = SshF5(f5_ip, cmd_pool_name).getssh
        for pool_line_all in pool_data_all.readlines():
            if "| Ltm::Pool:" in pool_line_all:
                # pool_line为获取到的包含pool名称的行
                pool_line = pool_line_all.strip()
                # pool_name为每一个vs所对应的pool的名称
                pool_name = re.split(" +", pool_line)[2]
                pool_list_inner.append(vs_name)
                pool_list_inner.append(pool_name)
                pool_list_outer.append(pool_list_inner)
                pool_list_inner = []
    return pool_list_outer

def getVsState(f5_ip):
    vs_list_outer = []
    for vs_list_inner in getPoolName(f5_ip):
        cmd_vs_state = 'show ltm virtual %s' % vs_list_inner[0]
        vs_state_all = SshF5(f5_ip, cmd_vs_state).getssh
        for vs_state_line_all in vs_state_all.readlines():
            # vs_state_line为状态命令获取到的每一行，以便之后进行数据处理
            vs_state_line = vs_state_line_all.strip()
            # Availability为vs的可用性所在的行
            if "Availability" in vs_state_line:
                # vs_availability为可用性
                vs_availability = re.split(" +", vs_state_line)[2]
                vs_list_inner.append(vs_availability)
            # State为vs的当前状态的行
            elif "State" in vs_state_line:
                # vs_state为当前状态
                vs_state = re.split(" +", vs_state_line)[2]
                vs_list_inner.append(vs_state)
            # Reason为当前所处状态的行
            elif "Reason" in vs_state_line:
                # vs_state_reason为原因
                vs_state_reason = vs_state_line.split(":")[1].strip()
                if "'" in vs_state_reason:
                    vs_state_reason = re.sub("'", "''", vs_state_reason)
                    vs_list_inner.append(vs_state_reason)
                else:
                    vs_list_inner.append(vs_state_reason)
            # Destination为包含VIP和其端口的行
            elif "Destination" in vs_state_line:
                # vs_vip为VIP的地址
                vs_vip = vs_state_line.split(":")[1].strip()
                # vip_port为vs的服务端口
                vip_port = vs_state_line.split(":")[2]
                vs_list_inner.insert(1, vs_vip)
                vs_list_inner.insert(2, vip_port)
            elif "Bits In" in vs_state_line:
                # vs_bits_in为从VIP进入的流量
                vs_bits_in = re.split(" +", vs_state_line)[2]
                vs_list_inner.append(vs_bits_in)
            elif "Bits Out" in vs_state_line:
                # vs_bits_out为流出的数据量
                vs_bits_out = re.split(" +", vs_state_line)[2]
                vs_list_inner.append(vs_bits_out)
            elif "Packets In" in vs_state_line:
                # vs_packets_in为从VIP进入的数据包
                vs_packets_in = re.split(" +", vs_state_line)[2]
                vs_list_inner.append(vs_packets_in)
            elif "Packets Out" in vs_state_line:
                # vs_packets_out为从VIP流出的数据包
                vs_packets_out = re.split(" +", vs_state_line)[2]
                vs_list_inner.append(vs_packets_out)
            elif "Current Connections" in vs_state_line:
                # vs_curr_conn为vs的当前连接数
                vs_curr_conn = re.split(" +", vs_state_line)[2]
                vs_list_inner.append(vs_curr_conn)
            elif "Maximum Connections" in vs_state_line:
                # vs_max_conn为vs的最大连接数
                vs_max_conn = re.split(" +", vs_state_line)[2]
                vs_list_inner.append(vs_max_conn)
            elif "Total Connections" in vs_state_line:
                # vs_total_conn为所有连接
                vs_total_conn = re.split(" +", vs_state_line)[2]
                vs_list_inner.append(vs_total_conn)
        vs_list_inner.insert(0, f5_ip)
        vs_tuple_inner = tuple(vs_list_inner)
        vs_list_outer.append(vs_tuple_inner)
    return vs_list_outer

host = yourhost
port = yourport
username = username
password = password
sid = yoursid
"""
表结构说明：
F5IP：所在F5设备的IP
VSNAME：vs的名称
VIPADDR：VIP地址
VIPPORT：VIP服务端口
POOLNAME：挂在当前vs下面pool的名称
VSAVAILABILITY：vs的可用性
VSSTATE：vs的状态
VSSTATEREASON：处于该状态的原因
VSBITSIN：流入vs的流量
VSBITSOUT：流出vs的流量
VSPACKETSIN：流入vs的数据包
VSPACKETSOUT：流出vs的数据包
VSCURRCONN：vs当前连接数
VSMAXCONN：vs最大连接数
VSTOTALCONN：vs上所有连接数
UPDATETIME：数据的插入时间
"""

create_table = 'CREATE TABLE F5_vs_info (\
F5IP VARCHAR2(30),\
VSNAME VARCHAR2(50),\
VIPADDR VARCHAR2(70) not null,\
VIPPORT VARCHAR2(20) not null,\
POOLNAME VARCHAR2(70),\
VSAVAILABILITY VARCHAR2(60),\
VSSTATE VARCHAR2(30),\
VSSTATEREASON VARCHAR2(200),\
VSBITSIN VARCHAR2(20),\
VSBITSOUT VARCHAR2(20),\
VSPACKETSIN VARCHAR2(20),\
VSPACKETSOUT VARCHAR2(20),\
VSCURRCONN VARCHAR2(20),\
VSMAXCONN VARCHAR2(20),\
VSTOTALCONN VARCHAR2(20),\
UPDATETIME DATE DEFAULT SYSDATE\
)'

insert_data = "INSERT INTO F5_vs_info (F5IP,VSNAME,VIPADDR,VIPPORT,POOLNAME,\
VSAVAILABILITY,VSSTATE,VSSTATEREASON,VSBITSIN,VSBITSOUT,\
VSPACKETSIN,VSPACKETSOUT,VSCURRCONN,VSMAXCONN,VSTOTALCONN) \
values ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"

def insertData():
    conn = ConnectDB(host, port, username, password, sid).getconn
    cursor = conn.cursor()
    cursor.execute(create_table)
    with open('f5_addr.txt', 'r') as f5_ip_all:
        for f5_ip_sour in f5_ip_all.readlines():
            if f5_ip_sour:
                f5_ip = f5_ip_sour.strip()
                vs_tuple_all = tuple(getVsState(f5_ip))
                for vs_tuple in vs_tuple_all:
                    print vs_tuple
                    cursor.execute(insert_data % vs_tuple)
                conn.commit()
    cursor.close()
    conn.close()

if __name__ == '__main__':
    insertData()