import smbus2
import bme280

port = 1
address = 0x76  # или 0x77, смотрите вывод i2cdetect

bus = smbus2.SMBus(port)
calibration_params = bme280.load_calibration_params(bus, address)

data = bme280.sample(bus, address, calibration_params)
print(f"Температура: {data.temperature:.2f} °C")
print(f"Давление: {data.pressure:.2f} гПа")
print(f"Влажность: {data.humidity:.2f} %")
