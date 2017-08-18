#!/bin/sh
#python /root/demo/license/bigiq_license.py -name Registration-Keys-Pool -op revoke -type regkey -iq 10.255.72.25 -iq_user admin -iq_pass admin -ip 173.255.119.130 -port 8443 -ip_user admin -ip_pass admin
sleep 10
python /root/demo/license/bigiq_license.py -name Registration-Keys-Pool -op grant -type regkey -iq 10.255.72.25 -iq_user admin -iq_pass admin -ip 10.255.72.140 -port 443 -ip_user admin -ip_pass admin

