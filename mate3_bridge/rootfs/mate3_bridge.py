#!/usr/bin/env python

AP_DESCRIPTION="""
Publish Radian data stream information to Home Assistant.
"""

AP_EPILOG="""
RunTEST
"""

import argparse
import json
import logging
import paho.mqtt.client as mqtt
import socket
import time

registered_devices = {}

radian_keys = {
    'l1_inv_a',
    'l1_chg_a',
    'l1_buy_a',
    'l1_sell_a',
    'l1_grid_input_v',
    'l1_gen_input_v',
    'l1_output_v',
    'l2_inv_a',
    'l2_chg_a',
    'l2_buy_a',
    'l2_selling_a',
    'l2_grid_input_v',
    'l2_gen_input_v',
    'l2_output_v',
    'inverter_mode',
    'inverter_err',
    'ac_mode',
    'battery_v',
    'misc',
    'inverter_warn',

    "l1_inv_w",
    "l1_chg_w",
    "l1_buy_w",
    "l1_sell_w",
    "l2_inv_w",
    "l2_chg_w",
    "l2_buy_w",
    "l2_sell_w",
}

radian_mappings = {
    "l1_inv_a": {
        "object_id": "l1_inv_a",
        "config": {
            "device_class": "current",
            "name": "L1 Inverter Current",
            "unit_of_measurement": "A",
            "value_template": "{{ value }}",
            "state_class": "measurement",
        }
    },

    "l1_chg_a": {
        "object_id": "l1_chg_a",
        "config": {
            "device_class": "current",
            "name": "L1 Charger Current",
            "unit_of_measurement": "A",
            "value_template": "{{ value }}",
            "state_class": "measurement",
        }
    },

    "l1_buy_a": {
        "object_id": "l1_buy_a",
        "config": {
            "device_class": "current",
            "name": "L1 Buying Current",
            "unit_of_measurement": "A",
            "value_template": "{{ value }}",
            "state_class": "measurement",
        }
    },

    "l1_sell_a": {
        "object_id": "l1_sell_a",
        "config": {
            "device_class": "current",
            "name": "L1 Selling Current",
            "unit_of_measurement": "A",
            "value_template": "{{ value }}",
            "state_class": "measurement",
        }
    },

    "l1_grid_input_v": {
        "object_id": "l1_grid_input_v",
        "config": {
            "device_class": "voltage",
            "name": "L1 Grid Voltage",
            "unit_of_measurement": "V",
            "value_template": "{{ value }}",
            "state_class": "measurement",
        }
    },

    "l1_gen_input_v": {
        "object_id": "l1_gen_input_v",
        "config": {
            "device_class": "voltage",
            "name": "L1 Generator Voltage",
            "unit_of_measurement": "V",
            "value_template": "{{ value }}",
            "state_class": "measurement",
        }
    },

    "l1_output_v": {
        "object_id": "l1_output_v",
        "config": {
            "device_class": "voltage",
            "name": "L1 Output Voltage",
            "unit_of_measurement": "V",
            "value_template": "{{ value }}",
            "state_class": "measurement",
        }
    },

    "l2_inv_a": {
        "object_id": "l2_inv_a",
        "config": {
            "device_class": "current",
            "name": "L2 Inverter Current",
            "unit_of_measurement": "A",
            "value_template": "{{ value }}",
            "state_class": "measurement",
        }
    },

    "l2_chg_a": {
        "object_id": "l2_chg_a",
        "config": {
            "device_class": "current",
            "name": "L2 Charger Current",
            "unit_of_measurement": "A",
            "value_template": "{{ value }}",
            "state_class": "measurement",
        }
    },

    "l2_buy_a": {
        "object_id": "l2_buy_a",
        "config": {
            "device_class": "current",
            "name": "L2 Buying Current",
            "unit_of_measurement": "A",
            "value_template": "{{ value }}",
            "state_class": "measurement",
        }
    },

    "l2_selling_a": {
        "object_id": "l2_selling_a",
        "config": {
            "device_class": "current",
            "name": "L2 Selling Current",
            "unit_of_measurement": "A",
            "value_template": "{{ value }}",
            "state_class": "measurement",
        }
    },

    "l2_grid_input_v": {
        "object_id": "l2_grid_input_v",
        "config": {
            "device_class": "current",
            "name": "L2 Grid Voltage",
            "unit_of_measurement": "V",
            "value_template": "{{ value }}",
            "state_class": "measurement",
        }
    },

    "l2_gen_input_v": {
        "object_id": "l2_gen_input_v",
        "config": {
            "device_class": "voltage",
            "name": "L2 Generator Voltage",
            "unit_of_measurement": "V",
            "value_template": "{{ value }}",
            "state_class": "measurement",
        }
    },

    "l2_output_v": {
        "object_id": "l2_output_v",
        "config": {
            "device_class": "voltage",
            "name": "L2 Output Voltage",
            "unit_of_measurement": "V",
            "value_template": "{{ value }}",
            "state_class": "measurement",
        }
    },

    "inverter_mode": {
        "object_id": "inverter_mode",
        "config": {
            "device_class": "enum",
            "name": "Inverter Operating Mode",
            "state_class": "measurement",
            "entity_category": "diagnostic",
            "options": [
                "Inverter Off",
                "Inverter Searching",
                "Inverter Active",
                "Bulk Charging",
                "Quiescent Charging",
                "Float Charging",
                "Equalize Charging",
                "Charger Disabled",
                "AC Support Mode",
                "Selling Power",
                "Pass-through Mode",
                "Stacked Inverter Active",
                "Stacked Inverter Inactive",
                "AC Offset Mode",
                "Inverter Error",
                "Generator Error",
                "Communication Error"
            ],
        }
    },

    "inverter_err": {
        "object_id": "inverter_err",
        "config": {
            "device_class": "enum",
            "name": "Inverter Error State",
            "state_class": "measurement",
            "entity_category": "diagnostic",
        }
    },

    "ac_mode": {
        "object_id": "ac_mode",
        "config": {
            "device_class": "enum",
            "name": "Inverter AC Mode",
            "state_class": "measurement",
            "entity_category": "diagnostic",
            "options": ["No AC Available", "AC Invalid", "AC In Use"],
        }
    },

    "battery_v": {
        "object_id": "battery_v",
        "config": {
            "device_class": "voltage",
            "name": "Battery Voltage",
            "unit_of_measurement": "V",
            "value_template": "{{ value|float }}",
            "state_class": "measurement",
        }
    },

    "misc": {
        "object_id": "misc",
        "config": {
            "device_class": "enum",
            "name": "Inverter Misc Status",
            "state_class": "measurement",
            "entity_category": "diagnostic",
        }
    },

    "inverter_warn": {
        "object_id": "inverter_warn",
        "config": {
            "device_class": "enum",
            "name": "Inverter Warning Status",
            "state_class": "measurement",
            "entity_category": "diagnostic",
        }
    },

    "l1_inv_w": {
        "object_id": "l1_inv_w",
        "config": {
            "device_class": "power",
            "name": "L1 Inverter Wattage",
            "unit_of_measurement": "W",
            "value_template": "{{ value }}",
            "state_class": "measurement",
        }
    },

    "l1_chg_w": {
        "object_id": "l1_chg_w",
        "config": {
            "device_class": "power",
            "name": "L1 Charger Wattage",
            "unit_of_measurement": "W",
            "value_template": "{{ value }}",
            "state_class": "measurement",
        }
    },

    "l1_buy_w": {
        "object_id": "l1_buy_w",
        "config": {
            "device_class": "power",
            "name": "L1 Buying Wattage",
            "unit_of_measurement": "W",
            "value_template": "{{ value }}",
            "state_class": "measurement",
        }
    },

    "l1_sell_w": {
        "object_id": "l1_sell_w",
        "config": {
            "device_class": "power",
            "name": "L1 Selling Wattage",
            "unit_of_measurement": "W",
            "value_template": "{{ value }}",
            "state_class": "measurement",
        }
    },

    "l2_inv_w": {
        "object_id": "l2_inv_w",
        "config": {
            "device_class": "power",
            "name": "L2 Inverter Wattage",
            "unit_of_measurement": "W",
            "value_template": "{{ value }}",
            "state_class": "measurement",
        }
    },

    "l2_chg_w": {
        "object_id": "l2_chg_w",
        "config": {
            "device_class": "power",
            "name": "L2 Charger Wattage",
            "unit_of_measurement": "W",
            "value_template": "{{ value }}",
            "state_class": "measurement",
        }
    },

    "l2_buy_w": {
        "object_id": "l2_buy_w",
        "config": {
            "device_class": "power",
            "name": "L2 Buying Wattage",
            "unit_of_measurement": "W",
            "value_template": "{{ value }}",
            "state_class": "measurement",
        }
    },

    "l2_sell_w": {
        "object_id": "l2_sell_w",
        "config": {
            "device_class": "power",
            "name": "L2 Selling Wattage",
            "unit_of_measurement": "W",
            "value_template": "{{ value }}",
            "state_class": "measurement",
        }
    },
}

