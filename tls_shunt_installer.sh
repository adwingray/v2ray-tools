#!/bin/bash

bash <(curl -L -s https://install.direct/go.sh)

bash <(curl -L -s https://raw.githubusercontent.com/liberal-boy/tls-shunt-proxy/master/dist/install.sh)

read -p "Enter domain of this host: " domain

rm /etc/tls-shunt-proxy/config.yaml
cat <<EOF >> /etc/tls-shunt-proxy/config.yaml
listen: 0.0.0.0:443
vhosts:
  - name: $domain
    tlsoffloading: true
    managedcert: true
    alpn: h2,http/1.1
    protocols: tls12,tls13
    http:
      handler: fileServer
      args: /var/www/html
    default:
      handler: proxyPass
      args: 127.0.0.1:40001
EOF

uuid="$(cat /proc/sys/kernel/random/uuid)"
echo $uuid

rm /etc/v2ray/config.json
cat <<EOF >> /etc/v2ray/config.json
{
    "inbounds": [
        {
            "protocol": "vmess",
            "listen": "127.0.0.1",
            "port": 40001,
            "settings": {
                "clients": [
                    {
                        "id": "$uuid"
                    }
                ]
            },
            "streamSettings": {
                "network": "tcp"
            }
        }
    ],
    "outbounds": [
        {
            "protocol": "freedom"
        }
    ]
}
EOF

systemctl enable --now tls-shunt-proxy
systemctl enable --now v2ray
