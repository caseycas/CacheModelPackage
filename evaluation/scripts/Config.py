from ConfigParser import SafeConfigParser
import os

class Config:
    def __init__(self, configFile):

        if os.path.isfile(configFile):
            self.Config = SafeConfigParser()
            self.Config.read(configFile)
        else:
            print("Config file not found at: ")
            print(configFile)
            quit()

    def ConfigSectionMap(self, section):
        dict1 = {}
        options = self.Config.options(section)
        for option in options:
            try:
                dict1[option] = self.Config.get(section, option)
            except:
                dict1[option] = None
        return dict1
