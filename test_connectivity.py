#!/usr/bin/python

# test all configs and put nodes with good connectivity under a folder
import os
import subprocess
import requests
import time
from multiprocessing import Process, Queue

from flask import Flask

#base_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = "/home/adwin/Tools/vmess2json"

def run_local_server(q):
    app = Flask(__name__)
    usable_nodes = {'nodes' : []}

    @app.route('/usable_nodes/')
    def get_usable_nodes():
        if q:
            usable_nodes = q.get()
        return usable_nodes
    app.run(host="127.0.0.1", port=10900)

def test_node(config_path):
    p = subprocess.Popen(["{}/v2ray-core/v2ray".format(base_dir), "-config", config_path])
    time.sleep(3)
    seconds_used = 100
    try:
        response = requests.get("https://news.ycombinator.com", headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}, proxies=dict(http="socks5h://127.0.0.1:10800", https="socks5h://127.0.0.1:10800"), timeout=30)
        seconds_used = response.elapsed.total_seconds()
    except:
        pass
    p.terminate()
    time.sleep(2)
    print("{} used {} seconds to fetch data".format(config_path, seconds_used))
    return seconds_used

q = Queue()
p = Process(target=run_local_server, args=(q,))
p.start()
while True:
    config_names = [f for f in os.listdir(os.path.join(base_dir, "test_connectivity_configs")) if os.path.isfile(os.path.join(base_dir, f)) and f.endswith(".json")]
    usable_nodes = {'nodes' : []}
    for config_name in config_names:
        seconds_used = test_node(os.path.join(base_dir, "test_connectivity_configs", config_name))
        if seconds_used < 10:
            usable_nodes['nodes'].append(config_name)
    q.put(usable_nodes)
    time.sleep(300)
