#!/usr/bin/env python3

import csv
import datetime
import time

from sensirion_shdlc_driver import ShdlcConnection, ShdlcSerialPort
from sensirion_shdlc_driver.errors import ShdlcTimeoutError
from shdlc_sps30.device import Sps30ShdlcDevice

sps30_product_type = "00080000"


def start_measurements(
    serial_port: str,
    filename: str,
    interval: int,
    verbose: bool = False,
    clean: bool = False,
):
    with ShdlcSerialPort(port=serial_port, baudrate=115200) as port:
        device = Sps30ShdlcDevice(ShdlcConnection(port))

        device.device_reset()
        time.sleep(0.1)

        product_type = device.device_information_product_type()
        print(f"Product type: {product_type}")
        assert product_type == sps30_product_type

        serial_number = device.device_information_serial_number()
        print(f"Serial number: {serial_number}")

        ((fw_major, fw_minor), rev, (shdlc_major, shdlc_minor)) = device.read_version()
        print(f"Firmware version: {fw_major}.{fw_minor}")
        print(f"Hardware revision: {rev}")
        print(f"Shdlc protocol version: {shdlc_major}.{shdlc_minor}")

        # default auto cleaning interval is 604800 seconds = 1 week
        device.write_auto_cleaning_interval(604800)
        auto_cleaning_interval = device.read_auto_cleaning_interval()
        print(f"Auto Cleaning Interval: {auto_cleaning_interval} seconds")

        device_status = device.read_device_status_register(False)
        assert device_status == (False, False, False)

        device.start_measurement()

        # manual fan cleaning
        if clean:
            print("Starting fan cleaning")
            device.start_fan_cleaning()
            time.sleep(5)

        time_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = filename.replace("{timestamp}", time_str)

        def print_measurement(time: str, readings: list[str]):
            designators = [
                "MC_1p0",
                "MC_2p5",
                "MC_4p0",
                "MC_10p",
                "NC_0p5",
                "NC_1p0",
                "NC_2p5",
                "NC_4p0",
                "NC_10p",
                "TPS",
            ]
            print(
                f'{time}   {"   ".join(f"{d}: {r}" for d, r in zip(designators, readings))}'
            )

        print(f'Open csv format file "{filename}"')

        with open(filename, "a") as csvfile:
            fieldnames = [
                "Time",
                "Mass Concentration 1p0 [ug/m^3]",
                "Mass Concentration 2p5 [ug/m^3]",
                "Mass Concentration 4p0 [ug/m^3]",
                "Mass Concentration 10p [ug/m^3]",
                "Number Concentration 0p5 [N/cm^3]",
                "Number Concentration 1p0 [N/cm^3]",
                "Number Concentration 2p5 [N/cm^3]",
                "Number Concentration 4p0 [N/cm^3]",
                "Number Concentration 10p [N/cm^3]",
                "Typical Particle Size [um]",
            ]
            new_file = csvfile.tell() == 0
            writer = csv.writer(csvfile, dialect="excel", delimiter=";")
            if new_file:
                writer.writerow(fieldnames)

            print("Starting measurements")

            try:
                while True:
                    if readings := device.read_measured_value():
                        time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        mass, number, size = readings
                        entry = [time_str] + [
                            f"{val:.6f}" for val in mass + number + (size,)
                        ]
                        writer.writerow(entry)
                        csvfile.flush()
                        if verbose:
                            print_measurement(
                                time_str,
                                [f"{val:9.6f}" for val in mass + number + (size,)],
                            )

                    time.sleep(interval)
            except KeyboardInterrupt:
                pass

        device.stop_measurement()
