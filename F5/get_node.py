#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
import os
from common_tools import ConnectDB, SshF5
from get_vs import getPoolName

def getNodeName(f5_ip):
    node_list_inner = []
    node_list_outer = []
    for pool_name_all in getPoolName(f5_ip):
        # 此命令是找出每一个pool里面包含的节点的名称和端口信息
        cmd = 'show ltm pool detail %s | grep "Ltm::Pool Member:"' % pool_name_all[1]
        node_data_all = SshF5(f5_ip, cmd).getssh
        for node_line_all in node_data_all.readlines():
            node_line_all = node_line_all.strip()
            if "| Ltm::Pool" in node_line_all:
                # node_name为节点的名称
                node_name = node_line_all.split(":")[3].strip()
                # node_port为节点的服务端口
                node_port = node_line_all.split(":")[4]
                node_list_inner.append(f5_ip)
                node_list_inner.append(pool_name_all[1])
                node_list_inner.append(node_name)
                node_list_inner.append(node_port)
                node_list_outer.append(node_list_inner)
                node_list_inner = []
    print node_list_outer
    # 返回一个包含所有节点名称信息的列表
    return node_list_outer

def getNodeState(f5_ip):
    node_list_outer = []
    pool_list_all = getNodeName(f5_ip)
    for node_list_inner in pool_list_all:
        # 显示每个节点的详细信息，包括流量等信息
        cmd = 'show ltm node %s' % node_list_inner[2]
        state_data_all = SshF5(f5_ip, cmd).getssh
        for state_line_all in state_data_all.readlines():
            if state_line_all:
                state_line_all = state_line_all.strip()
                if "Ltm::Node:" in state_line_all:
                    # node_addr为节点的IP地址
                    node_addr = state_line_all.split(" ")[2][1:-1]
                    node_list_inner.insert(3, node_addr)
                elif "Availability" in state_line_all:
                    # node_availability为节点的可用性
                    node_availability = state_line_all.split(":")[1].strip()
                    node_list_inner.append(node_availability)
                elif "State" in state_line_all:
                    # node_state为节点的状态
                    node_state = state_line_all.split(":")[1].strip()
                    node_list_inner.append(node_state)
                elif "Reason" in state_line_all:
                    # state_reason为该状态的原因
                    state_reason = state_line_all.split(":")[1].strip()
                    node_list_inner.append(state_reason)
                elif "Monitor" in state_line_all:
                    # node_monitor为节点监听器
                    node_monitor = state_line_all.split(":")[1].strip()
                    node_list_inner.append(node_monitor)
                elif "Monitor Status" in state_line_all:
                    # node_mon_status为节点监听器状态
                    node_mon_status = state_line_all.split(":")[1].strip()
                    node_list_inner.append(node_mon_status)
                elif "Session Status" in state_line_all:
                    # node_session_status为节点会话状态
                    node_session_status = state_line_all.split(":")[1].strip()
                    node_list_inner.append(node_session_status)
                elif "Bits In" in state_line_all:
                    # node_bits_in为流入节点的流量
                    node_bits_in = re.split(" +", state_line_all)[2]
                    node_list_inner.append(node_bits_in)
                elif "Bits Out" in state_line_all:
                    # node_bits_out为流出节点的流量
                    node_bits_out = re.split(" +", state_line_all)[2]
                    node_list_inner.append(node_bits_out)
                elif "Packets In" in state_line_all:
                    # node_packets_in为节点上流入的数据包
                    node_packets_in = re.split(" +", state_line_all)[2]
                    node_list_inner.append(node_packets_in)
                elif "Packets Out" in state_line_all:
                    # node_packets_out为节点上流出的数据包
                    node_packets_out = re.split(" +", state_line_all)[2]
                    node_list_inner.append(node_packets_out)
                elif "Current Connections" in state_line_all:
                    # node_cur_conn为该节点的当前连接数
                    node_cur_conn = re.split(" +", state_line_all)[2]
                    node_list_inner.append(node_cur_conn)
                elif "Maximum Connections" in state_line_all:
                    # node_max_conn为该节点最大连接数
                    node_max_conn = re.split(" +", state_line_all)[2]
                    node_list_inner.append(node_max_conn)
                elif "Total Connections" in state_line_all:
                    # node_total_conn为该节点所有连接数
                    node_total_conn = re.split(" +", state_line_all)[2]
                    node_list_inner.append(node_total_conn)
                elif "Total Requests" in state_line_all:
                    # node_total_request为该节点所有的连接请求数
                    node_total_request = re.split(" +", state_line_all)[3]
                    node_list_inner.append(node_total_request)
                elif "Current Sessions" in state_line_all:
                    # node_cur_session为该节点当前的会话数
                    node_cur_session = re.split(" +", state_line_all)[3]
                    node_list_inner.append(node_cur_session)
        print node_list_inner
        node_list_outer.append(tuple(node_list_inner))
    return tuple(node_list_outer)


