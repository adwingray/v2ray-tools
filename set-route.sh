#!/usr/bin/bash
ip rule add fwmark 1 table 100
ip -6 rule add fwmark 1 table 100
ip route add local 0.0.0.0/0 dev lo table 100
ip -6 route add local ::/0 dev lo table 100

