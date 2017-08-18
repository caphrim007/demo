#!/usr/bin/env python
# -*- coding: utf-8 -*-

#@Author: Carl Dubois
#@Email: c.dubois@f5.com
#@Description: System Authentication Token 
#@Product: BIGIQ
#@VersionIntroduced: 5.x

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
"""

import os
import sys
import simplejson as json
import base64
import string
import subprocess
import requests

requests.packages.urllib3.disable_warnings()

try:
    import json
except ImportError:
    import simplejson as json

def get_auth_token(config):
    print '####Get a authentication token from BIG-IQ.####'
    print "\n==================================================================="    
    print "POST to receive an authentication token to log into a target BIG-IQ"
    print "===================================================================\n"

    uri = 'https://' + config['bigiq'] + '/mgmt/shared/authn/login'
    data_json = {"username":config['username'], "password":config['password']}
    response = requests.post(uri, data=str(data_json), verify=False)
    
    if response.status_code==200:
        print "### Refresh Authentication Token ###"
        print response.json()['refreshToken']['token']
        print "\n"
        print "### Refresh Authentication Timout ###"
        print response.json()['refreshToken']['timeout']
        print "\n"
        print "### Authentication Token ###"
        print response.json()['token']['token']
        print "\n"
        print "### Authentication Token Timeout ###"
        print response.json()['token']['timeout']
    else:
        print response.json()['message']
        return False
    
    #print "\n================================================"
    #print "Test out rest call with new authentication token"
    #print "================================================\n"
    
    #info = {}
    #token = response.json()['token']['token']
    #f5_token = 'X-F5-Auth-Token: ' + str(token)
    #stat_uri = 'https://' + config['bigiq'] + '/mgmt/shared/diagnostics/device-stats'
    
    ## curl
    #os.system('curl -sk -H foo stats_uri')
    
    ## requests
    #response = requests.get(uri, headers=foo, verify=False)
    #response_json = response.json()

    ## response test
    #if response.status_code==200:
    #    print "OK"
    #else:
    #    print json.dumps(response.json(), default=lambda o: o.__dict__, sort_keys=True, indent=4)
        #print response_json['message']

    return True
    
#def refresh_auth_token(config):

if __name__ == '__main__':
    #==========================
    # Help
    #==========================
    config={}
    import argparse

    parser = argparse.ArgumentParser(description='GET authentication token from BIGIQ.')
    parser.add_argument('--config', type=str, help='Configuration, IQ-IP address, user, pass.')

    args = parser.parse_args()
    
    #==========================
    # Read config file
    #==========================    
    file = args.config
    
    infile = open (file, 'r')
    for line in infile:
        (key, val) = line.split(' = ')
        config[str(key)] = val.strip('\n')
        

    #==========================
    # Auth
    #==========================
    result = get_auth_token(config) 
    
    if result == True: 
        print 'SUCCESS: Retrived authentication token. - COMPLETE.'
    else:
        print 'INFO: Resolve authentication token. - NOT-COMPLETE'
        
