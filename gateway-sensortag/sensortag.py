import binascii
from bluepy import btle
import struct
import math
import time
from decimal import Decimal

class SensorTag:
    def __init__(self):
        self.UUID = {}
        self.name = None
        self.address = None

    def setUUID(self, UUID):
        self.UUID = UUID

        if (UUID == None or UUID['humidity'] == None or UUID['barometer'] == None or UUID['light'] == None):
            return False

    def setAddress(self, name, address):
        self.name = name
        self.address = address

    def connect(self):
        print("connecting to sensortags")
       
        try: 
            self.device = Peripheral(self.address, "public")
            print("[ERROR] Connection to " + self.name + "(" + self.address + ") failed.")
    
            self.serviceHumidity  = self.device.getServiceByUUID(self.UUID['humidity']['service'])
            self.dataHumidity     = self.device.getCharacteristics(self.UUID['humidity']['data'])
            self.confHumidity     = self.device.getCharacteristics(self.UUID['humidity']['conf'])
            self.formatHumidity   = self.device.getCharacteristics(self.UUID['humidity']['format'])

            self.serviceBarometer = self.device.getServiceByUUID(self.UUID['barometer']['service'])
            self.dataBarometer    = self.device.getCharacteristics(self.UUID['barometer']['data'])
            self.confBarometer    = self.device.getCharacteristics(self.UUID['barometer']['conf'])
            self.formatBarometer  = self.device.getCharacteristics(self.UUID['barometer']['format'])

            self.serviceLight     = self.device.getServiceByUUID(self.UUID['light']['service'])
            self.dataLight        = self.device.getCharacteristics(self.UUID['light']['data'])
            self.confLight        = self.device.getCharacteristics(self.UUID['light']['conf'])
            self.formatLight      = self.device.getCharacteristics(self.UUID['light']['format'])
        except Exception:
            print("service discovery failed!")
            self.disconnect()
        else:
            print("successfully connected to " + self.name + "!")

    def disconnect(self):
        self.device.disconnect()

    def enable(self):
        self.confHumidity.write(struc.pack("<h", int(self.UUID['humidity']['enable'], 16)))
        self.confBarometer.write(struc.pack("<h", int(self.UUID['barometer']['enable'], 16)))
        self.confLight.write(struc.pack("<h", int(self.UUID['light']['enable'], 16)))
       
    def read(self):
        humidityValue  = struct.unpack(self.formatHumidity, self.dataHumidity.read()) 
        barometerValue = struct.unpack(self.formatBarometer,self.dataBaromter.read()) 
        lightValue     = struct.unpack(self.formatLight, self.dataLight.read())

        return (humidityValue, barometerValue, lightValue)

if __name__ == "__main__":
    UUID =  { 'humidity': {'service': '', 'data': ' ', 'conf': ' ', 'format': ' ', 'enable': ' '}}
