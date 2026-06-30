
from lora_e32 import LoRaE32, print_configuration, Configuration
from lora_e32_constants import OperatingFrequency, FixedTransmission, WirelessWakeUpTime, TransmissionPower, \
    TransmissionPower20, AirDataRate, UARTParity, UARTBaudRate
from lora_e32_operation_constant import ResponseStatusCode
import serial

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

loraSerial = serial.Serial('/dev/serial0') #, baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)

lora = LoRaE32('915T30D', loraSerial, aux_pin=18, m0_pin=22, m1_pin=27)

# Initialize the LoRa module and print the initialization status code
code = lora.begin()
print("Initialization: {}", ResponseStatusCode.get_description(code))

##########################################################################################
# GET CONFIGURATION
##########################################################################################

# Retrieve the current configuration of the LoRa module and print it to the console
code, configuration = lora.get_configuration()
print("Retrieve configuration: {}", ResponseStatusCode.get_description(code))
print("------------- CONFIGURATION BEFORE CHANGE -------------")
print_configuration(configuration)

##########################################################################################
# SET CONFIGURATION
# To set the configuration, you must set the configuration with the new values
##########################################################################################

# Create a new Configuration object with the desired settings
configuration_to_set = Configuration('915T30D')
configuration_to_set.ADDL = 0x0B
configuration_to_set.ADDH = 0x00
configuration_to_set.CHAN = 15
configuration_to_set.OPTION.operatingFrequency = OperatingFrequency.FREQUENCY_915
configuration_to_set.OPTION.fixedTransmission = FixedTransmission.FIXED_TRANSMISSION
configuration_to_set.OPTION.wakeUpTime = WirelessWakeUpTime.WAKE_UP_250
configuration_to_set.OPTION.transmissionPower = TransmissionPower('915T30D').get_transmission_power().POWER_21
configuration_to_set.SPED.airDataRate = AirDataRate.AIR_DATA_RATE_100_96
configuration_to_set.SPED.uartParity = UARTParity.MODE_00_8N1
configuration_to_set.SPED.uartBaudRate = UARTBaudRate.BPS_9600

# Set the new configuration on the LoRa module and print the updated configuration to the console
code, confSetted = lora.set_configuration(configuration_to_set)
print("------------- CONFIGURATION AFTER CHANGE -------------")
print(ResponseStatusCode.get_description(code))
print_configuration(confSetted)

##########################################################################################
# RESTORE DEFAULT CONFIGURATION
# To restore the default configuration, you must set the configuration with the default values
##########################################################################################

# Set the configuration to default values and print the updated configuration to the console
#print("------------- RESTORE ALL DEFAULT -------------")
#configuration_to_set = Configuration('915T30D')
#code, confSetted = lora.set_configuration(configuration_to_set)
#print(ResponseStatusCode.get_description(code))
#print_configuration(confSetted)


