import serial
import time
import RPi.GPIO as GPIO
from lora_e220 import LoRaE220, Configuration
from lora_e220_operation_constant import ResponseStatusCode
from lora_e220_constants import FixedTransmission, RssiEnableByte

GPIO.setwarnings(False)

# Initialize the LoRaE220 module
loraSerial = serial.Serial('/dev/serial0')
lora = LoRaE220('900T22D', loraSerial, aux_pin=18, m0_pin=22, m1_pin=27)
code = lora.begin()
print("Initialization: {}".format(ResponseStatusCode.get_description(code)))

# Set the configuration to default values and print the updated configuration to the console
# Not needed if already configured
configuration_to_set = Configuration('900T22D')
configuration_to_set.ADDH = 0x00  # Address of this receiver
configuration_to_set.ADDL = 0x12  # Address of this receiver
configuration_to_set.CHAN = 16
configuration_to_set.TRANSMISSION_MODE.fixedTransmission = FixedTransmission.FIXED_TRANSMISSION
# To enable RSSI, you must also enable RSSI on sender
configuration_to_set.TRANSMISSION_MODE.enableRSSI = RssiEnableByte.RSSI_ENABLED
code, confSetted = lora.set_configuration(configuration_to_set)
print("Set configuration: {}".format(ResponseStatusCode.get_description(code)))

print("Waiting for messages...")
while True:
    if lora.available() > 0:
        # If the sender not set RSSI
        # code, value = lora.receive_message()
        # If the sender set RSSI
        code, value, rssi = lora.receive_message(rssi=True)
        # Универсальный перевод сырого байта RSSI для E220
        rssi_dbm = rssi - 256 if rssi > 128 else rssi
        print(f'RSSI: {rssi_dbm} dBm (сырое значение: {rssi})')
        print(ResponseStatusCode.get_description(code))
        print(value)
    time.sleep(0.1)