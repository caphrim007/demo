#!/usr/bin/env python
# -*- coding: utf-8 -*-

#@Author: Carl Dubois
#@Email: c.dubois@f5.com
#@Description: Report mapping a virtual server to a BIGIP
#@Product: BIGIQ
#@VersionIntroduced: 5.0.0

import sys
import json
import base64
import string
import os.path

def device_report(config):
    print "\n"
    print '####Show virtual servers and its corresponding BIGIP device name####'

    ## If config file is defiend we will use requests else we will assume running on BIGIQ and use httplib
    try:
        import requests
	requests.packages.urllib3.disable_warnings()
        uri = 'https://' + config['bigiq'] + '/mgmt/cm/adc-core/working-config/ltm/virtual'
	response = requests.get(uri, auth=(config['username'], config['password']), verify=False)
	parsed_response = response.json()
    except:
        import httplib
        ## Header used in the connection request
        headers = {}    
        headers['Authorization'] = 'Basic ' + string.strip(base64.b64encode(config['username'] + ':' + config['password']))
        connection = httplib.HTTPConnection('localhost:8100')
        ## Request GET virtuals
	connection.request('GET', '/cm/adc-core/working-config/ltm/virtual', None, headers)
        ## Parse Response
	response = connection.getresponse()

        ## If not successful then print response and exit.
	if response.status != 200:
           print response.status
	   print response.reason
	   return False

        response = response.read()
	parsed_response = json.loads(response)

    ## Lets take a look at the virtuals and the BIGIP device it belongs to.
    count = 1
    for item in parsed_response['items']:
        print str(count) + ". Virtual Server=" + item['name'] + " belongs to BIGIP=" + item['deviceReference']['name']
	count+=1

    print "\n"
    return True

if __name__ == '__main__':
    #==========================
    # Help
    #==========================
    config={}
    try:
        import argparse
        parser = argparse.ArgumentParser(description='Workflow Trust, Discover, Import LTM, AFM, ASM.')
        parser.add_argument('--config', type=str, help='Configuration,IQ-IP address, user, pass.')

        args = parser.parse_args()

        #==========================
        # Read config file
        #==========================
        file = args.config

        file = '{0}'.format(file)
        infile = open (file, 'r')
        for line in infile:
            (key, val) = line.split('=')
            config[str(key)] = val.strip('\n')
            
    except:
	print "No configuration file provided. Using localhost for network address. Assuming running directly on BIGIQ"
	config['username'] = 'admin'
	config['password'] = 'admin'

    #==========================
    # Report
    #==========================
    result = device_report(config) 
    if result == True: print 'Virtuals to Device reference report - COMPLETE.'