def mqtt_connect(client, userdata, flags, rc):
    """Handle MQTT connection callback."""
    logging.info("MQTT connected: " + mqtt.connack_string(rc))

def mqtt_disconnect(client, userdata, rc):
    """Handle MQTT disconnection callback."""
    logging.info("MQTT disconnected: " + mqtt.connack_string(rc))

def publish_config(port, device, uuid, mappings, keys):
    """Publish Home Assistant auto discovery data."""

    if uuid in registered_devices:
        if registered_devices[uuid] > time.time():
            logging.debug("Push time is in the future for uuid: " + uuid)
            return False

    for key in keys:
        mapping = mappings[key]
        object_id = mapping["object_id"]
        path = "/".join([args.discovery, "sensor", port + "-" + device, object_id, "config"])

        config = mapping["config"].copy()

        config["state_topic"] = "/".join([MQTT_PREFIX, port + "-" + device, object_id])
        config["unique_id"] = "-".join([uuid, port, device, object_id])
        config["device"] = { "identifiers": device, "name": device, "model": device, "manufacturer": "Outback Power" }
        logging.debug(path + ":" + json.dumps(config))

        mqttc.publish(path, json.dumps(config), retain=True)

    registered_devices[uuid] = time.time() + 600

    return True

def radianDeviceType(devtype):
    if devtype == "2":
        devtype = "FX_Inverter"
    elif devtype == "3":
        devtype = "Charge_Controller"
    elif devtype == "6":
        devtype = "Radian_Inverter"
    else:
        devtype = "Unknown"

    return devtype

