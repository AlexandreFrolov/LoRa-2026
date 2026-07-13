import board
import busio
from adafruit_ssd1306 import SSD1306_I2C
from PIL import Image, ImageDraw, ImageFont
import os

# Инициализация I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Разрешение дисплея (128x64 или 128x32 — проверьте свой модуль)
WIDTH, HEIGHT = 128, 64
oled = SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=0x3c)

oled.fill(0)
oled.show()

# Создаём холст для рисования
image = Image.new("1", (WIDTH, HEIGHT))
draw = ImageDraw.Draw(image)

# Загружаем шрифт с поддержкой кириллицы
# Пробуем DejaVu Sans, затем Liberation Sans — оба есть в стандартных репозиториях Raspberry Pi OS
font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
if not os.path.exists(font_path):
    font_path = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
if not os.path.exists(font_path):
    # Если ни один не найден, используем стандартный (без кириллицы)
    font = ImageFont.load_default()
    print("Кириллический шрифт не найден, будет отображён только ASCII-текст")
else:
    font = ImageFont.truetype(font_path, 14)  # размер шрифта в пикселях, подберите под свой дисплей

# Выводим русский и английский текст
draw.text((0, 0), "Привет, Pi!", font=font, fill=255)
draw.text((0, 16), "BME280 + OLED", font=font, fill=255)

# Отправляем изображение на дисплей
oled.image(image)
oled.show()
