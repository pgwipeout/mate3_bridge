#!/usr/bin/env python
# coding=utf-8

from __future__ import print_function
from __future__ import with_statement

AP_DESCRIPTION="""
Publish Radian data stream information to Home Assistant.
"""

AP_EPILOG="""
RunTEST
"""

import os
import argparse
import logging
import time
import socket
#import json

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
		misc.append("240 VAC Mode")
		return volt * 2
	else:
		return volt

def radianProcessData(data):
	if len(data) < 22:
		logging.error("Insufficient data received: %s" %len(data))
		return

	if data[0] != "01":
		logging.error("Only port 1 is supported right now")
		return

	logging.debug("port: %s" %data[0])
	logging.debug("devtype: %s" %data[1])
	logging.debug("L1 Inv current: %s A" %data[2])
	logging.debug("L1 Chg current: %s A" %data[3])
	logging.debug("L1 Buy current: %s A" %data[4])
	logging.debug("L1 Sell current: %s A" %data[5])
	logging.debug("L1 Grid Input Voltage: %s VAC" %radianVoltageConv(data[6], data[20]))
	logging.debug("L1 Gen Input Voltage: %s VAC" %radianVoltageConv(data[7], data[20]))
	logging.debug("L1 Output Voltage: %s VAC" %radianVoltageConv(data[8], data[20]))
	logging.debug("L2 Inv current: %s A" %data[9])
	logging.debug("L2 Chg current: %s A" %data[10])
	logging.debug("L2 Buy current: %s A" %data[11])
	logging.debug("L2 Sell current: %s A" %data[12])
	logging.debug("L2 Grid Input Voltage: %s VAC" %radianVoltageConv(data[13], data[20]))
	logging.debug("L2 Gen Input Voltage: %s VAC" %radianVoltageConv(data[14], data[20]))
	logging.debug("L2 Output Voltage: %s VAC" %radianVoltageConv(data[15], data[20]))
	logging.debug("Inverter Mode: %s" %radianModeConv(data[16]))
	logging.debug("Error: %s" %radianErrorConv(data[17]))
	logging.debug("AC mode: %s" %radianACModeConv(data[18]))
	logging.debug("Battery Voltage: %s VDC" %str(float(data[19]) / 10))
	logging.debug("Misc: %s" %radianMiscConv(data[20]))
	logging.debug("Warnings: %s" %radianWarningConv(data[21]))

	return

def radian_bridge():

	UDP_IP = "0.0.0.0"
	UDP_PORT = 57027

	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind((UDP_IP, UDP_PORT))

	while True:
		data, addr = sock.recvfrom(1024)
		logging.info("received message: %s" % data)
		data = "% s" % data
		data = data.split('<')[1]
		data = data.split('>')[0]
		data = data.split(',')
		data = [name.strip() for name in data]

		# Devtype 6 is for a Radian inverter, no other device is supported at this time.
		if data[1] == "6":
			radianProcessData(data)
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
	args = parser.parse_args()

	if args.debug:
		logging.info("Enabling debug logging")
		logging.getLogger().setLevel(logging.DEBUG)

	run()