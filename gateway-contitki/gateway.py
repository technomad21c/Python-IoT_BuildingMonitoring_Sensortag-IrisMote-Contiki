import serial
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
            sensorData = [ {
                        "measurement": "memory", 
                        "tags": { 
                            "sensor":data['sensorno'] 
                        }, 
                        "fields": {
                            "temperature": data['temperature'],
                            "light": data['light'],
                            "battery": data['battery'],
                        } 
                    } ]
   
            '''
            sensorData = [ {
                        "measurement": "memory", 
                        "tags": { 
                            "sensor": 1
                        }, 
                        "fields": {
                            "temperature": 21,
                            "light": 700,
                            "humidity": 50,
                        }
                    }
                  ]
            '''
            self.client.write_points(sensorData) 
            #print("Sensor data was sent to InflubDB")
    
    def initialize(self, propertyfile):
        self.setEnvVariables(propertyfile)

    def start(self):
        self.connectGateway()
        self.connectDB()
        self.send()

if __name__ == '__main__':
    propertyfile = "gateway.properties" 
    gw = Gateway()
    gw.initialize(propertyfile)
    gw.start()
