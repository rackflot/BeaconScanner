#!/usr/bin/python

import os
import time
import datetime
import glob
import MySQLdb
from time import strftime

#Uncomment for Live Temp Sensors
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

#Live Temp Sensors
poolTempSensor = '/sys/bus/w1/devices/28-0214632d15ff/w1_slave'
outsideTempSensor = '/sys/bus/w1/devices/28-03146315efff/w1_slave'

#Test Temp Sensors
#poolTempSensor = '/opt/code/tempSensor/devices/28-000003cee4ca/w1_slave' 
#outsideTempSensor = '/opt/code/tempSensor/devices/28-000003cee5ca/w1_slave'

# Variables for MySQL
db = MySQLdb.connect(host="localhost", user="XXXXXX",passwd="XXXXXX", db="XXXXXX")
cur = db.cursor()

#Reading Pool Temp Data  
def readPoolTempRaw():
    pt = open(poolTempSensor, 'r')
    lines = pt.readlines()
    pt.close()
    return lines
 
def readPoolTemp():
    lines = readPoolTempRaw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = readPoolTempRaw()
    poolTemp = lines[1].find('t=')
    if poolTemp != -1:
        tempString = lines[1][poolTemp+2:]
        poolTempC = float(tempString) / 1000.0
        poolTempF = poolTempC * 9.0 / 5.0 + 32.0
        return ("%.f" %poolTempF)

#Reading Outside Temp Data 
def readOutsideTempRaw():
    ot = open(outsideTempSensor, 'r')
    lines = ot.readlines()
    ot.close()
    return lines

def readOutsideTemp():
    lines = readOutsideTempRaw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = readOutsideTempRaw()
    outsideTempOutput = lines[1].find('t=')
    if outsideTempOutput != -1:
        tempString = lines[1][outsideTempOutput+2:]
        outsideTempC = float(tempString) / 1000.0
        outsideTempF = outsideTempC * 9.0 / 5.0 + 32.0
        return ("%.f" %outsideTempF)
        

while True:
        #print (readPoolTemp())
        #print (readOutsideTemp())      
        poolTemp = readPoolTemp()
        outsideTemp = readOutsideTemp()
        datetimeWrite = (time.strftime("%Y-%m-%d ") + time.strftime("%H:%M:%S"))
        
        # SQL Statement
        sql = ("""INSERT INTO tempLog (dateTime,poolTemp,outsideTemp) VALUES (%s,%s,%s)""",(datetimeWrite,poolTemp,outsideTemp))
        
        # Execute the SQL command
        cur.execute(*sql)
        
        # Commit your changes in the database
        db.commit()
        
        #cur.close()
        #db.close()
        time.sleep(3600)