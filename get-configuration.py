from lora_e32 import LoRaE32, print_configuration
from lora_e32_operation_constant import ResponseStatusCode
import serial
import RPi.GPIO as GPIO

GPIO.setwarnings(False)

loraSerial = serial.Serial('/dev/serial0')

lora = LoRaE32(
    '915T30D',
    loraSerial,
    aux_pin=18,
    m0_pin=22,
    m1_pin=27
)

try:
    code = lora.begin()
    print(f"Initialization: {ResponseStatusCode.get_description(code)}")

    code, configuration = lora.get_configuration()

    print(f"Retrieve configuration: {ResponseStatusCode.get_description(code)}")

    print_configuration(configuration)

finally:
    GPIO.cleanup()