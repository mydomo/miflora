#!/usr/bin/env python3
"""Demo file showing how to use the miflora library."""

import argparse
import re
import logging
import sys

from miflora.miflora_poller import MiFloraPoller, \
    MI_CONDUCTIVITY, MI_MOISTURE, MI_LIGHT, MI_TEMPERATURE, MI_BATTERY

def valid_miflora_mac(mac, pat=re.compile(r"C4:7C:8D:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}")):
    """Check for valid mac adresses."""
    if not pat.match(mac.upper()):
        raise argparse.ArgumentTypeError('The MAC address "{}" seems to be in the wrong format'.format(mac))
    return mac


def poll(mac, adapter):
    """Poll data from the sensor."""
    poller = MiFloraPoller(mac, adapter)
    print("Getting data from Mi Flora")
    print("FW: {}".format(poller.firmware_version()))
    print("Name: {}".format(poller.name()))
    print("Temperature: {}".format(poller.parameter_value(MI_TEMPERATURE)))
    print("Moisture: {}".format(poller.parameter_value(MI_MOISTURE)))
    print("Light: {}".format(poller.parameter_value(MI_LIGHT)))
    print("Conductivity: {}".format(poller.parameter_value(MI_CONDUCTIVITY)))
    print("Battery: {}".format(poller.parameter_value(MI_BATTERY)))



def main():
    """Main function.

    """

    print ('hci1')
    poll('C4:7C:8D:65:E2:1A','hci1')


if __name__ == '__main__':
    main()
