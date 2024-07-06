#!/usr/bin/env python3

#SwithchDoc Labs September 2018
# Public Domain


from __future__ import print_function
from builtins import str
import sys
sys.path.append('./SDL_Pi_HM3301')
import time
import pigpio
import SDL_Pi_HM3301

import datetime

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

import config

#print("config.DustSensorSCL=", config.DustSensorSCL)
#print("config.DustSensorSDA=", config.DustSensorSDA)

import state
#GPIO.setup(config.DustSensorPowerPin, GPIO.OUT)
#GPIO.output(config.DustSensorPowerPin, True)

def powerOnDustSensor():
  global hm3301, myPi
  GPIO.setup(config.DustSensorPowerPin, GPIO.OUT)
  GPIO.output(config.DustSensorPowerPin, True)
  time.sleep(1)
  myPi = pigpio.pi()
  try:
    hm3301 = SDL_Pi_HM3301.SDL_Pi_HM3301(SDA= config.DustSensorSDA, SCL = config.DustSensorSCL, pi=myPi)
  except:
    myPi.bb_i2c_close(config.DustSensorSDA)
    myPi.stop() 
    hm3301 = SDL_Pi_HM3301.SDL_Pi_HM3301(SDA= config.DustSensorSDA, SCL = config.DustSensorSCL, pi=myPi)
  time.sleep(1)

def powerOffDustSensor():
  global hm3301, myPi
  try:
    hm3301.close()
  except:
    myPi.bb_i2c_close(config.DustSensorSDA)
    myPi.stop() 
  time.sleep(1)
  GPIO.setup(config.DustSensorPowerPin, GPIO.OUT)
  GPIO.output(config.DustSensorPowerPin, False)
  time.sleep(1)



def read_AQI():
  global hm3301

  if (config.SWDEBUG):
    print ("###############")
    print ("Reading AQI")
    print ("###############")

  myData = None

  while not myData:
    if (config.SWDEBUG):
      print ("Turning Dust Power On")
    powerOnDustSensor()

    # delay for 30 seconds for calibrated reading
    time.sleep(30)

    try:
      myData = hm3301.get_data()
    except Exception as e:
      print('=================================')
      print(datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))
      print(e)
      print('=================================')
      #return 0
      if (config.SWDEBUG):
        print ("Turning Dust Power Off")
      powerOffDustSensor()
      time.sleep(3)
      continue

    if (config.SWDEBUG):
      print ("data=",myData)
    if (hm3301.checksum() != True):
      if (config.SWDEBUG):
        print("Checksum Error!")
      myData = hm3301.get_data()
      if (hm3301.checksum() != True):
        if (config.SWDEBUG):
          print("2 Checksum Errors!")
        continue

  myAQI = hm3301.get_aqi()
  if (config.SWDEBUG):
    hm3301.print_data()
    print ("AQI=", myAQI)

  if (config.SWDEBUG):
    print ("Turning Dust Power Off")
  powerOffDustSensor()
  state.AQI = myAQI


def old_read_AQI():

      if (config.SWDEBUG):
          print ("###############")
          print ("Reading AQI")
          print ("###############")

      if (config.SWDEBUG):
          print ("Turning Dust Power On")
      powerOnDustSensor()

   

      # delay for 30 seconds for calibrated reading

      time.sleep(30)
      time.sleep(0.1)


      myData = hm3301.get_data()
      if (config.SWDEBUG):
        print ("data=",myData)
      if (hm3301.checksum() != True):
          if (config.SWDEBUG):
            print("Checksum Error!")
          myData = hm3301.get_data()
          if (hm3301.checksum() != True):
                if (config.SWDEBUG):
                    print("2 Checksum Errors!")
                    return 0

      myAQI = hm3301.get_aqi()
      if (config.SWDEBUG):
        hm3301.print_data()
        print ("AQI=", myAQI)
      
      #hm3301.close()
      powerOffDustSensor()
      state.AQI = myAQI
      
def print_data():
    hm3301.print_data()

def get_aqi():
      myAQI = hm3301.get_aqi()
      return myAQI


def get_data():
      myData = hm3301.get_data()
      return myData
