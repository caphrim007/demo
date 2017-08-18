#!/usr/bin/env python
# -*- coding: utf-8 -*-

#@Author: Carl Dubois
#@Email: c.dubois@f5.com
#@Description: License an unmanaged BIGIP. Utility reg keys.
#@Product: BIGIQ
#@VersionIntroduced: 5.1.0

"""
Copyright 2017 by F5 Networks Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

usage: modify_pool_member_v2.py [-h] [-op OP] [-name NAME] [-iq IQ]
                                [-iq_user IQ_USER] [-iq_pass IQ_PASS]
                                [-csv CSV] [-list]

Usage:

List pool members and state. Perform action enable, disable, force-offline for
selected members.

optional arguments:
  -h, --help        show this help message and exit
  -op OP            To enable, disable, force-offline pool member. ex. enable,
                    disable, force-offline
  -name NAME        Name of pool memeber to perform action against.
  -iq IQ            Network address of BIG-IQ.
  -iq_user IQ_USER  Administrator username of BIGIP
  -iq_pass IQ_PASS  Administrator password if BIGIP
  -csv CSV          The csv file to identify pool members.
  -list
"""

import sys
import argparse
import requests
import re
import time
import os

try:
    import json
except ImportError:
    import simplejson as json

# disable request package warnings
requests.packages.urllib3.disable_warnings()

def operate_pool_members(args, csv):
    """
    1. Locate pool members.
    2. Perform action (enable, disable, force-offline) against pool members.
    """
    name=[]
    state=[]
    ##================
    # Find pool member
    ##================
    print "Enumerate all pool members to find: {0}".format(args.name)
    uri = 'https://' + args.iq + '/mgmt/cm/adc-core/working-config/ltm/pool'

    response = requests.get(uri, auth=(args.iq_user, args.iq_pass), verify=False)
    if response.status_code==200:
        ##=============================================================================
        # Identify pool member and execute operation. Enable / Disable / Force-Offline
        ##=============================================================================
        for item in response.json()['items']:            
            
            print item['name']
            
            if item['name'] == args.name:
                print 'Found pool: {0}'.format(args.name)
                uri_pool=item['membersCollectionReference']['link'].replace('localhost', args.iq)

                print uri_pool

                response = requests.get(uri_pool, auth=(args.iq_user, args.iq_pass), verify=False)
                if response.status_code==200:
                    for item in response.json()['items']:                 
                        for i in range(len(csv)):
                            if item['name'] == csv[i]:
                                print "INFO: Perform action {0} on pool member {1}".format(args.op, item['name'])
                                uri_self = 'https://' + args.iq + '/mgmt/cm/adc-core/tasks/self-service'
                                op_json = {"operation":args.op, "resourceReference":{"link":str(item['selfLink'])}}
                                response = requests.post(uri_self, data=str(op_json), auth=(args.iq_user, args.iq_pass), verify=False)
                                #print json.dumps(response.json(), default=lambda o: o.__dict__, sort_keys=True, indent=4)
                                break
                else:
                    continue
                break
        else: 
            print "ERROR: Unable to find pool members defined in csv."
            return False
    return True

def list_pool_members(args):
    """
    List pool members.
    List overall state of pool members.
    List session state of pool members. 
    """
    ##================
    # List pool member
    ##================
    print "Enumerate all pool mambers to find: {0}".format(args.name)
    uri = 'https://' + args.iq + '/mgmt/cm/adc-core/working-config/ltm/pool'

    response = requests.get(uri, auth=(args.iq_user, args.iq_pass), verify=False)
    i=0
    if response.status_code==200:
        ##========================================================================
        #  List all pool members to display state and session configuration states.
        #  #  ACTION          STATE    , SESSION
        #  1. force-offline = user-down, user-disabled
        #  2. enable        = user-up  , user-enabled
        #  3. disabled      = user-up  , user-disabled
        ##========================================================================
        for item in response.json()['items']:
            if item['name'] == args.name:
                print 'Found pool: {0}'.format(args.name)
                uri_pool=item['membersCollectionReference']['link'].replace('localhost', args.iq)
                response = requests.get(uri_pool, auth=(args.iq_user, args.iq_pass), verify=False)
                if response.status_code==200:
                    for item in response.json()['items']:
                        print 'Pool member {0}: State {1}: Session {2}'.format(item['name'], item['stateConfig'], item['sessionConfig'])
                    return True
                else:
                    return False
        else:
            print 'ERROR: Unable to find pool with name: {0}'.format(args.name)
    
    return True

if __name__ == '__main__':
    #==========================
    # Help
    #==========================
    parser = argparse.ArgumentParser(description='List pool members and state. Perform action enable, disable, force-offline for selected members.')
    parser.add_argument('-op', type=str, help='To enable, disable, force-offline pool member. ex. enable, disable, force-offline')
    parser.add_argument('-name', type=str, help='Name of pool memeber to perform action against.')
    parser.add_argument('-iq', type=str, help='Network address of BIG-IQ.')
    parser.add_argument('-iq_user', type=str, help='Administrator username of BIGIP')
    parser.add_argument('-iq_pass', type=str, help='Administrator password if BIGIP')
    parser.add_argument('-csv', type=str, help='The csv file to identify pool members.')
    parser.add_argument('-list', action='store_true')

    #==========================
    # Parser arguments
    #==========================
    args = parser.parse_args()

    #==========================
    # Read config file
    #==========================
    file = args.csv
    csv=[]

    if file:
	with open (file) as infile:
	    for line in infile:
                line = line.strip('\n')
                csv.append(line)
    else:
	print "ERROR: No agrument for csv file."
	sys.exit(1)

    #==========================
    # RegKey License Funtion
    #==========================
    if args.list:
        result = list_pool_members(args) 
    elif args.op=='enable' or args.op=='disable' or args.op=='force-offline':
        result = operate_pool_members(args, csv)
    else:
        os.system("python modify_pool_member.py -h")

    if result == True:
        print "INFO: BIG-IQ {0} pool member operation. SUCCESS".format(args.iq)
    else:
        print "ERROR: BIG-IQ {0} pool member operaion. ERROR".format(args.iq)
