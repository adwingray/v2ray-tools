#!/bin/python

# 1.ignore certain jsons.
# 2.remove useless jsons.

from urllib import parse
import requests
import os
import subprocess
import shutil
import time
import json
import copy

class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


base_dir = os.path.dirname(os.path.abspath(__file__))
# base_dir = "/home/adwin/Tools/vmess2json"
old_jsons = [f for f in os.listdir(base_dir) if os.path.isfile(os.path.join(base_dir, f)) and f.endswith(".json")]
for j in old_jsons:
    os.remove(os.path.join(base_dir, j))
old_jsons = [f for f in os.listdir(os.path.join(base_dir, "tmp")) if os.path.isfile(os.path.join(base_dir, "tmp", f)) and f.endswith(".json")]
for j in old_jsons:
    os.remove(os.path.join(base_dir, "tmp", j))
    #shutil.move(os.path.join(base_dir, json), "/tmp")

test_conn_example_data = None
with open(os.path.join(base_dir, "test_connectivity.example"), 'r') as example_file:
    test_conn_example_data = json.load(example_file)

def convert_to_test_conn(filepath, destpath):
    global test_conn_example_data
    result_data = copy.deepcopy(test_conn_example_data)
    original_data = None
    with open(filepath, 'r') as original_file:
        original_data = json.load(original_file)
    result_data['outbounds'].insert(0, original_data['outbounds'][0])
    result_data['outbounds'][0]['tag'] = "proxy"
    if ("full:" + original_data['outbounds'][0]['settings']['vnext'][0]['address']) not in result_data['dns']['servers'][-1]['domains']:
        result_data['dns']['servers'][-1]['domains'].append("full:" + original_data['outbounds'][0]['settings']['vnext'][0]['address'])
    with open(destpath, 'w') as original_file:
        json.dump(result_data, original_file, indent=4)

example_data = None
with open(base_dir + "/tproxy.example", 'r') as example_file:
    example_data = json.load(example_file)


def convert_to_balancer(filename):
    with open(os.path.join(base_dir, 'balancers', "{}.json".format(filename)), 'w') as ultimate_file:
        ultimate_data = copy.deepcopy(example_data)
        ultimate_data['routing']['balancers'][0]['selector'] = []
        current_jsons = [f for f in os.listdir(base_dir) if os.path.isfile(os.path.join(base_dir, f)) and f.endswith(".json")]
        for i, filename in enumerate(current_jsons):
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


urls = None
with open(base_dir + "/urls.txt", "r") as url_file:
    urls = json.load(url_file)['subscription']

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}


for name, url in urls.items():
    try:
        url = url.strip(' \r\n\t')
        print("Started to fetch content of {0}".format(url))
        urlpath = url.split('?')[0]
        params = dict(parse.parse_qsl(parse.urlsplit(url).query))
        print(urlpath)
        print(params)
        #response = requests.get(urlpath, params, timeout=10.0, headers=headers)
        response = requests.get(urlpath, params, timeout=10.0)
        if response.status_code != 200:
            print("Failed to fetch the content of {0}".format(url))
            continue;
        print(response.text)
        with open(base_dir + "/sub.txt", "w") as encoded_file:
            encoded_file.write(response.text)
        with cd(base_dir):
            p = subprocess.Popen("cat {0}/sub.txt | base64 -d | {0}/vmess2json.py --parse_all".format(base_dir), shell=True,
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        time.sleep(0.1)
        convert_to_balancer(name)
        previous_jsons = [f for f in os.listdir(base_dir) if os.path.isfile(os.path.join(base_dir, f)) and f.endswith(".json")]
        for j in previous_jsons:
            shutil.move(os.path.join(base_dir, j), os.path.join(base_dir, 'tmp', j))
    except:
        print("some errors happened")

# tmp_jsons = [f for f in os.listdir(os.path.join(base_dir, 'tmp')) if os.path.isfile(os.path.join(base_dir, 'tmp', f)) and f.endswith(".json")]
# for json in tmp_jsons:
#     os.move(os.path.join(base_dir, 'tmp', json), os.path.join(base_dir, json))

# convert_to_tproxy
# wait for vmess2json.py to finish its work
subprocess.run(["{}/convert_to_tproxy.py.backup".format(base_dir), os.path.join(base_dir, 'tmp')])
time.sleep(1)
for filename in os.listdir(os.path.join(base_dir, "tmp")):
    if filename.endswith(".json"):
        convert_to_test_conn(os.path.join(base_dir, "tmp", filename), os.path.join(base_dir, "test_connectivity_configs", filename))

# copy private jsons
private_jsons = [f for f in os.listdir(os.path.join(base_dir, "private")) if os.path.isfile(os.path.join(base_dir, "private", f)) and f.endswith(".json")]
for j in private_jsons:
    shutil.copy(os.path.join(base_dir, "private", j), base_dir)
balancer_jsons = [f for f in os.listdir(os.path.join(base_dir, "balancers")) if os.path.isfile(os.path.join(base_dir, "balancers", f)) and f.endswith(".json")]
for j in balancer_jsons:
    shutil.copy(os.path.join(base_dir, "balancers", j), base_dir)
