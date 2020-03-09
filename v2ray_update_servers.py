#!/bin/python

# 1.ignore certain jsons.
# 2.remove useless jsons.

from urllib import parse
import requests
import os
import subprocess
import shutil
import time

class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


#base_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = "/home/adwin/Tools/vmess2json"
old_jsons = [f for f in os.listdir(base_dir) if os.path.isfile(os.path.join(base_dir, f)) and f.endswith(".json")]
for json in old_jsons:
    os.remove(os.path.join(base_dir, json))
    #shutil.move(os.path.join(base_dir, json), "/tmp")

urls = []
with open(base_dir + "/urls.txt", "r") as url_file:
    urls.extend(url_file.readlines())

for url in urls:
    try:
        url = url.strip(' \r\n\t')
        print("Started to fetch content of {0}".format(url))
        urlpath = url.split('?')[0]
        params = dict(parse.parse_qsl(parse.urlsplit(url).query))
        print(urlpath)
        print(params)
        response = requests.get(urlpath, params, timeout=10.0);
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
    except:
        print("some errors happened")


# convert_to_tproxy
# wait for vmess2json.py to finish its work
time.sleep(0.1)
subprocess.run(["{}/convert_to_tproxy.py".format(base_dir)])

# copy private jsons
private_jsons = [f for f in os.listdir(os.path.join(base_dir, "private")) if os.path.isfile(os.path.join(base_dir, "private", f)) and f.endswith(".json")]
for json in private_jsons:
    shutil.copy(os.path.join(base_dir, "private", json), base_dir)
