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

global miflora_plant
miflora_plant = {}
global srv_backend
srv_backend = ''
global srv_adapter
srv_adapter = ''
global srv_polling_err
srv_polling_err = ''
global srv_polling_timeout
srv_polling_timeout = ''

def socket_input_process(input_string):

    if input_string.startswith('miflora_client:'):

        # server configuration
        server_configuration = input_string_config(input_string).split(',')
        # polling time (in minutes)
        srv_polling_time = int(server_configuration[0])
        # backend (default: GatttoolBackend)
        srv_backend = server_configuration[1]
        # adapter (default: hci0)
        srv_adapter = server_configuration[2]
        # time to wait before polling again a device that had an error during the reading (in minutes)
        srv_polling_err = server_configuration[3]
        # time to wait before stopping polling a device since the last request (in minutes)
        srv_polling_timeout = server_configuration[4]

        # split each MAC address in a list in order to be processed
        devices_to_analize = input_string_devices(input_string).split(',')

        if len(devices_to_analize) >= 1:

            for device in devices_to_analize:

                # check if the device requested has already polled
                requested_device = str(miflora_plant.get(device, 'Never'))

                if (requested_device == 'Never'):
                # device is asked for the first time, need to get the values .
                    polled_device_status = 'REQUESTED'
                    polled_device_fw = '?'
                    polled_device_name = '?'
                    polled_device_temp = '?'
                    polled_device_moist = '?'
                    polled_device_light = '?'
                    polled_device_cond = '?'
                    polled_device_batt = '?'
                    polled_device_timestamp = int(time.time())
                    polled_device_timeasked = int(time.time())

                    miflora_plant[device] = [polled_device_status,polled_device_fw,polled_device_name,polled_device_temp,polled_device_moist,polled_device_light,polled_device_cond,polled_device_batt,polled_device_timestamp,polled_device_timeasked]

                
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
                    requested_device_timeasked = int(time.time())

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
                            polled_device_timestamp = requested_device_timestamp
                            polled_device_timeasked = int(time.time())

                            miflora_plant[device] = [polled_device_status,polled_device_fw,polled_device_name,polled_device_temp,polled_device_moist,polled_device_light,polled_device_cond,polled_device_batt,polled_device_timestamp,polled_device_timeasked]

def device_poller():
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
                requested_device_timeasked = requested_device_data[9]

                # Check that the last time the device was asked is less than the polling timeout.
                if (time_difference(requested_device_timeasked) < (srv_polling_timeout * 60)):
                    if (requested_device_status == 'REQUESTED') or (requested_device_status == 'EXPIRED'):
                        poller = poll(device, srv_backend, srv_adapter, requested_device_timeasked)
                    if requested_device_status == 'ERROR':
                        if (time_difference(requested_device_timestamp) >= (srv_polling_err * 60)):
                            poller = poll(device, srv_backend, srv_adapter, requested_device_timeasked)
                # If the polling timeout has being reached delete from the device dictionary the key.
                if (time_difference(requested_device_timeasked) >= (srv_polling_timeout * 60)):
                    miflora_plant.pop(device, None)

        time.sleep(1)

def time_difference(timestamp):
    output = int(time.time()) - int(timestamp)
    return output

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


def poll(mac, backend, ble_adapter, requested_device_timeasked):
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
        polled_device_timeasked = requested_device_timeasked
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
        polled_device_timeasked = requested_device_timeasked


    miflora_plant[mac] = [polled_device_status,polled_device_fw,polled_device_name,polled_device_temp,polled_device_moist,polled_device_light,polled_device_cond,polled_device_batt,polled_device_timestamp,polled_device_timeasked]



def main():
    """ Main function.

    """
    input_string_fake = "miflora_client: 1,GatttoolBackend,hci1,10,5$|$C4:7C:8D:65:E2:1A"
    input_string_fake2 = "miflora_client: 1,GatttoolBackend,hci1,10,5$|$C4:7C:8D:65:E2:1A,C4:7C:8D:65:E2:1B"

    socket_input_process(input_string_fake2)
    while True:
        socket_input_process(input_string_fake)
        print(miflora_plant)
        time.sleep(1)


if __name__ == '__main__':
    Thread(target=main).start()
    Thread(target=device_poller).start()