def radianModeConv(mode):
    if mode == "00":
        mode = "Inverter Off"
    elif mode == "01":
        mode = "Inverter Searching"
    elif mode == "02":
        mode = "Inverter Active"
    elif mode == "03":
        mode = "Bulk Charging"
    elif mode == "04":
        mode = "Silent Charging"
    elif mode == "05":
        mode = "Float Charging"
    elif mode == "06":
        mode = "Equalize Charging"
    elif mode == "07":
        mode = "Charger Disabled"
    elif mode == "08":
        mode = "AC Support Mode"
    elif mode == "09":
        mode = "Selling Power"
    elif mode == "10":
        mode = "Pass-through Mode"
    elif mode == "11":
        mode = "Stacked Inverter Active"
    elif mode == "12":
        mode = "Stacked Inverter Inactive"
    elif mode == "14":
        mode = "AC Offset Mode"
    elif mode == "90":
        mode = "Inverter Error"
    elif mode == "91":
        mode = "Generator Error"
    elif mode == "92":
        mode = "Communication Error"

    return mode

def radianErrorConv(err):
    tmp_err = int(err)
    err = []
    if tmp_err & 0b00000001:
        err.append("AC Output Low")
    if tmp_err & 0b00000010:
        err.append("Stacking Error")
    if tmp_err & 0b00000100:
        err.append("Inverter Over Temperature")
    if tmp_err & 0b00001000:
        err.append("Battery Voltage Low")
    if tmp_err & 0b00010000:
        err.append("Communication Fault")
    if tmp_err & 0b00100000:
        err.append("Battery Voltage High")
    if tmp_err & 0b01000000:
        err.append("AC Output Shorted")
    if tmp_err & 0b10000000:
        err.append("Backfeed")
    if tmp_err == 0b0:
        err.append("None")

    return ", ".join(err)

def radianACModeConv(acmode):
    if acmode == "00":
        acmode = "No AC Available"
    elif acmode == "01":
        acmode = "AC Invalid"
    elif acmode == "02":
        acmode = "AC In Use"

    return acmode

