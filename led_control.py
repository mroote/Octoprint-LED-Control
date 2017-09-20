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

class LEDControl():
    def __init__(self, mqtt_host='127.0.0.1', mqtt_port='1883', mqtt_user='',
                 mqtt_pass=''):
        self.strip = None
        self.mqtt_client = mqtt.Client()
        self.mqtt_host = mqtt_host
        self.mqtt_port = mqtt_port
        self.mqtt_user = mqtt_user
        self.mqtt_pass = mqtt_pass

    def init_msg_client(self):
        if self.mqtt_user and self.mqtt_pass:
            self.mqtt_client.username_pw_set(self.mqtt_user, password=self.mqtt_pass)
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message

        self.mqtt_client.connect(self.mqtt_host, self.mqtt_port, 60)

        self.mqtt_client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        print('MQTT Client connected: {}'.format(rc))

        client.subscribe('octoprint/#')

        self.strip = LEDStrip()
        self.strip.init_strip()

        self.strip.color_wipe()

    def on_message(self, client, userdata, msg):
        refresh = False
        logger.debug('Received: {0}'.format(msg.topic))
        try:
            if 'PowerOn' in msg.topic:
                self.strip.color_wipe(wait_ms=100)
                refresh = True
            if 'PowerOff' in msg.topic:
                self.strip.color_wipe(color=Color(0,0,0), wait_ms=10)
            if 'ClientOpened' in msg.topic:
                self.strip.color_wipe(color=Color(0,64,255), wait_ms=10)
                refresh = True
            if 'Startup' in msg.topic:
                self.strip.rainbow_cycle()
                refresh = True
            if 'Connected' in msg.topic:
                self.strip.color_wipe(color=Color(0,255,64), wait_ms=10)
                refresh = True
            if 'Upload' in msg.topic or 'FileAdded' in msg.topic:
                self.strip.color_wipe(color=Color(0,255,10), wait_ms=10)
                refresh = True
            if 'PrintStarted' in msg.topic:
                self.strip.bounce(color=Color(255,32,20), color2=Color(0,255,32), iterations=2)
                refresh = True
            if 'PrintFailed' in msg.topic:
                self.strip.bounce(color=Color(255,32,32), color2=Color(255,128,128), iterations=5)
                refresh = True
            if 'PrintDone' in msg.topic:
                self.strip.rainbow_cycle(iterations=10, wait_ms=10)
                refresh = True
        except Exception as e:
            logger.debug('Error running animation: {0}'.format(e))
        finally:
            if refresh:
                self.strip.color_wipe()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--daemon', help='Start LED Control Daemon.', nargs='?', const=True)
    parser.add_argument('--host', help='Hostname or IP Address for MQTT broker.', type=str, default='127.0.0.1')
    parser.add_argument('--port', help='Port for MQTT broker.', default='1883')
    parser.add_argument('--user', help='User for MQTT broker.', default="")
    parser.add_argument('-p', '--password', help='Password for MQTT broker.', default="")

    parser.add_argument('--animation',
                        help='Run a single animation and exit.',
                        type=str,
                        choices=[k for k in LEDStrip.__dict__.keys() if k not in ('init_strip', 'single_run') and '__' not in k])
    parser.add_argument('--color', metavar='RGB', nargs=3, type=int)
    parser.add_argument('--color2', metavar='RGB', nargs=3, type=int)
    parser.add_argument('--wait-ms', type=int)
    parser.add_argument('--iterations', type=int)

    args = parser.parse_args()

    if args.daemon:
        try:
            ledcontrol = LEDControl(mqtt_user=args.user,
                                    mqtt_pass=args.password,
                                    mqtt_host=args.host,
                                    mqtt_port=args.port)
            ledcontrol.init_msg_client()
        except Exception as e:
            logger.debug(e)
        finally:
            sys.exit(0)

    if args.animation:
        strip = LEDStrip()
        strip.init_strip()
        os.setpgrp() # create new process group, become its leader
        try:
            animation = getattr(strip, args.animation)
            animation_args = {k: v for (k, v) in vars(args).items() if v is not None}
            if 'color' in animation_args:
                color = animation_args['color']
                animation_args['color'] = Color(color[0], color[1], color[2])
            logger.debug(animation_args)
            animation(**animation_args)
        except Exception as e:
            logger.debug(e)
            traceback.print_tb(err.__traceback__)
            er = sys.exc_info()[0]
            write_to_page( "<p>Error: %s</p>" % er )
        finally:
            # Ask nicely to stop then take the hammer out to prevent zombies
            os.killpg(0, signal.SIGTERM)
            time.sleep(2)
            os.killpg(0, signal.SIGKILL)
