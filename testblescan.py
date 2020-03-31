# test BLE Scanning software
# jcs 6/8/2014

import blescan
import sys

import bluetooth._bluetooth as bluez

import ptvsd

dev_id = 0

# Allow other computers to attach to ptvsd at this IP address and port.
# ptvsd.enable_attach(address=('192.168.1.175', 3000), redirect_output=True)

# Pause the program until a remote debugger is attached
# ptvsd.wait_for_attach()

sock = bluez.hci_open_dev(dev_id)
print ("ble thread started - testblescan.py")

blescan.hci_le_set_scan_parameters(sock)
blescan.hci_enable_le_scan(sock)

x = 0
# str sBeacon 
while True:
    returnedList = blescan.parse_events(sock, 10)
    #try:
    #    returnedList.sort()
        # x = returnedList.index("b940")
    #    break
    #except ValueError:
    #    print("wtf")
    print ("----------")
    for beacon in returnedList:
        print (beacon)

