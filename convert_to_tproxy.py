#!/usr/bin/python

import json
import os
import copy
import sys




base_dir = os.path.dirname(os.path.abspath(__file__))

example_data = None
with open(base_dir + "/tproxy.example", 'r') as example_file:
    example_data = json.load(example_file)

def convert_to_tproxy(filepath, destpath):
    global example_data
    result_data = copy.deepcopy(example_data)
    original_data = None
    with open(filepath, 'r') as original_file:
        original_data = json.load(original_file)
    result_data['outbounds'].insert(0, original_data['outbounds'][0])
    result_data['outbounds'][0]['streamSettings']['sockopt'] = {'mark' : 255}
    with open(destpath, 'w') as original_file:
        json.dump(result_data, original_file)

if len(sys.argv) == 1:
    for filename in os.listdir(base_dir):
        if filename.endswith(".json"):
            print(base_dir + '/' + filename)
            convert_to_tproxy(base_dir + '/' + filename, base_dir + '/' + filename)
elif len(sys.argv) == 2:
    convert_to_tproxy(sys.argv[1], base_dir + '/' + sys.argv[1].split('/')[-1])
