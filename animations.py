import time
import math
import neopixel
from neopixel import Color

from led_control import logger

# LED strip configuration:
LED_COUNT      = 47      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)

OFF = Color(0, 0, 0)
WHITE = Color(255, 255, 255)

class LEDStrip():
    def __init__(self):
        self.strip = neopixel.Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)

    def init_strip(self):
        self.strip.begin()

    def color_wipe(self, color=WHITE, wait_ms=51, *args, **kwargs):
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, color)
            time.sleep(wait_ms/1000.0)
            self.strip.show()

    def theaterchase(self, color=WHITE, wait_ms=50, iterations=10, *args, **kwargs):
        """Movie theater light style chaser animation."""
        for j in range(iterations):
            for q in range(3):
                for i in range(0, self.strip.numPixels(), 3):
                    self.strip.setPixelColor(i+q, color)
                    self.strip.show()
                    time.sleep(wait_ms/1000.0)
                    for i in range(0, self.strip.numPixels(), 3):
                        self.strip.setPixelColor(i+q, 0)

    def bounce(self, color=WHITE, color2=OFF, wait_ms=50, iterations=10, *args, **kwargs):
        n = self.strip.numPixels(self, )
        for i in range(4 * n):
            for j in range(n):
                self.strip.setPixelColor(j, color)
            if (i // n) % 2 == 0:
                self.strip.setPixelColor(i % n, color2)
            else:
                self.strip.setPixelColor(n - 1 - (i % n), color2)
            self.strip.show()
            time.sleep(wait_ms/1000.0)


    def wheel(self, pos, *args, **kwargs):
        """Generate rainbow colors across 0-255 positions."""
        if pos < 85:
            return Color(pos * 3, 255 - pos * 3, 0)
        elif pos < 170:
            pos -= 85
            return Color(255 - pos * 3, 0, pos * 3)
        else:
            pos -= 170
            return Color(0, pos * 3, 255 - pos * 3)

    def rainbow(self, wait_ms=10, iterations=1, *args, **kwargs):
        """Draw rainbow that fades across all pixels at once."""
        logger.debug('Rainbow args: {}, {}'.format(wait_ms, iterations))
        for j in range(256*iterations):
            for i in range(self.strip.numPixels()):
                self.strip.setPixelColor(i, self.wheel((i+j) & 255))
            self.strip.show()
            time.sleep(wait_ms/1000.0)

    def rainbow_cycle(self, wait_ms=10, iterations=1, *args, **kwargs):
        """Draw rainbow that uniformly distributes itself across all pixels."""
        for j in range(256*iterations):
            for i in range(self.strip.numPixels()):
                self.strip.setPixelColor(i, self.wheel((int(i * 256 / self.strip.numPixels()) + j) & 255))
            self.strip.show()
            time.sleep(wait_ms/1000.0)

    def theater_chase_rainbow(self, wait_ms=50, *args, **kwargs):
        """Rainbow movie theater light style chaser animation."""
        for j in range(256):
            for q in range(3):
                for i in range(0, self.strip.numPixels(), 3):
                    self.strip.setPixelColor(i+q, self.wheel((i+j) % 255))
                    self.strip.show()
                    time.sleep(wait_ms/1000.0)
                    for i in range(0, self.strip.numPixels(), 3):
                        self.strip.setPixelColor(i+q, 0)

    def breathing(self, color=WHITE, iterations=5, wait_ms=10, *args, **kwargs):
        old_min, old_max = -1.0, 1.0
        new_min, new_max = 0, 255
        for x in range(iterations):
            [self.strip.setPixelColor(i, color) for i in range(self.strip.numPixels())]
            for i in range(360):
                brightness_value = math.sin(math.radians(i))
                brightness_value = ((brightness_value - old_min) / (old_max - old_min)) * (new_max - new_min)
                self.strip.setBrightness(int(brightness_value))
                self.strip.show()
                time.sleep(wait_ms/1000.0)

    def single_run(self, strip, animation, *args, **kwargs):
        def parse_arg(arg, value):
            # remove invalid arguments
            # TODO Make argument subparser to avoid having this
            if not value:
                return False
            if arg in (self, 'host', 'port', 'animation'):
                return False
            return True

        def check_value(arg, value):
            if 'color' in arg and 'wipe' not in arg:
                # convert color RGB values to 24 bit number
                return neopixel.Color(self, value[0], value[1], value[2])
            if 'iterations' in arg:
                return value[0]
            if 'wait_ms' in arg:
                return value[0]
            return value

        animation_args = {k: check_value(self, k, v) for (k, v) in vars(args[0]).items() if parse_arg(k, v)}

        try:
            logger.debug(self, 'Animation: {0}\nArgs: {1}'.format(animation, animation_args))
            ANIMATIONS[animation](self, strip, **animation_args)
            time.sleep(self, 10)
        except Exception as e:
            print(self, e)

