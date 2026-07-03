import serial
import RPi.GPIO as GPIO
# Импортируем модули для E220
from lora_e220 import LoRaE220, Configuration
from lora_e220_constants import FixedTransmission, RssiEnableByte
from lora_e220_operation_constant import ResponseStatusCode

GPIO.setwarnings(False)

# Инициализация модуля LoRa E220-900T22D
loraSerial = serial.Serial('/dev/serial0') 
# Для E220-900T22D передаем базовую модель '900T22D'
lora = LoRaE220('900T22D', loraSerial, aux_pin=18, m0_pin=22, m1_pin=17)

code = lora.begin()
# Исправлено форматирование строки: в Python метод .format() или f-строки
print("Initialization: {}".format(ResponseStatusCode.get_description(code)))

# Конфигурация модуля
configuration_to_set = Configuration('900T22D')
configuration_to_set.ADDH = 0x00  # Старший байт адреса отправителя
configuration_to_set.ADDL = 0x11  # Младший байт адреса отправителя
configuration_to_set.CHAN = 16    # Рабочий канал (частота)

configuration_to_set.TRANSMISSION_MODE.enableRSSI = RssiEnableByte.RSSI_ENABLED

# В серии E220 за режим фиксированной передачи отвечает параметр ADD_MODE
configuration_to_set.TRANSMISSION_MODE.fixedTransmission = FixedTransmission.FIXED_TRANSMISSION

# Применяем конфигурацию
code, confSetted = lora.set_configuration(configuration_to_set)
print("Set configuration: {}".format(ResponseStatusCode.get_description(code)))

# Отправка фиксированного сообщения
# Формат: send_fixed_message(ADDH, ADDL, CHAN, message)
message = 'Hello, world!'
code = lora.send_fixed_message(0x00, 0x12, 16, message)

# Пояснение по комментариям: если мы отправляем на 0x00, 0x12, 15,
# то принимающий модуль должен быть настроен на ADDH=0x00, ADDL=0x12 и CHAN=15.
print("Send message: {}".format(ResponseStatusCode.get_description(code)))