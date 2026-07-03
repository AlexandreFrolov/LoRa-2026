import serial

from lora_e220 import LoRaE220, print_configuration
from lora_e220_operation_constant import ResponseStatusCode

loraSerial = serial.Serial('/dev/serial0') #, baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)

lora = LoRaE220('900T22D', loraSerial, aux_pin=18, m0_pin=22, m1_pin=17)

code = lora.begin()
print("Initialization: {}", ResponseStatusCode.get_description(code))

code, configuration = lora.get_configuration()

print("Retrieve configuration: {}", ResponseStatusCode.get_description(code))

print_configuration(configuration)