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

def socket_input_process(input_string):
    global devices_to_analize

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
                requested_device = str(miflora_plant.get(device, "Never"))

                # if device requested was polled before extract all the data
                if requested_device != "Never":
                    requested_device_data = device_string_cleaned(requested_device).split(',')

                    requested_device_mac = device
                    requested_device_fw = requested_device_data[0]
                    requested_device_name = requested_device_data[1]
                    requested_device_temp = requested_device_data[2]
                    requested_device_moist = requested_device_data[3]
                    requested_device_light = requested_device_data[4]
                    requested_device_cond = requested_device_data[5]
                    requested_device_batt = requested_device_data[6]
                    requested_device_timestamp = requested_device_data[7]

                    # check time since last poll
                    time_difference = int(time.time()) - int(requested_device_timestamp)
                    # time difference is greater than the interval between polling.
                    if time_difference >= (srv_polling_time * 60):
                        # poll again
                        poller = MiFloraPoller(requested_device_mac, srv_backend, adapter=srv_adapter)

                        polled_device_fw = poller.firmware_version()
                        polled_device_name = poller.name()
                        polled_device_temp = poller.parameter_value(MI_TEMPERATURE)
                        polled_device_moist = poller.parameter_value(MI_MOISTURE)
                        polled_device_light = abs(poller.parameter_value(MI_LIGHT))
                        polled_device_cond = poller.parameter_value(MI_CONDUCTIVITY)
                        polled_device_batt = poller.parameter_value(MI_BATTERY)
                        polled_device_timestamp = int(time.time())

                        miflora_plant[requested_device_mac] = [polled_device_fw,polled_device_name,polled_device_temp,polled_device_moist,polled_device_light,polled_device_cond,polled_device_batt,polled_device_timestamp]

                if requested_device == "Never":
                    # poll for the first time this device
                    poller = MiFloraPoller(requested_device_mac, srv_backend, adapter=srv_adapter)

                    polled_device_fw = poller.firmware_version()
                    polled_device_name = poller.name()
                    polled_device_temp = poller.parameter_value(MI_TEMPERATURE)
                    polled_device_moist = poller.parameter_value(MI_MOISTURE)
                    polled_device_light = abs(poller.parameter_value(MI_LIGHT))
                    polled_device_cond = poller.parameter_value(MI_CONDUCTIVITY)
                    polled_device_batt = poller.parameter_value(MI_BATTERY)
                    polled_device_timestamp = int(time.time())

                    miflora_plant[requested_device_mac] = [polled_device_fw,polled_device_name,polled_device_temp,polled_device_moist,polled_device_light,polled_device_cond,polled_device_batt,polled_device_timestamp]


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
    """ Poll data from the sensor.
        MiFloraPoller library can read the following parameters: mac, backend, cache_timeout=600, retries=3, adapter='hci0'
    """
    poller = MiFloraPoller(mac, backend, adapter=ble_adapter)
    """ DEMO MODE: PRINT OUTS THE RESULT
    print("Getting data from Mi Flora")
    print("FW: {}".format(poller.firmware_version()))
    print("Name: {}".format(poller.name()))
    print("Temperature: {}".format(poller.parameter_value(MI_TEMPERATURE)))
    print("Moisture: {}".format(poller.parameter_value(MI_MOISTURE)))
    print("Light: {}".format(abs(poller.parameter_value(MI_LIGHT))))
    print("Conductivity: {}".format(poller.parameter_value(MI_CONDUCTIVITY)))
    print("Battery: {}".format(poller.parameter_value(MI_BATTERY)))
    """
    temperature_value = poller.parameter_value(MI_TEMPERATURE)
    moisture_value = poller.parameter_value(MI_MOISTURE)
    light_value = abs(poller.parameter_value(MI_LIGHT))
    conductivity_value = poller.parameter_value(MI_CONDUCTIVITY)
    battery_value = poller.parameter_value(MI_BATTERY)


def main():
    """ Main function.

    """

    #poll('C4:7C:8D:65:E2:1A', GatttoolBackend, 'hci1')
    input_string_fake = "miflora_client: 180,GatttoolBackend,hci1$|$C4:7C:8D:65:E2:1A"

    while True:
        print(socket_input_process(input_string_fake))
        sleep(1)


if __name__ == '__main__':
    main()
