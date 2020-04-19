#!/usr/bin/python

import json
import os
import copy
import sys




# base_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = "/home/adwin/Tools/vmess2json"

example_data = None
with open(base_dir + "/tproxy.example", 'r') as example_file:
    example_data = json.load(example_file)


with open(base_dir + "/ultimate.json", 'w') as ultimate_file:
    ultimate_data = copy.deepcopy(example_data)
    ultimate_data['routing']['balancers'][0]['selector'] = []
    for i, filename in enumerate(os.listdir(base_dir)):
        if filename.endswith(".json") and filename != 'ultimate.json':
            print(base_dir + '/' + filename)
            original_data = None
            tag = "proxy-{}".format(i)
            with open(base_dir + '/' + filename, 'r') as original_file:
                original_data = json.load(original_file)
            ultimate_data['outbounds'].insert(0, original_data['outbounds'][0])
            ultimate_data['outbounds'][0]['streamSettings']['sockopt'] = {'mark' : 255}
            ultimate_data['outbounds'][0]['tag'] = tag
            if ("full:" + original_data['outbounds'][0]['settings']['vnext'][0]['address']) not in ultimate_data['dns']['servers'][-1]['domains']:
                ultimate_data['dns']['servers'][-1]['domains'].append("full:" + original_data['outbounds'][0]['settings']['vnext'][0]['address'])
            if ("full:" + original_data['outbounds'][0]['settings']['vnext'][0]['address']) not in ultimate_data['routing']['rules'][-2]['domain']:
                ultimate_data['routing']['rules'][-2]['domain'].append("full:" + original_data['outbounds'][0]['settings']['vnext'][0]['address'])
            ultimate_data['routing']['balancers'][0]['selector'].append(tag)
    json.dump(ultimate_data, ultimate_file, indent=4)
