import board
import busio
from adafruit_ssd1306 import SSD1306_I2C
from PIL import Image, ImageDraw, ImageFont

# Инициализация I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Разрешение дисплея: часто 128x64 или 128x32 — проверьте свой модуль
WIDTH, HEIGHT = 128, 64
oled = SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=0x3c)

oled.fill(0)
oled.show()

# Рисуем через PIL
image = Image.new("1", (WIDTH, HEIGHT))
draw = ImageDraw.Draw(image)
font = ImageFont.load_default()

draw.text((0, 0), "Hello, Pi!", font=font, fill=255)
draw.text((0, 16), "BME280 + OLED", font=font, fill=255)

oled.image(image)
oled.show()
