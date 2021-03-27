import pyudev
import pprint

context = pyudev.Context()

for device in context.list_devices(subsystem='tty', ID_BUS='usb'):
	if "DGT" in device.properties["ID_VENDOR"]:
		print("DGT board found at {}".format(device.properties["DEVNAME"]))
		# pprint.pprint(dict(device))
	elif "Arduino" in device.properties["ID_VENDOR"]:
		print("Arduino LCD found at {}".format(device.properties["DEVNAME"]))
