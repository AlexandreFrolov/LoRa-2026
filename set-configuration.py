import argparse
import serial
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Установка и чтение конфигурации модуля LoRa (E32 или E220)"
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
    parser.add_argument(
        "--addh", type=lambda x: int(x, 0), default=0x00,
        help="Старший байт адреса ADDH (по умолчанию: 0x00)"
    )
    parser.add_argument(
        "--addl", type=lambda x: int(x, 0), default=0x0B,
        help="Младший байт адреса ADDL (по умолчанию: 0x0B)"
    )
    parser.add_argument(
        "--chan", type=int, default=15,
        help="Номер канала CHAN (по умолчанию: 15)"
    )
    parser.add_argument(
        "--restore-defaults", action="store_true",
        help="Вместо установки новой конфигурации восстановить заводские настройки"
    )
    return parser.parse_args()


def init_lora(series, model, loraSerial, aux_pin, m0_pin, m1_pin):
    """Импортирует нужные модули и инициализирует объект LoRa нужной серии."""

    if series == "e32":
        from lora_e32 import LoRaE32, print_configuration, Configuration
        from lora_e32_constants import (
            OperatingFrequency, FixedTransmission, WirelessWakeUpTime,
            TransmissionPower, AirDataRate, UARTParity, UARTBaudRate
        )
        from lora_e32_operation_constant import ResponseStatusCode

        model = model or "915T30D"
        lora = LoRaE32(model, loraSerial, aux_pin=aux_pin, m0_pin=m0_pin, m1_pin=m1_pin)

        constants = dict(
            OperatingFrequency=OperatingFrequency,
            FixedTransmission=FixedTransmission,
            WirelessWakeUpTime=WirelessWakeUpTime,
            TransmissionPower=TransmissionPower,
            AirDataRate=AirDataRate,
            UARTParity=UARTParity,
            UARTBaudRate=UARTBaudRate,
        )

        return lora, Configuration, print_configuration, ResponseStatusCode, constants

    elif series == "e220":
        from lora_e220 import LoRaE220, print_configuration, Configuration
        from lora_e220_constants import (
            FixedTransmission, TransmissionPower, AirDataRate, UARTParity,
            UARTBaudRate, RssiAmbientNoiseEnable, SubPacketSetting,
            WorPeriod, LbtEnableByte, RssiEnableByte
        )
        from lora_e220_operation_constant import ResponseStatusCode

        model = model or "900T22D"
        lora = LoRaE220(model, loraSerial, aux_pin=aux_pin, m0_pin=m0_pin, m1_pin=m1_pin)

        constants = dict(
            FixedTransmission=FixedTransmission,
            TransmissionPower=TransmissionPower,
            AirDataRate=AirDataRate,
            UARTParity=UARTParity,
            UARTBaudRate=UARTBaudRate,
            RssiAmbientNoiseEnable=RssiAmbientNoiseEnable,
            SubPacketSetting=SubPacketSetting,
            WorPeriod=WorPeriod,
            LbtEnableByte=LbtEnableByte,
            RssiEnableByte=RssiEnableByte,
        )

        return lora, Configuration, print_configuration, ResponseStatusCode, constants

    else:
        raise ValueError(f"Неизвестная серия модуля: {series}")


def build_e32_configuration(model, args, constants):
    Configuration = constants["_Configuration"]
    cfg = Configuration(model)
    cfg.ADDL = args.addl
    cfg.ADDH = args.addh
    cfg.CHAN = args.chan
    cfg.OPTION.operatingFrequency = constants["OperatingFrequency"].FREQUENCY_915
    cfg.OPTION.fixedTransmission = constants["FixedTransmission"].FIXED_TRANSMISSION
    cfg.OPTION.wakeUpTime = constants["WirelessWakeUpTime"].WAKE_UP_250
    cfg.OPTION.transmissionPower = constants["TransmissionPower"](model).get_transmission_power().POWER_21
    cfg.SPED.airDataRate = constants["AirDataRate"].AIR_DATA_RATE_100_96
    cfg.SPED.uartParity = constants["UARTParity"].MODE_00_8N1
    cfg.SPED.uartBaudRate = constants["UARTBaudRate"].BPS_9600
    return cfg


def build_e220_configuration(model, args, constants):
    Configuration = constants["_Configuration"]
    cfg = Configuration(model)
    cfg.ADDL = args.addl
    cfg.ADDH = args.addh
    cfg.CHAN = args.chan
    cfg.SPED.airDataRate = constants["AirDataRate"].AIR_DATA_RATE_100_96
    cfg.SPED.uartParity = constants["UARTParity"].MODE_00_8N1
    cfg.SPED.uartBaudRate = constants["UARTBaudRate"].BPS_9600
    cfg.OPTION.transmissionPower = constants["TransmissionPower"](model).get_transmission_power().POWER_10
    cfg.OPTION.RSSIAmbientNoise = constants["RssiAmbientNoiseEnable"].RSSI_AMBIENT_NOISE_ENABLED
    cfg.OPTION.subPacketSetting = constants["SubPacketSetting"].SPS_064_10
    cfg.TRANSMISSION_MODE.fixedTransmission = constants["FixedTransmission"].FIXED_TRANSMISSION
    cfg.TRANSMISSION_MODE.WORPeriod = constants["WorPeriod"].WOR_1500_010
    cfg.TRANSMISSION_MODE.enableLBT = constants["LbtEnableByte"].LBT_DISABLED
    cfg.TRANSMISSION_MODE.enableRSSI = constants["RssiEnableByte"].RSSI_ENABLED
    return cfg


def main():
    args = parse_args()
    loraSerial = serial.Serial('/dev/serial0')

    lora, Configuration, print_configuration, ResponseStatusCode, constants = init_lora(
        args.series, args.model, loraSerial, args.aux_pin, args.m0_pin, args.m1_pin
    )
    model = args.model or ("915T30D" if args.series == "e32" else "900T22D")
    constants["_Configuration"] = Configuration

    try:
        ##################################################################
        # INIT
        ##################################################################
        code = lora.begin()
        print(f"Initialization: {ResponseStatusCode.get_description(code)}")

        ##################################################################
        # GET CONFIGURATION
        ##################################################################
        code, configuration = lora.get_configuration()
        print(f"Retrieve configuration: {ResponseStatusCode.get_description(code)}")
        print("------------- CONFIGURATION BEFORE CHANGE -------------")
        print_configuration(configuration)

        ##################################################################
        # SET CONFIGURATION or RESTORE DEFAULTS
        ##################################################################
        if args.restore_defaults:
            print("------------- RESTORE ALL DEFAULT -------------")
            configuration_to_set = Configuration(model)
        else:
            if args.series == "e32":
                configuration_to_set = build_e32_configuration(model, args, constants)
            else:
                configuration_to_set = build_e220_configuration(model, args, constants)

        code, confSetted = lora.set_configuration(configuration_to_set)
        print("------------- CONFIGURATION AFTER CHANGE -------------")
        print(ResponseStatusCode.get_description(code))
        print_configuration(confSetted)

    finally:
        GPIO.cleanup()


if __name__ == "__main__":
    main()