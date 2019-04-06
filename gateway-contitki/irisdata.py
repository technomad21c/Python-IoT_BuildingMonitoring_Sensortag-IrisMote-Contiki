
class IrisData:
    def __init__(self):
        self.dict = {}

    def convert(self, sensorvalue):
        tokens = sensorvalue.split(',')
        for token in tokens:
            kv = token.strip().replace('\x00', '').replace('\r','').split(':')
            self.dict[kv[0]] = kv[1]

        return self.dict

    def printData(self):
        for key in self.dict:
            print(key, ' : ', self.dict[key])
            

if __name__ == '__main__':
   data = IrisData()
   data.convert("sensorno:1, temperature:494, light:922, battery:0")
   data.printData()
 

