import serial

device = '/dev/ttyUSB1'

try:
    print("Trying...", device)
    iris = serial.Serial(device, 115200)
except:
    print("Failed to connect on", device)

while(True):
    try:
        data = iris.readline()
        print(data)
    except:
        print("Failed to get data from Iris Gateway!")


