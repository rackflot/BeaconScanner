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
	sPkt = sReceivedPacket.split(",") 
	if sPkt[0] == "ac:23:3f:a2:53:89":
		sTemp = sGetTemperatureFromMinewTempData(sPkt[1])
	return sTemp
