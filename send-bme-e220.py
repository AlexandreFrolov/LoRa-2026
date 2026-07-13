import time
import serial
import smbus2
import bme280
import RPi.GPIO as GPIO
from lora_e220 import LoRaE220, Configuration
from lora_e220_constants import FixedTransmission, RssiEnableByte, TransmissionPower, LbtEnableByte
from lora_e220_operation_constant import ResponseStatusCode

GPIO.setwarnings(False)

# --- Настройка BME280 ---
I2C_PORT = 1
I2C_ADDRESS = 0x76  # или 0x77, смотрите вывод i2cdetect

bus = smbus2.SMBus(I2C_PORT)
calibration_params = bme280.load_calibration_params(bus, I2C_ADDRESS)

# --- Настройка LoRa E220 ---
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
# Включаем аппаратный LBT (Listen Before Talk) - модуль сам слушает эфир
# перед передачей и задерживает отправку, если канал занят
configuration_to_set.TRANSMISSION_MODE.enableLBT = LbtEnableByte.LBT_ENABLED
configuration_to_set.OPTION.transmissionPower = TransmissionPower('900T22D').get_transmission_power().POWER_10

code, confSetted = lora.set_configuration(configuration_to_set)
print("Set configuration: {}".format(ResponseStatusCode.get_description(code)))

# --- Периодическая отправка данных с BME280 ---
SEND_INTERVAL = 60  # секунд между отправками

try:
    while True:
        data = bme280.sample(bus, I2C_ADDRESS, calibration_params)

        payload = {
            'temp': round(data.temperature, 2),
            'pres': round(data.pressure, 2),
            'hum': round(data.humidity, 2),
        }

        print(f"Температура: {payload['temp']} °C, "
              f"Давление: {payload['pres']} гПа, "
              f"Влажность: {payload['hum']} %")

        # The receiver must be configured with ADDH = 0x00, ADDL = 0x01, CHAN = 23
        code = lora.send_fixed_dict(0, 0x12, 16, payload)
        print("Send message: {}".format(ResponseStatusCode.get_description(code)))

        time.sleep(SEND_INTERVAL)

except KeyboardInterrupt:
    print("Остановлено пользователем")
finally:
    loraSerial.close()
    GPIO.cleanup()