host = 'qhinfoprd.db.foresealife.com'
port = 1521
username = 'midwaredata'
password = 'midwaredata'
sid = 'qhinfo'


"""
表结构说明：
F5IP：所在F5设备的IP
POOLNAME：pool的名称
NODENAME：该pool下节点的名称
NODEIP：节点的IP地址
NODEPORT：节点的服务端口
NODEAVAILABILITY：节点的可用性
NODESTATE：节点的状态
NODESTATEREASON：处于该状态的原因
NODEMONITOR：节点监听器
NODEMONITORSTATUS：节点监听器状态
NODESESSIONSTATUS：节点会话状态
NODEBITSIN：流入节点的流量
NODEBITSOUT：流出节点的流量
NODEPACKETSIN：流入节点的数据包
NODEPACKETSOUT：流出节点的数据包
NODECURCONN：节点当前连接数
NODEMAXCONN：节点最大连接数
NODETOTALCONN：节点所有的连接数
NODETOTALREQUEST：节点所有的连接请求数
NODECURSESSION：节点当前会话数
UPDATETIME：数据插入时间
"""
create_table = 'CREATE TABLE F5_node_info (\
F5IP VARCHAR2(30),\
POOLNAME VARCHAR2(50),\
NODENAME VARCHAR2(40),\
NODEADDR VARCHAR2(40) not null,\
NODEPORT VARCHAR2(40) not null,\
NODEAVAILABILITY VARCHAR2(40),\
NODESTATE VARCHAR2(40),\
NODESTATEREASON VARCHAR2(200),\
NODEMONITOR VARCHAR2(40),\
NODEMONITORSTATUS VARCHAR2(40),\
NODESESSIONSTATUS VARCHAR2(40),\
NODEBITSIN VARCHAR2(40),\
NODEBITSOUT VARCHAR2(40),\
NODEPACKETSIN VARCHAR2(40),\
NODEPACKETSOUT VARCHAR2(40),\
NODECURCONN VARCHAR2(40),\
NODEMAXCONN VARCHAR2(40),\
NODETOTALCONN VARCHAR2(40),\
NODETOTALREQUEST VARCHAR2(40),\
NODECURSESSION VARCHAR2(40),\
UPDATETIME DATE DEFAULT SYSDATE\
)'

insert_data = "INSERT INTO F5_node_info (F5IP,POOLNAME,NODENAME,NODEADDR,NODEPORT,\
NODEAVAILABILITY,NODESTATE,NODESTATEREASON,NODEMONITOR,NODEMONITORSTATUS,\
NODESESSIONSTATUS,NODEBITSIN,NODEBITSOUT,NODEPACKETSIN,NODEPACKETSOUT,\
NODECURCONN,NODEMAXCONN,NODETOTALCONN,NODETOTALREQUEST,NODECURSESSION) \
values ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"

def insertData():
    conn = ConnectDB(host, port, username, password, sid).getconn
    cursor = conn.cursor()
    cursor.execute(create_table)
    with open('f5_addr.txt', 'r') as f5_ip_all:
        for f5_ip in f5_ip_all.readlines():
            if f5_ip:
                f5_ip = f5_ip.strip()
                node_tuple = getNodeState(f5_ip)
                for argv in node_tuple:
                    print argv
                    cursor.execute(insert_data % argv)
                conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    insertData()