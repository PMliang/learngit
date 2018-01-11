#!/bin/bash
login_name=yourusername
login_ip=$1
login_pw=yourpassword
VALUE=f5ssh
cmd=$2
echo '#!/usr/bin/expect'>$VALUE
echo "set timeout 120" >>$VALUE
echo "spawn ssh $login_name@$login_ip">>$VALUE
echo 'expect {
"yes/no" { send "yes\r"; exp_continue }
"assword:" { send "'$login_pw'\r"}
}'>>$VALUE
echo 'expect {
"#" { send "'$cmd'\r"}
}'>>$VALUE
echo 'expect {
"(y/n) " { send "y"; exp_continue }
")---" { send " "; exp_continue }
"(END)" { send "q"; exp_continue }
"#" { send "quit\r" }
}'>>$VALUE
echo 'expect {
"#" { send "quit\r" }
}'>>$VALUE
/usr/bin/expect $VALUE