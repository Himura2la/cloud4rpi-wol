# -*- encoding: utf-8 -*-

import subprocess
import wakeonlan

wol_target_mac = 'FF-FF-FF-FF-FF-FF'
wol_target_host = 'himura-pc'

def ping():
    try:
	out = subprocess.check_output(['ping', '-W', '2', '-c', '1', wol_target_host])
	if '1 received' in out:
            return out.split('bytes from ', 1)[1].split(':', 1)[0]
        return 'Offline'
    except subprocess.CalledProcessError:
        return 'Offline'


def wake():
    for _ in range(3):
	wakeonlan.send_magic_packet(wol_target_mac)

