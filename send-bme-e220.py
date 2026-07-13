import time
import serial
import smbus2
import bme280
import RPi.GPIO as GPIO
from lora_e220 import LoRaE220, Configuration
from lora_e220_constants import FixedTransmission, RssiEnableByte, TransmissionPower, LbtEnableByte
from lora_e220_operation_constant import ResponseStatusCode

from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
from PIL import ImageFont

GPIO.setwarnings(False)

# --- Настройка BME280 ---
I2C_PORT = 1
I2C_ADDRESS = 0x76  # или 0x77, смотрите вывод i2cdetect
bus = smbus2.SMBus(I2C_PORT)
calibration_params = bme280.load_calibration_params(bus, I2C_ADDRESS)

# --- Настройка OLED дисплея (SSD1306, I2C) ---
OLED_I2C_ADDRESS = 0x3C  # смотрите вывод i2cdetect, встречается также 0x3D
serial_i2c = i2c(port=1, address=OLED_I2C_ADDRESS)
oled = ssd1306(serial_i2c)

try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 12)
except IOError:
    font = ImageFont.load_default()


def show_on_oled(temp=None, pres=None, hum=None, status=""):
    with canvas(oled) as draw:
        draw.text((0, 0), "Датчик BME280", font=font, fill="white")
        if temp is not None:
            draw.text((0, 14), f"Temp:  {temp} C", font=font, fill="white")
            draw.text((0, 26), f"Pres:  {pres} hPa", font=font, fill="white")
            draw.text((0, 38), f"Hum:   {hum} %", font=font, fill="white")
        else:
            draw.text((0, 20), "Нет данных", font=font, fill="white")
        if status:
            draw.text((0, 52), status, font=font, fill="white")


# --- Настройка LoRa E220 ---
loraSerial = serial.Serial('/dev/serial0')
lora = LoRaE220('900T22D', loraSerial, aux_pin=18, m0_pin=22, m1_pin=27)
code = lora.begin()
print("Initialization: {}".format(ResponseStatusCode.get_description(code)))
show_on_oled(status="Инициализация...")

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
        status_text = ResponseStatusCode.get_description(code)
        print("Send message: {}".format(status_text))

        show_on_oled(
            temp=payload['temp'],
            pres=payload['pres'],
            hum=payload['hum'],
            status=f"TX: {status_text}"
        )

        time.sleep(SEND_INTERVAL)

except KeyboardInterrupt:
    print("Остановлено пользователем")
finally:
    oled.clear()
    loraSerial.close()
    GPIO.cleanup()