def radianMiscConv(misc):
    tmp_misc = int(misc)
    misc = []
    if tmp_misc & 0b00000001:
        misc.append("Reserved 1")
    if tmp_misc & 0b00000010:
        misc.append("Reserved 2")
    if tmp_misc & 0b00000100:
        misc.append("Reserved 4")
    if tmp_misc & 0b00001000:
        misc.append("Reserved 8")
    if tmp_misc & 0b00010000:
        misc.append("Aux Output Enabled")
    else:
        misc.append("Aux Output Disabled")
    if tmp_misc & 0b00100000:
        misc.append("Relay Output Enabled")
    else:
        misc.append("Relay Output Disabled")
    if tmp_misc & 0b01000000:
        misc.append("AC 2 Selected")
    else:
        misc.append("AC 1 Selected")
    if tmp_misc & 0b10000000:
        misc.append("240 VAC Mode")
    else:
        misc.append("120 VAC Mode")

    return ", ".join(misc)

def radianWarningConv(warn):
    tmp_warn = int(warn)
    warn = []
    if tmp_warn & 0b00000001:
        warn.append("AC Input Frequency High")
    if tmp_warn & 0b00000010:
        warn.append("AC Input Frequency Low")
    if tmp_warn & 0b00000100:
        warn.append("AC Input Voltage High")
    if tmp_warn & 0b00001000:
        warn.append("AC Input Voltage Low")
    if tmp_warn & 0b00010000:
        warn.append("Buy Amperage Overload")
    if tmp_warn & 0b00100000:
        warn.append("Temperature Sensor Failed")
    if tmp_warn & 0b01000000:
        warn.append("Phase Loss")
    if tmp_warn & 0b10000000:
        warn.append("Fan Failure")
    if tmp_warn == 0b0:
        warn.append("None")

    return ", ".join(warn)

def radianVoltageConv(volt, misc):
    misc = int(misc)
    volt = int(volt)
    if misc & 0b10000000:
        return volt * 2
    else:
        return volt

def radianProcessData(data, mac):
    if len(data) < 22:
        logging.error("Insufficient data received: %s" %len(data))
        return

    if data[0] != "01":
        logging.error("Only port 1 is supported right now")
        return

# Input voltages need to be processed based on misc inverter mode
    data[6] = radianVoltageConv(data[6], data[20])
    data[7] = radianVoltageConv(data[7], data[20])
    data[8] = radianVoltageConv(data[8], data[20])
    data[13] = radianVoltageConv(data[13], data[20])
    data[14] = radianVoltageConv(data[14], data[20])
    data[15] = radianVoltageConv(data[15], data[20])

# Battery Voltage is a float, divide by 10
    data[19] = float(data[19]) / 10

# Process Devtype, Inverter Modes, Error Codes, AC Mode, Misc Codes, and Warnings
    data[0] = "port_" + data[0]
    data[1] = radianDeviceType(data[1])
    data[16] = radianModeConv(data[16])
    data[17] = radianErrorConv(data[17])
    data[18] = radianACModeConv(data[18])
    data[20] = radianMiscConv(data[20])
    data[21] = radianWarningConv(data[21])

    logging.debug("port: %s" %data[0])
    logging.debug("devtype: %s" %data[1])
    logging.debug("L1 Inv current: %s A" %data[2])
    logging.debug("L1 Chg current: %s A" %data[3])
    logging.debug("L1 Buy current: %s A" %data[4])
    logging.debug("L1 Sell current: %s A" %data[5])
    logging.debug("L1 Grid Input Voltage: %s VAC" %data[6])
    logging.debug("L1 Gen Input Voltage: %s VAC" %data[7])
    logging.debug("L1 Output Voltage: %s VAC" %data[8])
    logging.debug("L2 Inv current: %s A" %data[9])
    logging.debug("L2 Chg current: %s A" %data[10])
    logging.debug("L2 Buy current: %s A" %data[11])
    logging.debug("L2 Sell current: %s A" %data[12])
    logging.debug("L2 Grid Input Voltage: %s VAC" %data[13])
    logging.debug("L2 Gen Input Voltage: %s VAC" %data[14])
    logging.debug("L2 Output Voltage: %s VAC" %data[15])
    logging.debug("Inverter Mode: %s" %data[16])
    logging.debug("Error: %s" %data[17])
    logging.debug("AC mode: %s" %data[18])
    logging.debug("Battery Voltage: %s VDC" %data[19])
    logging.debug("Misc: %s" %data[20])
    logging.debug("Warnings: %s" %data[21])

    path = "/".join([MQTT_PREFIX, data[0] + "-" + data[1].replace(" ", "_")])

    publish_config(data[0], data[1].replace(" ", "_"), mac, radian_mappings, radian_keys)

    mqttc.publish(path +"/l1_inv_a", data[2])
    mqttc.publish(path +"/l1_chg_a", data[3])
    mqttc.publish(path +"/l1_buy_a", data[4])
    mqttc.publish(path +"/l1_sell_a", data[5])
    mqttc.publish(path +"/l1_grid_input_v", data[6])
    mqttc.publish(path +"/l1_gen_input_v", data[7])
    mqttc.publish(path +"/l1_output_v", data[8])
    mqttc.publish(path +"/l2_inv_a", data[9])
    mqttc.publish(path +"/l2_chg_a", data[10])
    mqttc.publish(path +"/l2_buy_a", data[11])
    mqttc.publish(path +"/l2_selling_a", data[12])
    mqttc.publish(path +"/l2_grid_input_v", data[13])
    mqttc.publish(path +"/l2_gen_input_v", data[14])
    mqttc.publish(path +"/l2_output_v", data[15])
    mqttc.publish(path +"/inverter_mode", data[16])
    mqttc.publish(path +"/inverter_err", data[17])
    mqttc.publish(path +"/ac_mode", data[18])
    mqttc.publish(path +"/battery_v", data[19])
    mqttc.publish(path +"/misc", data[20])
    mqttc.publish(path +"/inverter_warn", data[21])

    mqttc.publish(path +"/l1_inv_w", int(data[2]) * int(data[8]))
    mqttc.publish(path +"/l1_chg_w", int(data[3]) * int(data[8]))
    mqttc.publish(path +"/l1_buy_w", int(data[4]) * int(data[8]))
    mqttc.publish(path +"/l1_sell_w", int(data[5]) * int(data[8]))
    mqttc.publish(path +"/l2_inv_w", int(data[9]) * int(data[15]))
    mqttc.publish(path +"/l2_chg_w", int(data[10]) * int(data[15]))
    mqttc.publish(path +"/l2_buy_w", int(data[11]) * int(data[15]))
    mqttc.publish(path +"/l2_sell_w", int(data[12]) * int(data[15]))

