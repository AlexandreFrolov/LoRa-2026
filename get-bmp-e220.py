import serial
import time
import RPi.GPIO as GPIO
from lora_e220 import LoRaE220, Configuration
from lora_e220_operation_constant import ResponseStatusCode
from lora_e220_constants import FixedTransmission, RssiEnableByte

from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
from PIL import ImageFont

GPIO.setwarnings(False)

# --- Настройка OLED дисплея (SSD1306, I2C) ---
OLED_I2C_ADDRESS = 0x3C  # смотрите вывод i2cdetect, встречается также 0x3D
serial_i2c = i2c(port=1, address=OLED_I2C_ADDRESS)
oled = ssd1306(serial_i2c)

try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 12)
except IOError:
    font = ImageFont.load_default()


def show_on_oled(temp=None, pres=None, hum=None, rssi_dbm=None, status="OK"):
    with canvas(oled) as draw:
        draw.text((0, 0), "Погода (LoRa)", font=font, fill="white")
        if temp is not None:
            draw.text((0, 14), f"Temp:  {temp} C", font=font, fill="white")
            draw.text((0, 26), f"Pres:  {pres} hPa", font=font, fill="white")
            draw.text((0, 38), f"Hum:   {hum} %", font=font, fill="white")
        else:
            draw.text((0, 20), "Нет данных", font=font, fill="white")
        if rssi_dbm is not None:
            draw.text((0, 52), f"RSSI: {rssi_dbm} dBm", font=font, fill="white")


# --- Инициализация LoRaE220 ---
loraSerial = serial.Serial('/dev/serial0')
lora = LoRaE220('900T22D', loraSerial, aux_pin=18, m0_pin=22, m1_pin=27)
code = lora.begin()
print("Initialization: {}".format(ResponseStatusCode.get_description(code)))

configuration_to_set = Configuration('900T22D')
configuration_to_set.ADDH = 0x00  # Address of this receiver
configuration_to_set.ADDL = 0x12  # Address of this receiver
configuration_to_set.CHAN = 16
configuration_to_set.TRANSMISSION_MODE.fixedTransmission = FixedTransmission.FIXED_TRANSMISSION
configuration_to_set.TRANSMISSION_MODE.enableRSSI = RssiEnableByte.RSSI_ENABLED
code, confSetted = lora.set_configuration(configuration_to_set)
print("Set configuration: {}".format(ResponseStatusCode.get_description(code)))

print("Waiting for messages...")
show_on_oled(status="Ожидание...")
time.sleep(2)

try:
    while True:
        if lora.available() > 0:
            code, value, rssi = lora.receive_dict(rssi=True)
            print(ResponseStatusCode.get_description(code))
            rssi_dbm = rssi - 256
            print(f'RSSI: {rssi_dbm} dBm (сырое значение: {rssi})')

            if value:
                print("Данные:", value)
                temp = value.get('temp')
                pres = value.get('pres')
                hum = value.get('hum')
                show_on_oled(temp=temp, pres=pres, hum=hum, rssi_dbm=rssi_dbm)
            else:
                show_on_oled(rssi_dbm=rssi_dbm, status="Нет данных")

        time.sleep(2)

except KeyboardInterrupt:
    print("Остановлено пользователем")
finally:
    oled.clear()
    loraSerial.close()
    GPIO.cleanup()
