# BLE iBeaconScanner based on https://github.com/adamf/BLE/blob/master/ble-scanner.py
# JCS 06/07/14
# Adapted for Python3 by Michael duPont 2015-04-05

# BLE scanner based on https://github.com/adamf/BLE/blob/master/ble-scanner.py
# BLE scanner, based on https://code.google.com/p/pybluez/source/browse/trunk/examples/advanced/inquiry-with-rssi.py

# https://github.com/pauloborges/bluez/blob/master/tools/hcitool.c for lescan
# https://kernel.googlesource.com/pub/scm/bluetooth/bluez/+/5.6/lib/hci.h for opcodes
# https://github.com/pauloborges/bluez/blob/master/lib/hci.c#L2782 for functions used by lescan

# performs a simple device inquiry, and returns a list of ble advertizements 
# discovered device

# NOTE: Python's struct.pack() will add padding bytes unless you make the endianness explicit. Little endian
# should be used for BLE. Always start a struct.pack() format string with "<"

#Installation
#sudo apt-get install libbluetooth-dev bluez
#sudo pip-3.2 install pybluez   #pip-3.2 for Python3.2 on Raspberry Pi

import os
import sys
import struct
import bluetooth._bluetooth as bluez
import time

LE_META_EVENT = 0x3e
OGF_LE_CTL=0x08
OCF_LE_SET_SCAN_ENABLE=0x000C

# these are actually subevents of LE_META_EVENT
EVT_LE_CONN_COMPLETE=0x01
EVT_LE_ADVERTISING_REPORT=0x02

#from MF_Functions.py import sMinewTempData
#from MF_Functions.py import sGetTemperatureFromMinewTempData


def getBLESocket(devID):
	return bluez.hci_open_dev(devID)

#def returnnumberpacket(pkt):
#    myInteger = 0
#    multiple = 256
#    for i in range(len(pkt)):
#        myInteger += struct.unpack("B",pkt[i:i+1])[0] * multiple
#        multiple = 1
#    return myInteger

def returnstringpacket(pkt):
	myString = "";
	for i in range(len(pkt)):
		myString += "%02x" %struct.unpack("B",pkt[i:i+1])[0]
	return myString

#def printpacket(pkt):
#    for i in range(len(pkt)):
#        sys.stdout.write("%02x " % struct.unpack("B",pkt[i:i+1])[0])

def get_packed_bdaddr(bdaddr_string):
	packable_addr = []
	addr = bdaddr_string.split(':')
	addr.reverse()
	for b in addr:
		packable_addr.append(int(b, 16))
	return struct.pack("<BBBBBB", *packable_addr)

def packed_bdaddr_to_string(bdaddr_packed):
	return ':'.join('%02x'%i for i in struct.unpack("<BBBBBB", bdaddr_packed[::-1]))

def hci_enable_le_scan(sock):
	hci_toggle_le_scan(sock, 0x01)

def hci_disable_le_scan(sock):
	hci_toggle_le_scan(sock, 0x00)

def hci_toggle_le_scan(sock, enable):
	cmd_pkt = struct.pack("<BB", enable, 0x00)
	bluez.hci_send_cmd(sock, OGF_LE_CTL, OCF_LE_SET_SCAN_ENABLE, cmd_pkt)

def hci_le_set_scan_parameters(sock):
	old_filter = sock.getsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, 14)

