import wolframalpha
import configparser

config = configparser.ConfigParser()
# config.sections()
config.read('../config/config.ini')
print(config.sections())



# client = wolframalpha.Client('')