#!/bin/python

# 1.ignore certain jsons.
# 2.remove useless jsons.

import os
import json
import copy
import configparser
import argparse
import shutil
import subprocess
import time

from vmess2json import *

config = {
    "outbounds_dir":  "",
    "urls": {},
    "outbound_template": 
        {
          "outbounds": [
            {
              "protocol": "vmess",
              "settings": {
                "vnext": [
                  {
                    "address": "shcn2.tomlink.icu",
                    "port": 61000,
                    "users": [
                      {
                        "email": "user@v2ray.com",
                        "id": "caae081a-6d6b-443e-b9d8-42a145c890ed",
                        "alterId": 1,
                        "security": "auto"
                      }
                    ]
                  }
                ],
                "domainStrategy": "UseIP"
              },
              "streamSettings": {
                "network": "ws",
                "wsSettings": {
                  "connectionReuse": True,
                  "path": "",
                  "headers": {
                    "Host": ""
                  }
                },
                "sockopt": {
                  "mark": 255
                }
              },
              "mux": {
                "enabled": True
              },
              "tag": "proxy"
            },
            {
              "tag": "direct",
              "protocol": "freedom",
              "settings": {
                "domainStrategy": "UseIP"
              },
              "streamSettings": {
                "sockopt": {
                  "mark": 255
                }
              }
            },
            {
              "tag": "block",
              "protocol": "blackhole",
              "settings": {
                "response": {
                  "type": "http"
                }
              }
            },
            {
              "tag": "dns-out",
              "protocol": "dns",
              "streamSettings": {
                "sockopt": {
                  "mark": 255
                }
              }
            }
          ]
        },
}





def convert_to_tproxy(prev_conf):
    tproxy_outbound = copy.deepcopy(config['outbound_template'])
    tproxy_outbound['outbounds'][0] = prev_conf['outbounds'][0]
    if 'streamSettings' not in tproxy_outbound['outbounds'][0]:
        tproxy_outbound['outbounds'][0]['streamSettings'] = {}
    tproxy_outbound['outbounds'][0]['streamSettings']['sockopt'] = {'mark' : 255}
    tproxy_outbound['outbounds'][0]['tag'] = "proxy"
    tproxy_outbound['outbounds'][0]['settings']['domainStrategy'] = "UseIP"
    return tproxy_outbound

#  previous_jsons = [f for f in os.listdir(base_dir) if os.path.isfile(os.path.join(base_dir, f)) and f.endswith(".json")]
#  for j in previous_jsons:
        #  shutil.move(os.path.join(base_dir, j), os.path.join(base_dir, 'tmp', j))


#  urls = {}
#  with open(base_dir + "/urls.txt", "r") as url_file:
    #  urls = json.load(url_file)['subscription']

#  headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}


def download_and_convert_subscription(sub_name, url):
    print(url)
    url = url.strip(' \r\n\t')
    print("Started to fetch content of {0}".format(url))
    links = read_subscribe(url)

    for l in links:
        outbound = parseLink(l)
        print(outbound)
        if outbound is not None:
            full_json = vmess2client(load_TPL("CLIENT"), outbound)
            name = "{}|{}.json".format(sub_name, outbound["ps"].replace("/", "_").replace(".", "-"))
            os.makedirs(config['outbounds_dir'], exist_ok=True)
            with open(os.path.join(config['outbounds_dir'], name), "w") as f:
                json.dump(convert_to_tproxy(full_json), f, indent=2)


#  for _, url in config['urls'].items():


# if failed to update, move old jsons back
#  if len([f for f in os.listdir(base_dir) if f.endswith(".json")]) < 10:
    #  for j in previous_jsons:
            #  shutil.move(os.path.join(base_dir, 'tmp', j), os.path.join(base_dir, j))
#  else:
    #  # Delete old jsons if success
    #  for j in previous_jsons:
        #  os.remove(os.path.join(base_dir, 'tmp', j))


if __name__ == "__main__":
    conf = configparser.ConfigParser()
    conf.read("/etc/v2t.conf")
    config['outbounds_dir'] = conf['GENERAL']['OutboundsDir']
    config['urls'] = conf['SUBSCRIPTION']

    parser = argparse.ArgumentParser(description="update v2ray subscription or change node")
    parser.add_argument('-u', '--update',
                        action="store_true",
                        default=False,
                        help="update from all subscriptions")
    parser.add_argument('-c', '--choose',
                        action="store_true",
                        default=False,
                        help="choose one node from local nodes")

    option = parser.parse_args()
    if option.update:   
        print(config['urls'])
        for key in config['urls']:
            download_and_convert_subscription(key, str(config['urls'][key]))
    if option.choose:
        out_files = os.listdir(config['outbounds_dir'])
        for i, v in enumerate(out_files):
            print(i, " :", v)
        choice = int(input("Please choose node by number: "))
        #  os.remove("/etc/v2ray/conf.d/06_outbounds.json")
        shutil.copy(os.path.join(config['outbounds_dir'], out_files[choice]), "/etc/v2ray/conf.d/06_outbounds.json")
        subprocess.run(["systemctl restart v2ray"], shell=True)
        time.sleep(0.5)

        


    