def parse_events(sock, loop_count=100):
	old_filter = sock.getsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, 14)
	flt = bluez.hci_filter_new()
	bluez.hci_filter_all_events(flt)
	bluez.hci_filter_set_ptype(flt, bluez.HCI_EVENT_PKT)
	sock.setsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, flt )
	myFullList = []
	for i in range(0, loop_count):
		pkt = sock.recv(255)
		ptype, event, plen = struct.unpack("BBB", pkt[:3])
		if event == bluez.EVT_INQUIRY_RESULT_WITH_RSSI:
			i = 0
		elif event == bluez.EVT_NUM_COMP_PKTS:
			i = 0
		elif event == bluez.EVT_DISCONN_COMPLETE:
			i = 0
		elif event == LE_META_EVENT:
			subevent, = struct.unpack("B", pkt[3:4])
			pkt = pkt[4:]
			if subevent == EVT_LE_CONN_COMPLETE:
				le_handle_connection_complete(pkt)
			elif subevent == EVT_LE_ADVERTISING_REPORT:
				num_reports = struct.unpack("B", pkt[0:1])[0]
				report_pkt_offset = 0
				for i in range(0, num_reports):
					# build the return string
					Adstring = packed_bdaddr_to_string(pkt[report_pkt_offset + 3:report_pkt_offset + 9])
					Adstring += ',' + returnstringpacket(pkt[report_pkt_offset -22: report_pkt_offset - 6])
					#Adstring += ',' + "%i" % returnnumberpacket(pkt[report_pkt_offset -6: report_pkt_offset - 4])
					Adstring += ',' + returnstringpacket(pkt[report_pkt_offset -6: report_pkt_offset - 4])
					#Adstring += ',' + "%i" % returnnumberpacket(pkt[report_pkt_offset -4: report_pkt_offset - 2])
					Adstring += ',' + returnstringpacket(pkt[report_pkt_offset -4: report_pkt_offset - 2])
					try:
						#Adstring += ',' + "%i" % struct.unpack("b", pkt[report_pkt_offset -2:report_pkt_offset -1])
						Adstring += ',' + returnstringpacket(pkt[report_pkt_offset -2:report_pkt_offset -1])
						#The last byte is always 00; we don't really need it
						#Adstring += ',' + "%i" % struct.unpack("b", pkt[report_pkt_offset -1:report_pkt_offset])
						#Adstring += ',' + returnstringpacket(pkt[report_pkt_offset -1:report_pkt_offset])
					except: 1
					#Prevent duplicates in results
					if Adstring not in myFullList: myFullList.append(Adstring)
	sock.setsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, old_filter )
	return myFullList

import string 

csMAC_Address = "ac:23:3f:a2:53:89"
# Battery in 50, Temp data is in 13c2          
#    ____MAC Addr_____ _______Data1____________BBTTTT__ _D2_ _D3_ D4  
a = "ac:23:3f:a2:53:89,01060303e1ff0e16e1ffa1135013c289,53a2,3f23,ac"
#                      00010203040506070809101112131415        

# ---------------------------------------------------------------------
# The blescan code returns a string separated by commas.
# Split the received Bluetooth frame into a list of 5 parts.
# First check the MAC address to see if it is our Beacon
# If that packet contains the MAC address, pass the P1-Data1
# packet to extact the Temperature. 
# Battery in 50, Temp data is in 13c2          
#    _P0_MAC Addr_____ _______P1_Data1_________BBTTTT__ _P2_ _P3_ P4  
#   "ac:23:3f:a2:53:89,01060303e1ff0e16e1ffa1135013c289,53a2,3f23,ac"
#                      00010203040506070809101112131415        
# ---------------------------------------------------------------------

def sMinewTempData(sReceivedPacket):
	sTemp = ""
	sPkt = sReceivedPacket.split(",") 
	if sPkt[0] == "ac:23:3f:a2:53:89": # Our MAC address
		if (sPkt[1][20:22].upper() == "A1"):
			if(sPkt[1][22:24].upper() == "13"):
				sTemp = sGetTemperatureFromMinewTempData(sPkt[1])
	return sTemp

