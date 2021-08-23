#!/usr/bin/python

import json
import os
import copy
import sys




base_dir = os.path.dirname(os.path.realpath(__file__))
# base_dir = "/home/adwin/Tools/vmess2json"

template_data = None
with open(os.path.join(base_dir, "outbounds.template"), 'r') as template_file:
    template_data = json.load(template_file)

def convert_to_tproxy(filepath, destpath):
    global template_data
    result_data = copy.deepcopy(template_data)
    original_data = None
    with open(filepath, 'r') as original_file:
        original_data = json.load(original_file)
    result_data['outbounds'].insert(0, original_data['outbounds'][0])
    result_data['outbounds'][0]['streamSettings']['sockopt'] = {'mark' : 255}
    result_data['outbounds'][0]['tag'] = "proxy"
    with open(destpath, 'w') as original_file:
        json.dump(result_data, original_file, indent=4)

if len(sys.argv) == 1:
    for filename in os.listdir(base_dir):
        if filename.endswith(".json"):
            print(os.path.join(base_dir, filename))
            try:
                convert_to_tproxy(os.path.join(base_dir, filename), os.path.join(base_dir, filename))
            except json.decoder.JSONDecodeError:
                continue
            except KeyError:
                continue
            else:
                continue
elif len(sys.argv) == 2:
    if os.path.isfile(sys.argv[1]):
        convert_to_tproxy(sys.argv[1], base_dir + '/' + sys.argv[1].split('/')[-1])
    elif os.path.isdir(sys.argv[1]):
        for filename in os.listdir(sys.argv[1]):
            if filename.endswith(".json"):
                print(os.path.join(base_dir, filename))
                try:
                    convert_to_tproxy(os.path.join(sys.argv[1], filename), os.path.join(base_dir, filename))
                except json.decoder.JSONDecodeError:
                    continue
                except KeyError:
                    continue
                else:
                    continue

elif len(sys.argv) == 4:
    template_filepath = sys.argv[2]
    save_dir = sys.argv[3]
    with open(template_filepath, 'r') as template_file:
        template_data = json.load(template_file)
