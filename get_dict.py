from lora_e32 import LoRaE32, Configuration
import serial
import time

from lora_e32_constants import FixedTransmission
from lora_e32_operation_constant import ResponseStatusCode

import RPi.GPIO as GPIO
GPIO.setwarnings(False)


# Initialize the LoRaE32 module
loraSerial = serial.Serial('/dev/serial0') #, baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)
lora = LoRaE32('915T30D', loraSerial, aux_pin=18, m0_pin=22, m1_pin=27)
code = lora.begin()
print("Initialization: {}", ResponseStatusCode.get_description(code))

# Set the configuration to default values and print the updated configuration to the console
# Not needed if already configured
configuration_to_set = Configuration('915T30D')
configuration_to_set.ADDH = 0 
configuration_to_set.ADDL = 0x12 # Address of this receive no sender
configuration_to_set.CHAN = 15
configuration_to_set.OPTION.fixedTransmission = FixedTransmission.FIXED_TRANSMISSION
code, confSetted = lora.set_configuration(configuration_to_set)
print("Set configuration: {}", ResponseStatusCode.get_description(code))

print("Waiting for messages...")
#while True:
#    if lora.available() > 0:
#        code, value = lora.receive_message()
#        print(ResponseStatusCode.get_description(code))
#
#        print(value)
#        time.sleep(2)
        
while True:
    if lora.available() > 0:
        code, value = lora.receive_dict()
        print(ResponseStatusCode.get_description(code))
        print(value)
        print(value['key1'])
        time.sleep(2)        