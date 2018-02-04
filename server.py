#!/usr/bin/env python3
"""Demo file showing how to use the miflora library."""
import socket
from threading import Thread
import os
import time
import re
from collections import OrderedDict

##########- MIFLORA SCRIPT -##########
import argparse
import re
import logging
import sys

from miflora.miflora_poller import MiFloraPoller, \
    MI_CONDUCTIVITY, MI_MOISTURE, MI_LIGHT, MI_TEMPERATURE, MI_BATTERY
from miflora import miflora_scanner, available_backends, BluepyBackend, GatttoolBackend, PygattBackend
##########- END MIFLORA SCRIPT -##########


##########- CONFIGURE SCRIPT -##########
socket_ip = '0.0.0.0'
socket_port = 54321

miflora_plant = {}

def socket_input_process(input_string):
    global miflora_plant
    global srv_backend
    global srv_adapter

    if input_string.startswith('miflora_client:'):

        # server configuration
        server_configuration = input_string_config(input_string).split(',')
        # polling time (in minutes)
        srv_polling_time = int(server_configuration[0])
        # backend (default: GatttoolBackend)
        srv_backend = server_configuration[1]
        # adapter (default: hci0)
        srv_adapter = server_configuration[2]

        # split each MAC address in a list in order to be processed
        devices_to_analize = input_string_devices(input_string).split(',')

        if len(devices_to_analize) >= 1:

            for device in devices_to_analize:

                # check if the device requested has already polled
                requested_device = str(miflora_plant.get(device, 'Never'))

                if (requested_device == 'Never'):
                # device is asked for the first time, need to get the values .
                    polled_device_status = 'TOBEUPDATED'
                    polled_device_fw = '?'
                    polled_device_name = '?'
                    polled_device_temp = '?'
                    polled_device_moist = '?'
                    polled_device_light = '?'
                    polled_device_cond = '?'
                    polled_device_batt = '?'
                    polled_device_timestamp = int(time.time())

                    miflora_plant[device] = [polled_device_status,polled_device_fw,polled_device_name,polled_device_temp,polled_device_moist,polled_device_light,polled_device_cond,polled_device_batt,polled_device_timestamp]

                
                if requested_device != 'Never':
                # device already polled, gather all the available data.
                    requested_device_data = device_string_cleaned(requested_device).split(',')

                    requested_device_status = requested_device_data[0]
                    requested_device_fw = requested_device_data[1]
                    requested_device_name = requested_device_data[2]
                    requested_device_temp = requested_device_data[3]
                    requested_device_moist = requested_device_data[4]
                    requested_device_light = requested_device_data[5]
                    requested_device_cond = requested_device_data[6]
                    requested_device_batt = requested_device_data[7]
                    requested_device_timestamp = requested_device_data[8]

                    if requested_device_status == 'OK':
                        # check time since last poll
                        time_difference = int(time.time()) - int(requested_device_timestamp)
                        # time difference is greater than the interval between polling.
                        if (time_difference >= (srv_polling_time * 60)):
                            polled_device_status = 'EXPIRED'
                            polled_device_fw = requested_device_fw
                            polled_device_name = requested_device_name
                            polled_device_temp = requested_device_temp
                            polled_device_moist = requested_device_moist
                            polled_device_light = requested_device_light
                            polled_device_cond = requested_device_cond
                            polled_device_batt = requested_device_batt
                            polled_device_timestamp = int(time.time())

                            miflora_plant[device] = [polled_device_status,polled_device_fw,polled_device_name,polled_device_temp,polled_device_moist,polled_device_light,polled_device_cond,polled_device_batt,polled_device_timestamp]

def device_poller():
    global miflora_plant
    while True:
        for device in miflora_plant:
            requested_device = str(miflora_plant.get(device, 'Never'))
            if requested_device != 'Never':
                # device exist, gather all the available data.
                requested_device_data = device_string_cleaned(requested_device).split(',')

                requested_device_status = requested_device_data[0]
                requested_device_fw = requested_device_data[1]
                requested_device_name = requested_device_data[2]
                requested_device_temp = requested_device_data[3]
                requested_device_moist = requested_device_data[4]
                requested_device_light = requested_device_data[5]
                requested_device_cond = requested_device_data[6]
                requested_device_batt = requested_device_data[7]
                requested_device_timestamp = requested_device_data[8]

                if requested_device_status != 'OK':
                    poller = poll(device, srv_backend, srv_adapter)
        time.sleep(1)


def input_string_stripped(string):
    output = string.replace("miflora_client: ", "").strip()
    return output

def input_string_config(string):
    output = input_string_stripped(string).split('$|$')
    return output[0]


def input_string_devices(string):
    output = input_string_stripped(string).split('$|$')
    return output[1]

def device_string_cleaned(string):
    output = str(string.replace("[", "").replace("]", "").replace(" ", "").replace("'", ""))
    return output



##########- MIFLORA SCRIPT -##########
def valid_miflora_mac(mac, pat=re.compile(r"C4:7C:8D:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}")):
    """Check for valid mac adresses."""
    if not pat.match(mac.upper()):
        raise argparse.ArgumentTypeError('The MAC address "{}" seems to be in the wrong format'.format(mac))
    return mac


def poll(mac, backend, ble_adapter):
    global miflora_plant
    """ Poll data from the sensor.
        MiFloraPoller library can read the following parameters: mac, backend, cache_timeout=600, retries=3, adapter='hci0'
    """
    try:
        poller = MiFloraPoller(mac, GatttoolBackend, adapter=ble_adapter)

        polled_device_status = 'OK'
        polled_device_fw = poller.firmware_version()
        polled_device_name = poller.name()
        polled_device_temp = poller.parameter_value(MI_TEMPERATURE)
        polled_device_moist = poller.parameter_value(MI_MOISTURE)
        polled_device_light = abs(poller.parameter_value(MI_LIGHT))
        polled_device_cond = poller.parameter_value(MI_CONDUCTIVITY)
        polled_device_batt = poller.parameter_value(MI_BATTERY)
        polled_device_timestamp = int(time.time())
    except:
        polled_device_status = 'ERROR'
        polled_device_fw = '?'
        polled_device_name = '?'
        polled_device_temp = '?'
        polled_device_moist = '?'
        polled_device_light = '?'
        polled_device_cond = '?'
        polled_device_batt = '?'
        polled_device_timestamp = int(time.time())


    miflora_plant[mac] = [polled_device_status,polled_device_fw,polled_device_name,polled_device_temp,polled_device_moist,polled_device_light,polled_device_cond,polled_device_batt,polled_device_timestamp]



def main():
    """ Main function.

    """

    #poll('C4:7C:8D:65:E2:1A', GatttoolBackend, 'hci1')
    input_string_fake = "miflora_client: 1,GatttoolBackend,hci1$|$C4:7C:8D:65:E2:1A,C4:7C:8D:65:E2:1B"

    while True:
        socket_input_process(input_string_fake)
        print(miflora_plant)
        time.sleep(1)


if __name__ == '__main__':
    Thread(target=main).start()
    Thread(target=device_poller).start()

