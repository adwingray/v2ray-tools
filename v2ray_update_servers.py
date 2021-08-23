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


base_dir = os.path.dirname(os.path.realpath(__file__))
#  base_dir = "/home/adwin/Tools/vmess2json"
previous_jsons = [f for f in os.listdir(base_dir) if os.path.isfile(os.path.join(base_dir, f)) and f.endswith(".json")]
for j in previous_jsons:
        shutil.move(os.path.join(base_dir, j), os.path.join(base_dir, 'tmp', j))


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
        # wait for vmess2json.py to finish its work
        time.sleep(1)
        #  convert_to_balancer(name)
    except:
        print("some errors happened")


# convert_to_tproxy
subprocess.run(["{}/convert_to_tproxy.py".format(base_dir)])
time.sleep(1)

# if failed to update, move old jsons back
if len([f for f in os.listdir(base_dir) if f.endswith(".json")]) < 10: 
    for j in previous_jsons:
            shutil.move(os.path.join(base_dir, 'tmp', j), os.path.join(base_dir, j))
else:
    # Delete old jsons if success
    for j in previous_jsons:
        os.remove(os.path.join(base_dir, 'tmp', j))



# copy private jsons
#  private_jsons = [f for f in os.listdir(os.path.join(base_dir, "private")) if os.path.isfile(os.path.join(base_dir, "private", f)) and f.endswith(".json")]
#  for j in private_jsons:
    #  shutil.copy(os.path.join(base_dir, "private", j), base_dir)
