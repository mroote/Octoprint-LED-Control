# Octoprint-LED-Control

Control WS2812 LED's via Octoprint MQTT Events

Using the MQTT plugin for Octoprint this script will respond to event messages and change attached LED's using the desired animation.

Useful for lighting the build surface and reacting to print events such as heating or print completed.

#### Dependencies

* Adafruits Python Neopixel library: https://github.com/jgarff/rpi_ws281x/tree/master/python
* Paho MQTT: https://pypi.python.org/pypi/paho-mqtt/1.3.0

## Usage

The script can be run with two modes, daemon and single run.  Single run is useful for testing animations while daemon mode will listen to thq MQTT bus and respond to messages.

To run a single run animation:

```
$ ./led_control.py --animation color_wipe --color 255 255 255
```

To launch the daemon mode:

```
$ ./led_control.py --daemon
```

Help text is available with all options for each mode with the --help flag.

```
$ ./led_control.py --help
usage: led_control.py [-h] [--daemon [DAEMON]] [--host HOST] [--port PORT]
                      [--user USER] [-p PASSWORD]
                      [--animation {rainbow_cycle,rainbow,theater_chase_rainbow,theaterchase,color_wipe,bounce}]
                      [--color RGB RGB RGB] [--color2 RGB RGB RGB]
                      [--wait-ms WAIT_MS] [--interval INTERVAL]

optional arguments:
  -h, --help            show this help message and exit
  --daemon [DAEMON]     Start LED Control Daemon.
  --host HOST           Hostname or IP Address for MQTT broker.
  --port PORT           Port for MQTT broker.
  --user USER           User for MQTT broker.
  -p PASSWORD, --password PASSWORD
                        Password for MQTT broker.
  --animation {rainbow_cycle,rainbow,theater_chase_rainbow,theaterchase,color_wipe,bounce}
                        Run a single animation and exit.
  --color RGB RGB RGB
  --color2 RGB RGB RGB
  --wait-ms WAIT_MS
  --interval INTERVAL
```


