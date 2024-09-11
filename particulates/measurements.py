#!/usr/bin/env python3

import csv
import datetime
import time

from sensirion_shdlc_driver import ShdlcConnection, ShdlcSerialPort
from sensirion_shdlc_driver.errors import ShdlcTimeoutError
from shdlc_sps30.device import Sps30ShdlcDevice

sps30_product_type = "00080000"


def main():
    with ShdlcSerialPort(port="/dev/ttyUSB0", baudrate=115200) as port:
        device = Sps30ShdlcDevice(ShdlcConnection(port))

        device.device_reset()
        time.sleep(0.1)

        product_type = device.device_information_product_type()
        print(f'Product type: {product_type}')
        assert product_type == sps30_product_type

        serial_number = device.device_information_serial_number()
        print(f'Serial number: {serial_number}')

        ((fw_major, fw_minor), rev, (shdlc_major, shdlc_minor)) = device.read_version()
        print(f'Firmware version: {fw_major}.{fw_minor}')
        print(f'Hardware revision: {rev}')
        print(f'Shdlc protocol version: {shdlc_major}.{shdlc_minor}')

        # default auto cleaning interval is 604800 seconds = 1 week
        device.write_auto_cleaning_interval(604800)
        auto_cleaning_interval = device.read_auto_cleaning_interval()
        print(f'Auto Cleaning Interval: {auto_cleaning_interval} seconds')

        device_status = device.read_device_status_register(False)
        assert device_status == (False, False, False)

        # start measurement
        device.start_measurement()

        # manual fan cleaning
        # start_fan_cleaning(device)

        with open("measurements.csv", "w") as csvfile:
            fieldnames = [
                "Time",
                "Mass Concentration 1p0",
                "Mass Concentration 2p5",
                "Mass Concentration 4p0",
                "Mass Concentration 10p",
                "Number Concentration 0p5",
                "Number Concentration 1p0",
                "Number Concentration 2p5",
                "Number Concentration 4p0",
                "Number Concentration 10p",
                "Typical Particle Size",
            ]
            writer = csv.writer(csvfile, dialect="excel", delimiter=";")
            writer.writerow(fieldnames)

            while True:
                if readings := device.read_measured_value():
                    time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    mass, number, size = readings
                    entry = [time_str] + [f"{val:.6f}" for val in mass + number + (size,)]
                    writer.writerow(entry)
                    csvfile.flush()

                time.sleep(1)


        # stop measurement
        device.stop_measurement()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exit(0)
