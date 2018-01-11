#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import os
import pexpect
import sys

def pssh():
    login_user = "read"
    f5_ip = sys.argv[1]
    login_pw = "read2017"
    cmd = sys.argv[2]
    try:
        child = pexpect.spawn('/usr/bin/ssh %s@%s' % (login_user, f5_ip))
        child.logfile_read = sys.stdout
        while True:
            loginconfirm = child.expect(["\(yes/no\)?", "assword:"])
            if loginconfirm == 0:
                child.sendline("yes")
            if loginconfirm == 1:
                child.sendline(login_pw)
                break
        child.expect("#")
        child.sendline(cmd)
        print child.readlines()
        while True:
            index = child.expect(['(y/n)', '\)---', '\(END\)'])
            if index == 0:
                child.send("y")
            if index == 1:
                child.send(" ")
            if index == 2:
                child.send("q")
                break
        child.expect("#")
        child.sendline("quit")
        child.close()
    except pexpect.EOF:
        print 'eof'
    except pexpect.TIMEOUT:
        print "timeout"

if __name__ == "__main__":
    pssh()