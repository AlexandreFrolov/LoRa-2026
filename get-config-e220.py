import serial
import RPi.GPIO as GPIO
from lora_e220 import LoRaE220, print_configuration
from lora_e220_operation_constant import ResponseStatusCode

GPIO.setwarnings(False)
loraSerial = serial.Serial('/dev/serial0')  # , baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)
lora = LoRaE220('900T22D', loraSerial, aux_pin=18, m0_pin=22, m1_pin=27)

try:
    code = lora.begin()
    print(f"Initialization: {ResponseStatusCode.get_description(code)}")

    code, configuration = lora.get_configuration()
    print(f"Retrieve configuration: {ResponseStatusCode.get_description(code)}")

    if configuration is not None:
        print_configuration(configuration)
    else:
        print("Не удалось получить конфигурацию модуля (configuration is None).")
finally:
    GPIO.cleanup()