from lora_e32 import LoRaE32
import serial
from RPi import GPIO

# Отключаем предупреждения GPIO, чтобы они не засоряли консоль
GPIO.setwarnings(False)

# Инициализируем UART порт
loraSerial = serial.Serial('/dev/serial0', baudrate=9600)

# Подключаем модуль E32
lora = LoRaE32('915T30D', loraSerial, aux_pin=18, m0_pin=22, m1_pin=27)

# Инициализируем
code = lora.begin()

if code == 1:
    print("Статус: Успешно подключено (Код 1)")
else:
    print(f"Статус: Ошибка инициализации (Код {code})")
