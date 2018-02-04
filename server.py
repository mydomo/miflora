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

        string_devices_to_analize = input_string.replace("miflora_devices: ", "").strip()
        # split each MAC address in a list in order to be processed
        devices_to_analize = string_devices_to_analize.split(',')

        if len(devices_to_analize) >= 1:

            for device in devices_to_analize:

                battery_level_moderator =  str(batt_lev_detected.get(device, "Never"))
                # cleaning the value stored
                cleaned_battery_level_moderator = str(battery_level_moderator.replace("[", "").replace("]", "").replace(" ", "").replace("'", ""))
                # assign the battery level and the timestamp to different variables
                if cleaned_battery_level_moderator == "Never":
                    batt_need_update = True
                    #print("ASK: Battery of: " + device + " has not previously scanned, starting now.")

                if cleaned_battery_level_moderator != "Never":
                    # DEVICE HAS A PREVIOUS STORED BATTERY LEVEL
                    stored_batterylevel, stored_timestamp = cleaned_battery_level_moderator.split(',')
                    time_difference = int(time.time()) - int(stored_timestamp)
                    #print("ASK: Battery of: " + str(device) + " has being scanned: " + str(time_difference) + " seconds ago.")
                    if ( (int(time_difference) >= int(min_inval_between_batt_level_readings)) or (str(stored_batterylevel) == '255') ):
                        batt_need_update = True
                        #print(device + " battery level need an update! Doing now!")

            if batt_need_update == True and read_value_lock == True:
                return str(lang_READING_LOCK)

            if batt_need_update == True and read_value_lock == False:
                return str(lang_READING_START)

            if batt_need_update == False:
                return str(batt_lev_detected)
        else:
            mode = 'beacon_data'

def input_string_config(string):
    output = string.replace("miflora_client: ", "").strip().split('$')
    return output[0]


def input_string_devices(string):
    output = string.replace("miflora_client: ", "").strip().split('$')
    return output[1]



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
    input_string_fake = "miflora_client: 180,hci1$C4:7C:8D:65:E2:1A,C4:7C:8D:65:E2:2A"

    print(input_string_config(input_string_fake))
    print(input_string_devices(input_string_fake))


if __name__ == '__main__':
    main()
