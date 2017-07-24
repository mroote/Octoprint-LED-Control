#!/usr/bin/env python

import argparse
import sys
import time
import os
import signal
import traceback
import logging

import paho.mqtt.client as mqtt
import neopixel

from animations import *

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger()

# LED strip configuration:
LED_COUNT      = 47      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)

def init_strip():
    return neopixel.Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)

class LEDControl():
    def __init__(self, strip, mqtt_host='127.0.0.1', mqtt_port='1883', mqtt_user='',
                 mqtt_pass=''):
        self.strip = strip
        self.mqtt_client = mqtt.Client()
        self.mqtt_host = mqtt_host
        self.mqtt_port = mqtt_port
        self.mqtt_user = mqtt_user
        self.mqtt_pass = mqtt_pass

    def init_msg_client(self):
        self.mqtt_client.username_pw_set(self.mqtt_user, password=self.mqtt_pass)
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message

        self.mqtt_client.connect(self.mqtt_host, self.mqtt_port, 60)

        self.mqtt_client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        print('MQTT Client connected: {}'.format(rc))

        client.subscribe('octoprint/#')

        ANIMATIONS['color_wipe'](self.strip)

    def on_message(self, client, userdata, msg):
        refresh = False
        logger.info('Received: {0}'.format(msg.topic))
        try:
            if 'PowerOn' in msg.topic:
                ANIMATIONS['color_wipe'](self.strip, wait_ms=150)
                refresh = True
            if 'PowerOff' in msg.topic:
                ANIMATIONS['color_wipe'](self.strip, color=Color(0,0,0), wait_ms=10)
            if 'ClientOpened' in msg.topic:
                ANIMATIONS['color_wipe'](self.strip, color=Color(0,64,255), wait_ms=10)
                refresh = True
            if 'Startup' in msg.topic:
                ANIMATIONS['rainbow_cycle'](self.strip)
                refresh = True
            if 'Connected' in msg.topic:
                ANIMATIONS['color_wipe'](self.strip, color=Color(0,255,64), wait_ms=10)
                refresh = True
            if 'Upload' in msg.topic or 'FileAdded' in msg.topic:
                ANIMATIONS['color_wipe'](self.strip, color=Color(0,255,10), wait_ms=10)
                refresh = True
            if 'PrintStarted' in msg.topic:
                ANIMATIONS['bounce'](self.strip, color=Color(0,32,255), color2=Color(0,255,32), iterations=2)
                refresh = True
            if 'PrintFailed' in msg.topic:
                ANIMATIONS['bounce'](self.strip, color=Color(255,32,32), color2=Color(255,128,128), iterations=5)
                refresh = True
            if 'PrintDone' in msg.topic:
                ANIMATIONS['rainbow_cycle'](self.strip)
                refresh = True
        except Exception as e:
            logger.debug('Error running animation: {0}'.format(e))
        finally:
            if refresh:
                ANIMATIONS['color_wipe'](self.strip)

def single_run(strip, animation, *args, **kwargs):
    def parse_arg(arg, value):
        # remove invalid arguments
        # TODO Make argument subparser to avoid having this
        if not value:
            return False
        if arg in ('host', 'port', 'animation'):
            return False
        return True

    def check_value(arg, value):
        if 'color' in arg and 'wipe' not in arg:
            # convert color RGB values to 24 bit number
            return neopixel.Color(value[0], value[1], value[2])
        if 'iterations' in arg:
            return value[0]
        return value

    animation_args = {k: check_value(k, v) for (k, v) in vars(args[0]).items() if parse_arg(k, v)}

    try:
        logger.debug('Animation: {0}\nArgs: {1}'.format(animation, animation_args))
        ANIMATIONS[animation](strip, **animation_args)
        time.sleep(10)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--daemon', help='Start LED Control Daemon.', nargs='?', const=True)
    parser.add_argument('--host', help='Hostname or IP Address for MQTT broker.', type=str, default='127.0.0.1')
    parser.add_argument('--port', help='Port for MQTT broker.', default='1883')
    parser.add_argument('--user', help='User for MQTT broker.', default="")
    parser.add_argument('-p', '--password', help='Password for MQTT broker.', default="")

    parser.add_argument('--animation', help='Run a single animation and exit.', choices=ANIMATIONS.keys())
    parser.add_argument('--color', metavar='RGB', nargs=3, type=int)
    parser.add_argument('--color2', metavar='RGB', nargs=3, type=int)
    parser.add_argument('--wait-ms', type=int, nargs=1)
    parser.add_argument('--iterations', type=int, nargs=1)

    args = parser.parse_args()

    strip = init_strip()
    strip.begin()

    if args.daemon:
        try:
            ledcontrol = LEDControl(strip,
                                    mqtt_host=args.host,
                                    mqtt_port=args.port,
                                    mqtt_user=args.user,
                                    mqtt_pass=args.password)
            ledcontrol.init_msg_client()
        except Exception as e:
            logger.debug(e)
        finally:
            sys.exit(0)

    if args.animation:
        os.setpgrp() # create new process group, become its leader
        try:
            single_run(strip, args.animation, args)
        except Exception as e:
            print(e)
            traceback.print_tb(err.__traceback__)
            er = sys.exc_info()[0]
            write_to_page( "<p>Error: %s</p>" % er )
        finally:
            # Ask nicely to stop then take the hammer out to prevent zombies
            os.killpg(0, signal.SIGTERM)
