import argparse

from particulates.measurements import start_measurements


def main():
    parser = argparse.ArgumentParser(
        prog="particulates", description="Start particulates measurement"
    )
    parser.add_argument("port", help="Serial port to connect to")
    parser.add_argument(
        "-f",
        "--filename",
        default="{timestamp}_particulates.csv",
        help='Measurement filename in csv format (default: "%(default)s")',
    )
    parser.add_argument(
        "-i",
        "--interval",
        default=1,
        type=int,
        help="Measurement interval in seconds (default: %(default)s)",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Print measurements to stdout"
    )
    parser.add_argument(
        "-c",
        "--clean",
        action="store_true",
        help="Start fan cleaning before measurements",
    )

    args = parser.parse_args()
    start_measurements(
        args.port, args.filename, args.interval, args.verbose, args.clean
    )


if __name__ == "__main__":
    main()
