import serial
import RPi.GPIO as GPIO
from lora_e220 import LoRaE220, Configuration
from lora_e220_constants import FixedTransmission, RssiEnableByte, TransmissionPower
from lora_e220_operation_constant import ResponseStatusCode

GPIO.setwarnings(False)
loraSerial = serial.Serial('/dev/serial0') 
lora = LoRaE220('900T22D', loraSerial, aux_pin=18, m0_pin=22, m1_pin=27)

code = lora.begin()
print("Initialization: {}".format(ResponseStatusCode.get_description(code)))

# Конфигурация модуля
configuration_to_set = Configuration('900T22D')
configuration_to_set.ADDH = 0x00  # Старший байт адреса отправителя
configuration_to_set.ADDL = 0x11  # Младший байт адреса отправителя
configuration_to_set.CHAN = 16    # Рабочий канал (частота)
configuration_to_set.TRANSMISSION_MODE.enableRSSI = RssiEnableByte.RSSI_ENABLED
configuration_to_set.TRANSMISSION_MODE.fixedTransmission = FixedTransmission.FIXED_TRANSMISSION

from lora_e220_constants import TransmissionPower
configuration_to_set.OPTION.transmissionPower = TransmissionPower('900T22D').get_transmission_power().POWER_10

code, confSetted = lora.set_configuration(configuration_to_set)
print("Set configuration: {}".format(ResponseStatusCode.get_description(code)))

#code, configuration = lora.get_configuration()
#from lora_e220 import print_configuration
#print_configuration(configuration)

# Отправка фиксированного сообщения
# Формат: send_fixed_message(ADDH, ADDL, CHAN, message)
#message = 'Привет! Изучаем модули LoRa'
#code = lora.send_fixed_message(0x00, 0x12, 16, message)
#print("Send message: {}".format(ResponseStatusCode.get_description(code)))


# Send a dictionary message (fixed)
data = {'key1': 'value1', 'key2': 'value2'}
code = lora.send_fixed_dict(0, 0x12, 16, data)
# The receiver must be configured with ADDH = 0x00, ADDL = 0x01, CHAN = 23
print("Send message: {}", ResponseStatusCode.get_description(code))