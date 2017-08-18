#!/usr/bin/env python
# -*- coding: utf-8 -*-

#@Author: Carl Dubois
#@Email: c.dubois@f5.com
#@Description: Create JSON report for Utility Based Licensing
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
import base64
import string
import requests
import time

requests.packages.urllib3.disable_warnings()

try:
    import json
except ImportError:
    import simplejson as json

def get_json_report(args):
    print "\n==================================================================="    
    print "POST to create utility report based on base registration key"
    print "===================================================================\n"

    uri = 'https://' + args.bigiq + '/mgmt/cm/device/licensing/utility-billing-reports'
    data_json = {"regKey":args.baseregkey,"manuallySubmitReport":'true'}
    response = requests.post(uri, data=str(data_json), auth=('admin', 'admin'), verify=False)

    if response.status_code==202:
        self_uri = response.json()['selfLink'].replace('localhost', args.bigiq)
        time.sleep(4)
        response = requests.get(self_uri, auth=('admin', 'admin'), verify=False)
        report_uri = response.json()['reportUri'].replace('localhost', args.bigiq)
        return True, report_uri

    else:
        print response.json()
        return False

if __name__ == '__main__':
    #==========================
    # Help
    #==========================
    config={}
    import argparse

    parser = argparse.ArgumentParser(description='GET authentication token from BIGIQ.')
    parser.add_argument('--bigiq', type=str, help='Configuration, IQ address.')
    parser.add_argument('--baseregkey', type=str, help='Base reg key for utility pool.')
    args = parser.parse_args()

    #==========================
    # Get JSON Report
    #==========================
    result = get_json_report(args) 
    
    if result[0] == True: 
        print 'SUCCESS: JSON Report created. - COMPLETE.'
        print result[1]
    else:
        print 'INFO: Unable to create JSON report. - NOT-COMPLETE'
