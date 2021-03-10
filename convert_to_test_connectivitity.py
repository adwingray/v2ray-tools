#!/usr/bin/python

import json
import os
import copy
import sys




# base_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = "/home/adwin/Tools/vmess2json"

example_data = None
with open(os.path.join(base_dir, "test_connectivity.example"), 'r') as example_file:
    example_data = json.load(example_file)

def convert_to_test_conn(filepath, destpath):
    global example_data
    result_data = copy.deepcopy(example_data)
    original_data = None
    with open(filepath, 'r') as original_file:
        original_data = json.load(original_file)
    result_data['outbounds'].insert(0, original_data['outbounds'][0])
    result_data['outbounds'][0]['streamSettings']['sockopt'] = {'mark' : 255}
    result_data['outbounds'][0]['tag'] = "proxy"
    if ("full:" + original_data['outbounds'][0]['settings']['vnext'][0]['address']) not in result_data['dns']['servers'][-1]['domains']:
        result_data['dns']['servers'][-1]['domains'].append("full:" + original_data['outbounds'][0]['settings']['vnext'][0]['address'])
    with open(destpath, 'w') as original_file:
        json.dump(result_data, original_file, indent=4)

if len(sys.argv) == 1:
    for filename in os.listdir(base_dir):
        if filename.endswith(".json"):
            print(base_dir + '/' + filename)
            convert_to_tproxy(base_dir + '/' + filename, base_dir + '/' + filename)
elif len(sys.argv) == 2:
    if os.path.isfile(sys.argv[1]):
        convert_to_tproxy(sys.argv[1], base_dir + '/' + sys.argv[1].split('/')[-1])
    elif os.path.isdir(sys.argv[1]):
        for filename in os.listdir(sys.argv[1]):
            if filename.endswith(".json"):
                print(base_dir + '/' + filename)
                convert_to_tproxy(os.path.join(sys.argv[1], filename), base_dir + '/' + filename)

elif len(sys.argv) == 4:
    example_filepath = sys.argv[2]
    save_dir = sys.argv[3]
    with open(example_filepath, 'r') as example_file:
        example_data = json.load(example_file)