import binascii
from bluepy import btle
import struct
import math
import time
from decimal import Decimal

class SensorTag(object):
    def __init__(self):
        self.UUID = {}
        self.name = None
        self.address = None

        self.device = None
        self.confHumidity = None

    def setUUID(self, UUID):
        self.UUID = UUID

        if (UUID == None or UUID['humidity'] == None or UUID['barometer'] == None or UUID['light'] == None):
            return False

    def setAddress(self, name, address):
        self.name = name
        self.address = address

    def connect(self):
        print("trying to connect to a sensortag: " + self.name + "(" + self.address + ")")
       
        try: 
            self.device = btle.Peripheral(self.address, "public")
        except Exception:
            print("conection failed!")
        else:
            print("successfully connected to sensortag...")
      
        try:
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
    from yamlreader import YamlReader
    yr = YamlReader()
    dict = yr.read("gateway.properties")
    for key, value in dict.items():
        print(key + " : " + str(value)) 

    st = SensorTag()
    st.setUUID(dict['UUID'])
    st.setAddress(dict['sensortags'][0]['sensortag']['name'], dict['sensortags'][0]['sensortag']['address']) 

    st.connect()
    #st.enable()
