## Sensirion SPS30 particulates measurements

```
usage: particulates [-h] [-f FILENAME] [-i INTERVAL] [-v] [-c] port

Start particulates measurement

positional arguments:
  port                  Serial port to connect to

options:
  -h, --help            show this help message and exit
  -f FILENAME, --filename FILENAME
                        Measurement filename in csv format (default: "{timestamp}_particulates.csv")
  -i INTERVAL, --interval INTERVAL
                        Measurement interval in seconds (default: 1)
  -v, --verbose         Print measurements to stdout
  -c, --clean           Start fan cleaning before measurements
  ```
