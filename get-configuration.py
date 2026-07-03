import argparse
import serial
import RPi.GPIO as GPIO

GPIO.setwarnings(False)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Инициализация и чтение конфигурации модуля LoRa (E32 или E220)"
    )
    parser.add_argument(
        "--series", type=str, choices=["e32", "e220"], default="e32",
        help="Серия модуля LoRa: e32 или e220 (по умолчанию: e32)"
    )
    parser.add_argument(
        "--model", type=str, default=None,
        help="Тип модуля LoRa, например 915T30D для E32 или 900T22D для E220 "
             "(по умолчанию: 915T30D для e32, 900T22D для e220)"
    )
    parser.add_argument(
        "--aux-pin", type=int, default=18,
        help="Номер GPIO-пина AUX (по умолчанию: 18)"
    )
    parser.add_argument(
        "--m0-pin", type=int, default=22,
        help="Номер GPIO-пина M0 (по умолчанию: 22)"
    )
    parser.add_argument(
        "--m1-pin", type=int, default=27,
        help="Номер GPIO-пина M1 (по умолчанию: 27)"
    )
    return parser.parse_args()


def build_lora(series, model, loraSerial, aux_pin, m0_pin, m1_pin):
    """Создаёт объект модуля LoRa нужной серии и возвращает
    (lora, ResponseStatusCode, print_configuration) для дальнейшей работы."""

    if series == "e32":
        from lora_e32 import LoRaE32, print_configuration
        from lora_e32_operation_constant import ResponseStatusCode

        model = model or "915T30D"
        lora = LoRaE32(
            model,
            loraSerial,
            aux_pin=aux_pin,
            m0_pin=m0_pin,
            m1_pin=m1_pin,
        )

    elif series == "e220":
        from lora_e220 import LoRaE220, print_configuration
        from lora_e220_operation_constant import ResponseStatusCode

        model = model or "900T22D"
        lora = LoRaE220(
            model,
            loraSerial,
            aux_pin=aux_pin,
            m0_pin=m0_pin,
            m1_pin=m1_pin,
        )

    else:
        raise ValueError(f"Неизвестная серия модуля: {series}")

    return lora, ResponseStatusCode, print_configuration


def main():
    args = parse_args()
    loraSerial = serial.Serial('/dev/serial0')

    lora, ResponseStatusCode, print_configuration = build_lora(
        args.series,
        args.model,
        loraSerial,
        args.aux_pin,
        args.m0_pin,
        args.m1_pin,
    )

    try:
        code = lora.begin()
        print(f"Initialization: {ResponseStatusCode.get_description(code)}")

        code, configuration = lora.get_configuration()
        print(f"Retrieve configuration: {ResponseStatusCode.get_description(code)}")
        print_configuration(configuration)
    finally:
        GPIO.cleanup()


if __name__ == "__main__":
    main()