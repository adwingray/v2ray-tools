#!/usr/bin/fish
set json_dir /home/adwin/Tools/vmess2json
set i 1
for s in $json_dir/*.json
	echo "$i ==> $s"
	set -g i (math $i + 1)
end
printf "Please choose the server you like:"
read -l chosen
echo $chosen
set i 1
for s in $json_dir/*.json
	if test $chosen -eq $i
		printf "You've chosen %s\n" $s
		cp $s /etc/v2ray/conf.d/06_outbounds.json
		systemctl restart v2ray
		exit
	end
	set -g i (math $i + 1)
end