MQTT_TLS = False
MQTT_PREFIX = "mate3"
mqttc = mqtt.Client()
mqttc.on_connect = mqtt_connect
mqttc.on_disconnect = mqtt_disconnect

def radian_bridge():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.bind((args.interface, args.port))


    if args.username != None:
        mqttc.username_pw_set(args.username, password=args.password)
    if MQTT_TLS:
        mqttc.tls_set()
    mqttc.connect_async(args.host, args.hostport, 60)
    logging.debug("attempting mqtt connection on: %s" % args.host)
    logging.debug("port: %s" %args.port)
    mqttc.loop_start()

    while True:
        data, addr = sock.recvfrom(1024)
        logging.debug("received message: %s" % data)
        data = "% s" % data
        mac = data.split('[')[1]
        mac = mac.split(']')[0]
        data = data.split('<')[1]
        data = data.split('>')[0]
        data = data.split(',')
        data = [name.strip() for name in data]

		# Devtype 6 is for a Radian inverter, no other device is supported at this time.
        if data[1] == "6":
            radianProcessData(data, mac)
        else:
            logging.error("Unsupported Device Type: %s" %data[1])

def run():
    """Run main"""
    radian_bridge()

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)

    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                    description=AP_DESCRIPTION,
                                    epilog=AP_EPILOG)

    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("-i", "--interface", type=str, default="0.0.0.0",
                        help="Address to listen on (default: %(default)s)")
    parser.add_argument("-p", "--port", type=int, default=57027,
                        help="Port to listen on (default: %(default)s)")
    parser.add_argument("-H", "--host", type=str, default="127.0.0.1",
                        help="MQTT Host Address (default: %(default)s)")
    parser.add_argument("-P", "--hostport", type=int, default=1883,
                        help="MQTT Host Port (default: %(default)s)")
    parser.add_argument("-u", "--username", type=str, default=None,
                        help="MQTT Username (default: %(default)s)")
    parser.add_argument("-s", "--password", type=str, default=None,
                        help="MQTT Password (default: %(default)s)")
    parser.add_argument("-D", "--discovery", type=str, default="homeassistant",
                        help="Homeassistant MQTT discovery prefix (default: %(default)s)")
    args = parser.parse_args()

    if args.debug:
        logging.info("Enabling debug logging")
        logging.getLogger().setLevel(logging.DEBUG)

    run()