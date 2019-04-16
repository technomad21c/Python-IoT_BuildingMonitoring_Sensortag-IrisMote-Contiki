import binascii
from bluepy import btle
import struct
import math
import time
from decimal import Decimal

class Sensortag(object):
    def __init__(self):
        self.sensortype = "sensortag"
        self.UUID = {}
        self.name = None
        self.address = None

        self.device = None
        self.confHumidity = None
        
        self.data = {}

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
            print("successfully connected")
      
        try:
            self.serviceHumidity  = self.device.getServiceByUUID(self.UUID['humidity']['service'])
            self.dataHumidity     = self.serviceHumidity.getCharacteristics(self.UUID['humidity']['data'])[0]
            self.confHumidity     = self.serviceHumidity.getCharacteristics(self.UUID['humidity']['conf'])[0]
            self.formatHumidity   = self.UUID['humidity']['format']

            self.serviceBarometer = self.device.getServiceByUUID(self.UUID['barometer']['service'])
            self.dataBarometer    = self.serviceBarometer.getCharacteristics(self.UUID['barometer']['data'])[0]
            self.confBarometer    = self.serviceBarometer.getCharacteristics(self.UUID['barometer']['conf'])[0]
            self.formatBarometer  = self.UUID['barometer']['format']

            self.serviceLight     = self.device.getServiceByUUID(self.UUID['light']['service'])
            self.dataLight        = self.serviceLight.getCharacteristics(self.UUID['light']['data'])[0]
            self.confLight        = self.serviceLight.getCharacteristics(self.UUID['light']['conf'])[0]
            self.formatLight      = self.UUID['light']['format']
 
            self.serviceBattery   = self.device.getServiceByUUID(self.UUID['battery']['service'])
            self.dataBattery      = self.serviceBattery.getCharacteristics(self.UUID['battery']['data'])[0]
            
        except Exception:
            print("service discovery failed!")
            self.disconnect()
        else:
            print("successfully enabled")

    def disconnect(self):
        self.device.disconnect()

    def enable(self):
        self.confHumidity.write(struct.pack("B", 0x01))
        self.confBarometer.write(struct.pack("B", 0x01))
        self.confLight.write(struct.pack("B", 0x01))
       
    def read(self):
        (rawT, rawH)  = struct.unpack(self.formatHumidity, self.dataHumidity.read()) 
        humiTemp = -46.85 + 175.72 * (rawT / 65536.0)
        #humiRH = -6.0 + 125.0 * ((rawH & 0xFFFC) / 65536.0)
        self.data['humidity'] = round( -6.0 + 125.0 * ((rawH & 0xFFFC) / 65536.0), 1)

        (tL, tM, tH, pL, pM, pH) = struct.unpack(self.formatBarometer,self.dataBarometer.read()) 
        baroTemp = (tH*65536 + tM*256 + tL) / 100.0
        #baroPress = (pH*65536 + pM*256 + pL) / 100.0
        self.data['barometicpressure'] = round((pH*65536 + pM*256 + pL) / 100.0, 1)

        raw = struct.unpack(self.formatLight, self.dataLight.read())[0]
        m = raw & 0xFFF
        e = (raw & 0xFF00) >> 12
        #optiValue = 0.01 * (m << 2)
        self.data['luminance'] = round(0.01 * (m << 2),1)

        self.data['battery'] = ord(self.dataBattery.read())

        self.data['sensortype'] = self.sensortype
        self.data['sensornumber'] = self.name
        return self.data

if __name__ == "__main__":
    from yamlreader import YamlReader
    yr = YamlReader()
    dict = yr.read("gateway.properties")
    for key, value in dict.items():
        print(key + " : " + str(value)) 

    st = Sensortag()
    st.setUUID(dict['UUID'])
    st.setAddress(dict['sensortags'][0]['sensortag']['name'], dict['sensortags'][0]['sensortag']['address']) 

    st.connect()
    st.enable()
    while True:
        print("sensor value: ", st.read())
        time.sleep(10)
