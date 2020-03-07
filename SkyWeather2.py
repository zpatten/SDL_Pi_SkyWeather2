#!/usr/bin/env python3
#
# SkyWeather2 Solar Powered Weather Station
# Januayr 2020
#
# SwitchDoc Labs
# www.switchdoc.com
#
#

# imports
# Check for user imports
from __future__ import print_function

import config

config.SWVERSION = "002"
# system imports

import time
from apscheduler.schedulers.background import BackgroundScheduler
import apscheduler.events

import subprocess
import pclogging
import traceback
import sys
import picamera

# user defined imports
import updateBlynk
import state
import tasks
import wirelessSensors
import wiredSensors
import sendemail
import watchDog
import DustSensor
import util
import BMP280
import SkyCamera

# Scheduler Helpers

# print out faults inside events
def ap_my_listener(event):
        if event.exception:
              print (event.exception)
              print (event.traceback)


# helper functions

	
def shutdownPi(why):

   pclogging.log(pclogging.INFO, __name__, "Pi Shutting Down: %s" % why)
   sendemail.sendEmail("test", "SkyWeather2 Shutting down:"+ why, "The SkyWeather2 Raspberry Pi shutting down.", config.notifyAddress,  config.fromAddress, "");
   sys.stdout.flush()
   time.sleep(10.0)

   os.system("sudo shutdown -h now")

def rebootPi(why):

   pclogging.log(pclogging.INFO, __name__, "Pi Rebooting: %s" % why)
   if (config.USEBLYNK):
     updateBlynk.blynkEventUpdate("Pi Rebooting: %s" % why)
     updateBlynk.blynkStatusTerminalUpdate("Pi Rebooting: %s" % why)
   pclogging.log(pclogging.INFO, __name__, "Pi Rebooting: %s" % why)
   os.system("sudo shutdown -r now")




# main program
print ("")

print ("##########################################################")
print ("SkyWeather2 Weather Station Version "+config.SWVERSION+" - SwitchDoc Labs")
print ("")
print ("Program Started at:"+ time.strftime("%Y-%m-%d %H:%M:%S"))
print ("##########################################################")
print ("")

#
if (config.SWDEBUG):
    print("Starting pigpio daemon")

cmd = [ '/usr/bin/pigpiod' ]
output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)

# detect devices

################
# BMP280 Setup 
################
bmp280 = BMP280.BMP280()

try:
        bmp280 = BMP280.BMP280()
        config.BMP280_Present = True
except Exception as e: 
        if (config.SWDEBUG):
            print ("I/O error({0}): {1}".format(e.errno, e.strerror))
            print(traceback.format_exc())

        config.BMP280_Present = False

################
# SkyCamera Setup 
################


#Establish WeatherSTEMHash
if (config.USEWEATHERSTEM == True):
    state.WeatherSTEMHash = SkyCamera.SkyWeatherKeyGeneration(config.STATIONKEY)

#Detect Camera WeatherSTEMHash
try:

    with picamera.PiCamera() as cam:
        if (config.SWDEBUG):
            print("Pi Camera Revision",cam.revision)
        cam.close()
    config.Camera_Present = True
except:
    config.Camera_Present = False


# display device present variables


print("----------------------")
print(util.returnStatusLine("BMP280",config.BMP280_Present))
print(util.returnStatusLine("SkyCam",config.Camera_Present))
print(util.returnStatusLine("AS3935",config.AS3935_Present))
print(util.returnStatusLine("OLED",config.OLED_Present))
print(util.returnStatusLine("SunAirPlus/SunControl",config.SunAirPlus_Present))
print(util.returnStatusLine("SolarMAX",config.SolarMAX_Present))
print(util.returnStatusLine("DustSensor",config.DustSensor_Present))
print()
print(util.returnStatusLine("UseBlynk",config.USEBLYNK))
print(util.returnStatusLine("UseMySQL",config.enable_MySQL_Logging))
print(util.returnStatusLine("Check WLAN",config.enable_WLAN_Detection))
print(util.returnStatusLine("WeatherUnderground",config.WeatherUnderground_Present))
print(util.returnStatusLine("UseWeatherStem",config.USEWEATHERSTEM))
print("----------------------")

# startup


pclogging.log(pclogging.INFO, __name__, "SkyWeather2 Startup Version"+config.SWVERSION )

if (config.USEBLYNK):
     updateBlynk.blynkEventUpdate("SW Startup Version "+config.SWVERSION)
     updateBlynk.blynkStatusTerminalUpdate("SW Startup Version "+config.SWVERSION) 

subjectText = "The "+ config.STATIONKEY + " SkyWeather2 Raspberry Pi has #rebooted."
ipAddress = subprocess.check_output(['hostname',  '-I'])
bodyText = "SkyWeather2 Version "+config.SWVERSION+ " Startup \n"+ipAddress.decode()+"\n"
if (config.SunAirPlus_Present):
	sampleSunAirPlus()
	bodyText = bodyText + "\n" + "BV=%0.2fV/BC=%0.2fmA/SV=%0.2fV/SC=%0.2fmA" % (batteryVoltage, batteryCurrent, solarVoltage, solarCurrent)

sendemail.sendEmail("test", bodyText, subjectText ,config.notifyAddress,  config.fromAddress, "");


if (config.USEBLYNK):
     updateBlynk.blynkInit()



# Set up scheduler

scheduler = BackgroundScheduler()

# for debugging
scheduler.add_listener(ap_my_listener, apscheduler.events.EVENT_JOB_ERROR)

##############
# setup tasks
##############
hdc1080 = None
wiredSensors.readWiredSensors(bmp280, hdc1080)

# prints out the date and time to console
scheduler.add_job(tasks.tick, 'interval', seconds=60)

# read wireless sensor package
scheduler.add_job(wirelessSensors.readSensors) # run in background

# read wired sensor package
scheduler.add_job(wiredSensors.readWiredSensors, 'interval', args=[bmp280, hdc1080], seconds = 30) 

if (config.SWDEBUG):
    # print state
    scheduler.add_job(state.printState, 'interval', seconds=60)

if (config.USEBLYNK):
    scheduler.add_job(updateBlynk.blynkStateUpdate, 'interval', seconds=15)
        
scheduler.add_job(watchDog.patTheDog, 'interval', seconds=10)   # reset the WatchDog Timer


# every 5 days at 00:04, reboot
scheduler.add_job(rebootPi, 'cron', day='5-30/5', hour=0, minute=4, args=["5 day Reboot"]) 
	
#check for Barometric Trend (every 15 minutes)
scheduler.add_job(util.barometricTrend, 'interval', seconds=15*60)

if (config.DustSensor_Present):
    #scheduler.add_job(DustSensor.read_AQI, 'interval', seconds=60*5)
    scheduler.add_job(DustSensor.read_AQI, 'interval', seconds=60*2)
    
# sky camera
if (config.USEWEATHERSTEM):
    if (config.Camera_Present):
        scheduler.add_job(SkyCamera.takeSkyPicture, 'interval', seconds=config.INTERVAL_CAM_PICS__SECONDS) 


# start scheduler
scheduler.start()
print ("-----------------")
print ("Scheduled Jobs")
print ("-----------------")
scheduler.print_jobs()
print ("-----------------")



# Main Loop

while True:

    time.sleep(1.0)

