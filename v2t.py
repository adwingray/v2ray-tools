#!/bin/env python

import os
import json
import copy
import configparser
import argparse
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
    tproxy_outbound['outbounds'].insert(0, prev_conf['outbounds'][0])
    if 'streamSettings' not in tproxy_outbound['outbounds'][0]:
        tproxy_outbound['outbounds'][0]['streamSettings'] = {}
    tproxy_outbound['outbounds'][0]['streamSettings']['sockopt'] = {'mark' : 255}
    tproxy_outbound['outbounds'][0]['tag'] = "proxy"
    tproxy_outbound['outbounds'][0]['settings']['domainStrategy'] = "UseIP"
    return tproxy_outbound


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

def set_direct_dns_for_outbound(outbound, dns):
    domain = None
    if 'vnext' in outbound[0]['settings']:
        domain = outbound[0]['settings']['vnext'][0]['address']
    elif 'servers' in outbound[0]['settings']:
        domain = outbound[0]['settings']['servers'][0]['address']

    if domain is None:
        print("No domain found in outbound. Check format changes.")
        exit(1)

    dns['servers'][-1]['domains'][1] = "domain:" + domain
    print(dns)



    

def main():
    conf = configparser.ConfigParser()
    conf.read("/etc/v2t.conf")
    config['outbounds_dir'] = conf['GENERAL']['OutboundsDir']
    config['dest_config_file'] = conf['GENERAL']['DestConfigFile']
    config['urls'] = conf['SUBSCRIPTION']
    config['template_config_file'] = conf['GENERAL']['TemplateConfigFile']

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
            try:
                download_and_convert_subscription(key, str(config['urls'][key]))
            except:
                print("Error happened when downloading subscription")

    if option.choose:
        out_files = os.listdir(config['outbounds_dir'])
        out_files.sort()
        for i, v in enumerate(out_files):
            print(i, " :", v)
        choice = int(input("Please choose node by number: "))

        # Load the full template
        v2ray_config = {}
        if config['template_config_file'] == "":
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")) as f:
                v2ray_config = json.load(f)
        else:
            with open(config['template_config_file']) as f:
                v2ray_config = json.load(f)


        # Load chosen outbound
        outbound = {}
        with open(os.path.join(config['outbounds_dir'], out_files[choice])) as f:
            outbound = json.load(f)

        # Merge them
        v2ray_config |= outbound
        set_direct_dns_for_outbound(v2ray_config['outbounds'], v2ray_config['dns'])
        os.makedirs(os.path.join(os.path.dirname(config['dest_config_file'])), exist_ok=True)
        with open(config['dest_config_file'], "w") as f:
            json.dump(v2ray_config, f, indent=2)
        subprocess.run(["systemctl stop cgproxy"], shell=True)
        time.sleep(0.5)
        subprocess.run(["systemctl restart v2ray"], shell=True)
        time.sleep(0.5)
        subprocess.run(["systemctl start cgproxy"], shell=True)
        time.sleep(0.5)


if __name__ == "__main__":
    main()
