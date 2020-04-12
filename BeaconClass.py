import string 
import os
import sys
import struct
import time
import psutil
import mysql.connector as mariadb
from time import strftime  

def dateTime(): #get UNIX time  
		secs = float(time.time())  
		secs = secs*1000  
		return secs  

def sGetTimeStamp():
	return(time.ctime(time.time()))
	# seconds = time.time()
	# local_time = time.ctime(seconds)

# Test Max Address for Demo Packet
sMAC_Address = "ac:23:3f:a2:53:89"
# Demo Packet of Data
# Battery in 50, Temp data is in 13c2          
#    ____MAC Addr_____ _______Data1____________BBTTTT__ _D2_ _D3_ D4  
pktBeaconDemo = "ac:23:3f:a2:53:89,01060303e1ff0e16e1ffa1135013c289,53a2,3f23,ac"
#                      00010203040506070809101112131415        
# ---------------------------------------------------------------------

# csMself.fTemperatureFAC_Address = "ac:23:3f:a2:53:89"

#db = mariadb.connect(host="localhost", user="root", password="flicket", database="sensor") # replace password with your password  
db = mariadb.connect(host="localhost", user='root', password='flicket', database='sensor') # replace password with your password  
cur = db.cursor()  

class iBeaconPkt:

	def __init__(self, sMAC_Addr):
		self.sMAC_Addr = sMAC_Addr
		self.fTemperatureC = 0.0
		self.fTemperatureF = 0.0
		self.iBattery = 0
		self.sTemperatureBytes = ""
		self.sBatteryBytes = ""

	# ---------------------------------------------------------------------
	# The blescan code returns a string separated by commas.
	# Split the received Bluetooth frame into a list of 5 parts.
	# First check the MAC address to see if it is our Beacon
	# If that packet contains the MAC address, pass the P1-Data1
	# packet to extact the Temperature. 
	# Battery BB is 50, Temp TTTT is 13c2.
	# The MAC address from the beacon can contain many frames. We are looking
	# for the frame with Temp and Battery in it in this example below.        
	#    _P0_MAC Addr_____ _______P1_Data1_____MMMMBBTTTT__ _P2_ _P3_ P4  
	#   "ac:23:3f:a2:53:89,01060303e1ff0e16e1ffa1135013c289,53a2,3f23,ac"
	#                      00010203040506070809101112131415       
	#  The return value is a string 
	# ---------------------------------------------------------------------
	def sParseBeacon(self, sReceivedPacket):
		sPkt = sReceivedPacket.split(",") 
		if sPkt[0] == self.sMAC_Addr: # Our MAC address
			if (sPkt[1][20:22].upper() == "A1"):
				if(sPkt[1][22:24].upper() == "13"):
					# ---------------------------------------------------------------------
					# Will take the P1_Data1 string and get the BB data.
					# Per the definition above the  
					# ---------------------------------------------------------------------					
					self.sBatteryBytes = sPkt[1][24:26]						# Store Org Str
					self.iBattery = int(self.sBatteryBytes, 16) 			# Get BB - 50
					# ---------------------------------------------------------------------
					# Will take the P1_Data1 string and get the TTTT data.
					# Per the definition above the  
					# ---------------------------------------------------------------------
					# Convert iCTemp from hex to Centigrade. 
					sTemperature = sPkt[1][26:30] 		# Get TTTT - ex13C2	
					iCTemp = int(sTemperature, 16)  			# convert string to int
					iCTempHigh = iCTemp >> 8  			# get upper byte, 0x13 = 19
					fCTempLow = float(iCTemp & 0x00FF) 	# Get lower byte C2	
					fCTempLow = round(fCTempLow/256, 2)
					self.fTemperatureC = iCTempHigh + fCTempLow  	# Get the floating fraction
					# Convert from Centigrade to Fahrenheit)	
					self.fTemperatureF = round(((9.0/5.0 * self.fTemperatureC + 32.0)), 2)


	def fGetTemperatureF(self):
		return(self.fTemperatureF)

	def fGetTemperatureC(self):
		return(self.fTemperatureC)
	
	def iGetBatteryLife(self):
		return(self.iBattery)

		
if __name__ == '__main__':

	x = iBeaconPkt(sMAC_Address)
	x.sParseBeacon(pktBeaconDemo)
	fTempC = x.fGetTemperatureC()
	fTempF = x.fGetTemperatureF()
	iBattery = x.iGetBatteryLife()

	sDate = sGetTimeStamp()
	iDate = dateTime()
	
	sql = ("""INSERT INTO pool (datetime,temperature) VALUES (%s,%s)""", (iDate, fTempF)) 

	try:  
		print ("Writing to the database...")  
		cur.execute(*sql)  
		db.commit()  
		print ("Write complete")  

		cur.execute("SELECT datetime, temperature FROM pool" )

		for (datetime, temperature) in cur:
			print("time: "+str(datetime) + ", Temp: "+ str(temperature))
	
	except:  
		db.rollback()  
		print ("We have a problem")  
	
	cur.close()  
	db.close()  

	print("Temp F: " + str(fTempF) + ", Temp C: " + str(fTempC) + ", Battery Level: " + str(iBattery) + "%")

"""
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
"""