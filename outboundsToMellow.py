#!/usr/bin/python

import json
import os
import copy
import sys




base_dir = os.path.dirname(os.path.abspath(__file__))
# base_dir = "/home/adwin/Tools/vmess2json"


def convert_to_mellow(filepath):
    original_data = None
    with open(filepath, 'r') as original_file:
        original_data = json.load(original_file)
    mellow_outbound = "vmess1://" + original_data['outbounds'][0]['settings']['vnext'][0]['users'][0]['id'] + '@' + original_data['outbounds'][0]['settings']['vnext'][0]['address'] + ":" + str(original_data['outbounds'][0]['settings']['vnext'][0]['port'])
    if original_data['outbounds'][0]['streamSettings']['network'] == 'tcp':
        mellow_outbound += "?network=tcp"
    elif original_data['outbounds'][0]['streamSettings']['network'] == 'ws':
        mellow_outbound += original_data['outbounds'][0]['streamSettings']['wsSettings']['path'] + "?network=ws"
        if 'security' in original_data['outbounds'][0]['streamSettings']:
            mellow_outbound += '&tls=true'
        mellow_outbound += '&ws.host=' + original_data['outbounds'][0]['streamSettings']['wsSettings']['headers']['Host']
    return mellow_outbound

with open(base_dir + '/mellow_outbounds.txt', 'w') as mellow_outbound_file:
    if len(sys.argv) == 1:
        for i, filename in enumerate(os.listdir(base_dir)):
            if filename.endswith(".json"):
                print(base_dir + '/' + filename)
                outbound = convert_to_mellow(base_dir + '/' + filename)
                print(outbound)
                mellow_outbound_file.write("Proxy-{}, vmess1, {}\n".format(i + 1, outbound))
    elif len(sys.argv) == 2:
        outbound = convert_to_tproxy(sys.argv[1])
        print(outbound)
        mellow_outbound_file.write("Proxy-1, vmess1, {}\n".format(outbound))