# ---------------------------------------------------------------------
# Will take the P1_Data1 string and get the TTTT data.
# Per the definition above the  
# ---------------------------------------------------------------------
def sGetTemperatureFromMinewTempData(sMinewPkt):
	sCTemp = sMinewPkt[26:30] 			# Get TTTT ex13C2
	iCTemp = int(sCTemp, 16)  			# convert string to int
	# Convert iCTemp from hex to Centigrade. 
	iCTempHigh = iCTemp >> 8  			# get upper byte, 0x13 = 19
	fCTempLow = float(iCTemp & 0x00FF) 	# Get lower byte C2	
	fCTempLow = (fCTempLow/256) * 100  	# Get the floating fraction
	fCTempLow = round(fCTempLow)		# round it to 2 decimal points
	sTemp = str(iCTempHigh) + "." + str(int(fCTempLow)) + " Centigrade, "
	# Convert from Centigrade to Fahrenheit)	
	fTempF = round(((9.0/5.0 * (iCTempHigh + fCTempLow/100) + 32.0)), 2)
	sFTemp = str(fTempF)
	# Concatenate the Strings 
	sTemp = sTemp + sFTemp + " Fahrenheit"
	return(sTemp)

# Return CPU temperature as a character string                                      
def getCPUtemperature():
    res = os.popen('vcgencmd measure_temp').readline()
    return(res.replace("temp=","").replace("'C\n",""))

# Return RAM information (unit=kb) in a list                                        
# Index 0: total RAM                                                                
# Index 1: used RAM                                                                 
# Index 2: free RAM                                                                 
def getRAMinfo():
    p = os.popen('free')
    i = 0
    while 1:
        i = i + 1
        line = p.readline()
        if i==2:
            return(line.split()[1:4])

# Return % of CPU used by user as a character string                                
def getCPUuse():
    # imf = os.popen(top -n1 | awk '/Cpu\(s\):/ {print $2}').readline().strip()
    # imf = os.popen(top -n1 | awk #'/Cpu\(s\):/ {print $2}')
    # imf = (str(os.popen("top -n1 | awk '/Cpu\(s\):/ {print $2}'").readline().strip()))
    # return(imf)
    return(str(os.popen("top -n1 | awk '/%Cpu\(s\):/ {print $2}'").readline().strip()))
    

# Return information about disk space as a list (unit included)                     
# Index 0: total disk space                                                         
# Index 1: used disk space                                                          
# Index 2: remaining disk space                                                     
# Index 3: percentage of disk used                                                  
def getDiskSpace():
    p = os.popen("df -h /")
    i = 0
    while 1:
        i = i +1
        line = p.readline()
        if i==2:
            return(line.split()[1:5])
 


if __name__ == '__main__':
	dev_id = 0
	try:
		sock = bluez.hci_open_dev(dev_id)
		print("ble thread started - blescan.py")
	except:
		print("error accessing bluetooth device...")
		sys.exit(1)

	hci_le_set_scan_parameters(sock)
	hci_enable_le_scan(sock)
	x = 1
	print("----------")
	while True:
		returnedList = parse_events(sock, 10)        
		for beacon in returnedList:
			sTemp = sMinewTempData(beacon)
			if (sTemp != ""):
				seconds = time.time()
				local_time = time.ctime(seconds)

				print("Local Time: " + local_time + ", index: "+ str(x) + " - "+ sTemp)
				# every 10 lines, add a separator
				if (x % 10 == 0): 
					print("--------------------------------------------------------------")
					# CPU informatiom
					CPU_temp = getCPUtemperature()
					CPU_usage = getCPUuse()
					print("CPU Temp: " + CPU_temp + ", CPU Usage: "+ CPU_usage)
					# RAM information
					# Output is in kb, here I convert it in Mb for readability
					RAM_stats = getRAMinfo()
					RAM_total = round(int(RAM_stats[0]) / 1000,1)
					RAM_used = round(int(RAM_stats[1]) / 1000,1)
					RAM_free = round(int(RAM_stats[2]) / 1000,1)
					print ("RAM Used: " + str(RAM_used) + ", RAM Free: " + str(RAM_free) + ", RAM Total: " + str(RAM_total))
					# Disk information
					DISK_stats = getDiskSpace()
					DISK_total = DISK_stats[0]
					DISK_free = DISK_stats[1]
					DISK_perc = DISK_stats[3]
					print("Disk Used: " + DISK_perc + ", Disk Free: " + DISK_free + ", Disk Total: " + DISK_total)
					print("--------------------------------------------------------------")
				x = x + 1

   
