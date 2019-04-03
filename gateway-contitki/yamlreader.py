import yaml

class YamlReader:
    def __init__(self):
        self.dict = {}

    def read(self, filename):
        stream = open(filename, "r")
        self.dict = yaml.full_load(stream)

        return self.dict

if (__name__ == '__main__'):
    yr = YamlReader()
    dict = yr.read("gateway.properties")
    for key, value in dict.items():
        print(key + " : " + str(value))
