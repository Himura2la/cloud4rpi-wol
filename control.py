# -*- coding: utf-8 -*-
#
# Cloud4RPi Example for Next Thing Co. C.H.I.P.
# =============================================
#
# This example demonstrates different scenarios of using Cloud4RPi service
# on C.H.I.P.:
#
# - Monitoring events
# - Controling a GPIO pin
# - Monitoring temperature with the DS18B20 sensor
#
# For complete instructions on how to run this example, refer
# to the [How To](https://cloud4rpi.github.io/docs/howto/) article.
#
# The DS18B20 sensor should be connected as follows:
#
#  / GND |────────────> GND
# | DATA |─────────┬──> LCD-D2
#  \ VCC |─┬─[4k7]─┘
#          └──────────> 5V
#  DS18B20 (bottom view)

from os import uname
from socket import gethostname
from time import sleep
import sys
import random
import cloud4rpi
import chip
import ds18b20
import wol

DEVICE_TOKEN = '__MEMENTO_TOKEN__'

# Constants
DATA_SENDING_INTERVAL = 30  # secs
DIAG_SENDING_INTERVAL = 60  # secs
POLL_INTERVAL = 0.5  # secs


def wake_pc(value):
    if value:
	return wol.wake()

def ping_pc(value):
    return wol.ping()


def main():
    # load w1 modules
    ds18b20.init_w1()

    # Detect DS18B20 temperature sensors.
    ds_sensors = ds18b20.DS18b20.find_all()

    # Put variable declarations here
    variables = {
        'Outside Temp': {
            'type': 'numeric',
            'bind': ds_sensors[0] if ds_sensors else None
        },
        'PC IP': {
            'type': 'string',
            'value': False,
            'bind': ping_pc,
        },
        'PC WoL': {
            'type': 'bool',
            'value': False,
            'bind': wake_pc,
        },
        'CPU Temp': {
            'type': 'numeric',
            'bind': chip.cpu_temp
        }
    }

    # Put system data declarations here
    diagnostics = {
        'IP Address': chip.ip_address,
        'Host': gethostname(),
        'Operating System': " ".join(uname())
    }

    device = cloud4rpi.connect(DEVICE_TOKEN)
    device.declare(variables)
    device.declare_diag(diagnostics)

    device.publish_config()

    # adds a 1 second delay to ensure device variables are created
    sleep(1)

    try:
        diag_timer = 0
        data_timer = 0
        while True:
            if data_timer <= 0:
                device.publish_data()
                data_timer = DATA_SENDING_INTERVAL

            if diag_timer <= 0:
                device.publish_diag()
                diag_timer = DIAG_SENDING_INTERVAL

            diag_timer -= POLL_INTERVAL
            data_timer -= POLL_INTERVAL
            sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        cloud4rpi.log.info('Keyboard interrupt received. Stopping...')

    except Exception as e:
        error = cloud4rpi.get_error_message(e)
        cloud4rpi.log.error("ERROR! %s %s", error, sys.exc_info()[0])
        sys.exit(1)

    finally:
        sys.exit(0)


if __name__ == '__main__':
    main()
