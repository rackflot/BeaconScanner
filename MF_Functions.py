
import string 
import os
import sys
import struct
import time
import psutil

def sGetTimeStamp():
	return(time.ctime(time.time()))
	# seconds = time.time()
	# local_time = time.ctime(seconds)

# csMAC_Address = "ac:23:3f:a2:53:89"
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
		RAM_stats = p.readline()
		if i==2:
			# return(line.split()[1:4])
			return(RAM_stats.split()[1:4])
	 #       break
	#sRAM_Stat = str(round(int(RAM_stats[0]) / 1000,1)) + str(round(int(RAM_stats[1]) / 1000,1) + str(round(int(RAM_stats[2]) / 1000,1)))
			
def getRAMInfoStr():
	p = os.popen('free')
	i = 0
	while 1:
		i = i + 1
		RAM_stats = p.readline()
		if i==2:
			# return(RAM_stats.split()[1:4])
			RAM_stats = RAM_stats.split()[1:4]
			RAM_total = round(int(RAM_stats[0]) / 1000,1)
			RAM_used = round(int(RAM_stats[1]) / 1000,1)
			RAM_free = round(int(RAM_stats[2]) / 1000,1)
			# return("RAM Used: " + str(RAM_used) + ", RAM Free: " + str(RAM_free) + ", RAM Total: " + str(RAM_total))
			return("RAM Used: " + str(round(int(RAM_stats[1]) / 1000,1)) + ", RAM Free: "  + str(round(int(RAM_stats[2]) / 1000,1)) +  ", RAM Total: " + str(round(int(RAM_stats[0]) / 1000,1)))


# Return % of CPU used by user as a character string                                
def getCPUuse():
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
	