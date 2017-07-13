# Octoprint-LED-Control

Control WS2812 LED's via Octoprint MQTT Events

Using the MQTT plugin for Octoprint this script will respond to event messages and change attached LED's using the desired animation.

Useful for lighting the build surface and reacting to print events such as heating or print completed.

#### Dependencies

Adafruits Python Neopixel library: https://github.com/jgarff/rpi_ws281x/tree/master/python
Paho MQTT: https://pypi.python.org/pypi/paho-mqtt/1.3.0
