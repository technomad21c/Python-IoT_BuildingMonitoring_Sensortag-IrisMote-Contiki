import serial
import time
from influxdb import InfluxDBClient
from yamlreader import YamlReader
from sensortag import Sensortag

class Gateway:
    def __init__(self):
        self.sensortagUUID = {}
        self.humidity = {}
        self.barometer= {}
        self.light = {}
        self.sensortagUUID['humidity'] = self.humidity
        self.sensortagUUID['barometer'] = self.barometer
        self.sensortagUUID['light'] = self.light

        self.connectedDevice = None
        self.dbClient = None
   
        self.sensortags = []

    def setEnvVariables(self, filename):
        yr = YamlReader()
        env = yr.read(filename) 

        self.humidity['service'] = env['UUID']['humidity']['service']
        self.humidity['data']    = env['UUID']['humidity']['data']
        self.humidity['conf']    = env['UUID']['humidity']['conf']
        self.humidity['period']  = env['UUID']['humidity']['period']
        self.humidity['format']  = env['UUID']['humidity']['format']

        self.barometer['service'] = env['UUID']['barometer']['service']
        self.barometer['data']    = env['UUID']['barometer']['data']
        self.barometer['conf']    = env['UUID']['barometer']['conf']
        self.barometer['period']  = env['UUID']['barometer']['period']
        self.barometer['format']  = env['UUID']['barometer']['format']

        self.light['service'] = env['UUID']['light']['service']
        self.light['data']    = env['UUID']['light']['data']
        self.light['conf']    = env['UUID']['light']['conf']
        self.light['period']  = env['UUID']['light']['period']
        self.light['format']  = env['UUID']['light']['format']

        self.DB_ADDR     = env['db_addr']
        self.DB_PORT     = env['db_port']
        self.DB_DATABASE = env['db_database']

        for i in range(len(env['sensortags'])):
            sensortag = Sensortag()
            sensortag.setUUID(env['UUID'])
            sensortag.setAddress(env['sensortags'][i]['sensortag']['name'], env['sensortags'][i]['sensortag']['address'])

            self.sensortags.append(sensortag)
            print("init: ", sensortag)
        
    def connectSensortags(self):
        for sensortag in self.sensortags: 
            print("connect to sensortag: ", sensortag)
            sensortag.connect()
            sensortag.enable()

    def connectDB(self):
        self.client = InfluxDBClient(host=self.DB_ADDR, port=self.DB_PORT)
        self.client.switch_database(self.DB_DATABASE)

    def send(self): 
        while(True):
            for sensortag in self.sensortags:
                data = sensortag.read()
                print(data)
                datatemperature = [ {
                        "measurement": "temperature", 
                        "tags": { 
                            "sensor-type": data['sensortype'], 
                            "sensor-number": data['sensornumber'] 
                        }, 
                        "fields": {
                            "value": data['temperature'],
                        } 
                    } ]
   
                datahumidity = [ {
                        "measurement": "humidity", 
                        "tags": { 
                            "sensor-type": data['sensortype'], 
                            "sensor-number": data['sensornumber'] 
                        }, 
                        "fields": {
                            "value": data['humidity'],
                        } 
                    } ]
   
                databarometrnicpressure = [ {
                        "measurement": "barometricpressure", 
                        "tags": { 
                            "sensor-type": data['sensortype'], 
                            "sensor-number": data['sensornumber'] 
                        }, 
                        "fields": {
                            "value": data['barometricpressure'],
                        } 
                    } ]

                dataluminance = [ {
                        "measurement": "luminance", 
                        "tags": { 
                            "sensor-type": data['sensortype'], 
                            "sensor-number": data['sensornumber'] 
                        }, 
                        "fields": {
                            "value": data['luminance'],
                        } 
                    } ]

                databattery = [ {
                        "measurement": "battery", 
                        "tags": { 
                            "sensor-type": data['sensortype'], 
                            "sensor-number": data['sensornumber'] 
                        }, 
                        "fields": {
                            "value": data['battery'],
                        } 
                    } ]

                dataE110= [ {
                        "measurement": "E110", 
                        "tags": { 
                            "sensor-type": data['sensortype'], 
                            "sensor-number": data['sensornumber'] 
                        }, 
                        "fields": {
                            "temperature": data['temperature'],
                            "humidity": data['humidity'],
                            "barometicpressure": data['barometricpressure'],
                            "luminance": data['luminance'],
                            "battery": data['battery'],
                        } 
                    } ]
                self.client.write_points(datatemperature)
                self.client.write_points(datahumidity)
                self.client.write_points(databarometricpressure)
                self.client.write_points(dataluminance)
                self.client.write_points(databattery)
                self.client.write_points(dataE110)
            time.sleep(60)
    
    def initialize(self, propertyfile):
        self.setEnvVariables(propertyfile)

    def start(self):
        self.connectSensortags()
        self.connectDB()
        self.send()

if __name__ == '__main__':
    print("Smart Building Monitoring starts...")
    propertyfile = "../config/gateway.properties" 
    gw = Gateway()
    gw.initialize(propertyfile)
    gw.start()
