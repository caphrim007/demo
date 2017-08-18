#!/usr/bin/env python
# -*- coding: utf-8 -*-

#@Author: Carl Dubois
#@Email: c.dubois@f5.com
#@Description: BIGIQ / BIGIP create firewall policy, reference to virtual
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

import sys
import re
import base64
import string
import os.path
import argparse
import requests
import time

## Disable request package warnings.
requests.packages.urllib3.disable_warnings()

try:
    import json
except ImportError:
    import simplejson as json

def create_policy(config):
    print "\n"
    print '####Create firewall policy {0}####'.format(config['policy_name'])

    ## Create address list
    data = {"addresses":[{"address":config["addr_list_ip"], "description": "Address-List"}], "partition":"Common", "name":config["addr_list"]}
    uri = 'https://' + config['bigiq'] + '/mgmt/cm/firewall/working-config/address-lists'
    
    ## Request POST
    response = requests.post(uri, data=str(data), auth=(config['iq_user'], config['iq_pass']), verify=False)
    ## DEBUG ##
    #print json.dumps(response.json(), default=lambda o: o.__dict__, sort_keys=True, indent=4)
    ###########
    t=1
    if response.status_code in [200, 202]:
        print "\nINFO: Address-List {0} create was successful.".format(config['addr_list'])
        addr_link = response.json()['selfLink'].replace('localhost', config['bigiq'])
    else:
        print "\nERROR: Unable to create address-list {0}".format(config['addr_list'])
        return False

    ## Create port list
    port=re.match(r"(\d+), (\d+)", config['port_list_port'])
    port1=port.group(1)
    port2=port.group(2)
    data = {"ports":[{"port":port1, "description": "port_1"}, {"port":port2, "description": "port_2"}], "partition":"Common", "name":config["port_list"]}
    uri = 'https://' + config['bigiq'] + '/mgmt/cm/firewall/working-config/port-lists'
    
    ## Request POST
    response = requests.post(uri, data=str(data), auth=(config['iq_user'], config['iq_pass']), verify=False)
    ## DEBUG ##
    #print json.dumps(response.json(), default=lambda o: o.__dict__, sort_keys=True, indent=4)
    ###########
    t=1
    if response.status_code in [200, 202]:
        print "\nINFO: Port-List {0} create was successful.".format(config['port_list'])
        port_link = response.json()['selfLink'].replace('localhost', config['bigiq'])
    else:
        print "\nERROR: Unable to create port-list {0}".format(config['port_list'])
        return False

    ## Create policy
    data = {"partition":"Common", "name":config["policy_name"]}
    uri = 'https://' + config['bigiq'] + '/mgmt/cm/firewall/working-config/policies'
    
    ## Request POST
    response = requests.post(uri, data=str(data), auth=(config['iq_user'], config['iq_pass']), verify=False)
    ## DEBUG ##
    #print json.dumps(response.json(), default=lambda o: o.__dict__, sort_keys=True, indent=4)
    ###########
    
    t=1
    if response.status_code in [200, 202]:
        policy_link = response.json()['selfLink'].replace('localhost', config['bigiq'])
    else:
        print "\nERROR: Unable to create firewall policy {0}".format(config['policy_name'])
        print json.dumps(response.json()['message'], default=lambda o: o.__dict__, sort_keys=True, indent=4)
        return False

    policy_link+="/rules"
    data = {"name":config["rule_name"], "rowHeight":'45', "editRowHeight":'125', "action":"accept", "protocol":"tcp", "state":"enabled", "log":"false", "$isNew":"true", "clientOrder":'1', "source":{"addressListReferences":[{"name":config["addr_list"], "link":str(addr_link), "$isNew":"true"}], "portListReferences":[{"name":config["port_list"], "link":str(port_link), "$isNew":"true"}]}, "partition":"Common", "evalOrder":'1000'}

    ## Request POST
    response = requests.post(policy_link, data=str(data), auth=(config['iq_user'], config['iq_pass']), verify=False)
    ## DEBUG ##
    # print json.dumps(response.json(), default=lambda o: o.__dict__, sort_keys=True, indent=4)
    ###########
    if response.status_code in [200, 202]:
        print "\nINFO: Firewall Policy {0} create and add rule containing address-list and port-list was successful.".format(config['policy_name'])
        rule_link = response.json()['selfLink'].replace('localhost', config['bigiq'])
    else:
        print "\nERROR: Unable to create add rules to policy {0}".format(config['policy_name'])
        print json.dumps(response.json()['message'], default=lambda o: o.__dict__, sort_keys=True, indent=4)
        return False

    return policy_link

def reference_to_virtual(config, policy):
    print "\n"
    print '####Add policy {0} to virtual server {1}####'.format(config['policy_name'], config['virtual_server'])
    
    if policy == False:
        return False
    else:
        policy = re.sub('/rules$', '', policy)
        ## Get virtual server firewall context
        uri = 'https://' + config['bigiq'] + '/mgmt/cm/firewall/working-config/firewalls'
        response = requests.get(uri, auth=(config['iq_user'], config['iq_pass']), verify=False)
        
        for i in range(len(response.json()['items'])):
            if response.json()['items'][i]['name'] == config['virtual_server']:
                print "\n### PATCH the policy {0} into virtual server {1} ###".format(config['policy_name'], config['virtual_server'])
                data = {"enforcedPolicyReference":{"link":str(policy)}}
                virtual_link = response.json()['items'][i]['selfLink'].replace('localhost', config['bigiq'])
                response = requests.patch(virtual_link, data=str(data), auth=(config['iq_user'], config['iq_pass']), verify=False)
                if response.status_code in [200, 202]:
                    print "\nINFO: PATCH firewall policy {0} into virtual server {1} was successful".format(config['policy_name'], config['virtual_server'])
                    return True
                else:
                    print "\nERROR: Unable to create firewall policy {0}".format(config['policy_name'])
                    print json.dumps(response.json()['message'], default=lambda o: o.__dict__, sort_keys=True, indent=4)
                    return False
            else:
                continue
        else:
            print "\nERROR: Unable to find the virtual server named {0} to house policy named {1}".format(config['virtual_server'], config['policy_name'])
            return False

    return True

if __name__ == '__main__':
    config = {}
    parser = argparse.ArgumentParser(description='Create a Firewall Policy and Reference to a Virtual.')
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
    # create firewall policy
    #==========================
    policy = create_policy(config)
    time.sleep(3)
    #==========================
    # reference policy to virtual
    #==========================
    result = reference_to_virtual(config, policy)
    time.sleep(3)
    
    if result == True:
        print "\nINFO: Create policy {0} and referenced to virtual {1} complete.".format(config['policy_name'], config['virtual_server'])
    else:
        print "\nERROR: Create policy {0} and referenced to virtual {1} failed.".format(config['policy_name'], config['virtual_server'])
        
