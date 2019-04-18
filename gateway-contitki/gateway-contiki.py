import serial
import math
from influxdb import InfluxDBClient
from yamlreader import YamlReader
from irisdata import IrisData

class Gateway:
    def __init__(self):
        self.DEVICE = None
        self.BAUDRATE = None
        self.DB_ADDR = None
        self.DB_PORT = None
        self.connectedDevice = None
        self.dbClient = None

    def setEnvVariables(self, filename):
        yr = YamlReader()
        env = yr.read(filename) 
        self.DEVICE = env['device']
        self.BAUDRATE = env['baudrate']

        self.DB_ADDR = env['db_addr']
        self.DB_PORT = env['db_port']

    def connectGateway(self):
        try:
            print("Trying...", self.DEVICE)
            self.connectedDevice = serial.Serial(self.DEVICE,self.BAUDRATE) 
        except:
            print("Failed to connect on", self.DEVICE)

    def connectDB(self):
        self.client = InfluxDBClient(host=self.DB_ADDR, port=self.DB_PORT)
        self.client.switch_database('test')

    def send(self): 
        iris = IrisData()

        while(True):
            recv = self.connectedDevice.readline().decode(errors='ignore')
            #print(recv)

            data  = iris.convert(recv)  # converted into dictionary type
            print(data)
            data['temperature'] = self.convertTemperature(int(data['temperature']))
            data['luminance'] = self.convertIlluminance(int(data['luminance']))
            data['battery'] = self.convertBattery(int(data['battery']))

            data['sensortype'] = "iris"
            sensorname_prefix = "E110-iris-0"
            datatemperature = [ {
                        "measurement": "temperature",
                        "tags": {
                            "sensor-type": data['sensortype'],
                            "sensor-number": sensorname_prefix + str(data['sensorno']),
                        },
                        "field": {
                            "value": data['temperature'],
                        }
                } ]

            dataluminance = [ {
                        "measurement": "luminance",
                        "tags": {
                            "sensor-type": data['sensortype'],
                            "sensor-number": sensorname_prefix + str(data['sensorno']),
                        },
                        "field": {
                            "value": data['luminance'],
                        }
                } ]

            databattery = [ {
                        "measurement": "battery",
                        "tags": {
                            "sensor-type": data['sensortype'],
                            "sensor-number": sensorname_prefix + str(data['sensorno']),
                        },
                        "field": {
                            "value": data['battery'],
                        }
                } ]

            dataE110 = [ {
                        "measurement": "E110", 
                        "tags": { 
                            "sensor-type": data['sensortype'],
                            "sensor-number": sensorname_prefix + str(data['sensorno']),
                        }, 
                        "fields": {
                            "temperature": data['temperature'],
                            "luminance": data['luminance'],
                            "battery": data['battery'],
                        } 
                    } ]
   

            self.client.write_points(dataE110)
            print("Sensor data was sent to InflubDB")
    
    def convertTemperature(self, DN):
        Rthr = 10000 * (1023 - DN) / DN
        lnRthr = math.log(Rthr)
        TdegC = 1 / (0.001010024 + 0.000242127 * lnRthr + 0.000000146 * math.pow(lnRthr, 3)) - 273.15 
        return round(TdegC, 2)

    def convertIlluminance(self, DN):
        EU = 100 * DN / 1023
        return round(EU, 2)

    def convertBattery(self, ADC):
        v = 1.223  #voltage reference
        V = v * 1024 / ADC
        p = int(100 - (3.6 - round(V, 1)) * 10)
        return p

    def initialize(self, propertyfile):
        self.setEnvVariables(propertyfile)

    def start(self):
        self.connectGateway()
        self.connectDB()
        self.send()

if __name__ == '__main__':
    propertyfile = "../config/gateway.properties" 
    gw = Gateway()
    gw.initialize(propertyfile)
    gw.start()
