def color_wipe(strip, color, wait_ms=50, *args, **kwargs):
    time.sleep(6)
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        time.sleep(wait_ms/1000.0)
        strip.show()
    [strip.setPixelColor(i, color) for i in range(strip.numPixels())]
    strip.show()

def theaterchase(strip, color, wait_ms=50, iterations=10, *args, **kwargs):
    """Movie theater light style chaser animation."""
    for j in range(iterations):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, color)
                strip.show()
                time.sleep(wait_ms/1000.0)
                for i in range(0, strip.numPixels(), 3):
                    strip.setPixelColor(i+q, 0)

def bounce(strip, color, wait_ms=50, iterations=10, *args, **kwargs):
    if not args.color2:
        color2 = Color(0, 0, 0)
    n = strip.numPixels()

    for i in range(4 * n):
        for j in range(n):
            strip.setPixelColor(j, color)
        if (i // n) % 2 == 0:
            strip.setPixelColor(i % n, color2)
        else:
            strip.setPixelColor(n - 1 - (i % n), color2)
        strip.show()
        time.sleep(wait_ms/1000.0)


def wheel(pos, *args, **kwargs):
        """Generate rainbow colors across 0-255 positions."""
        if pos < 85:
                return Color(pos * 3, 255 - pos * 3, 0)
        elif pos < 170:
                pos -= 85
                return Color(255 - pos * 3, 0, pos * 3)
        else:
                pos -= 170
                return Color(0, pos * 3, 255 - pos * 3)

def rainbow(strip, wait_ms=20, iterations=1, *args, **kwargs):
        """Draw rainbow that fades across all pixels at once."""
        for j in range(256*iterations):
                for i in range(strip.numPixels()):
                        strip.setPixelColor(i, wheel((i+j) & 255))
                strip.show()
                time.sleep(wait_ms/1000.0)

def rainbow_cycle(strip, wait_ms=20, iterations=5, *args, **kwargs):
        """Draw rainbow that uniformly distributes itself across all pixels."""
        for j in range(256*iterations):
                for i in range(strip.numPixels()):
                        strip.setPixelColor(i, wheel((int(i * 256 / strip.numPixels()) + j) & 255))
                strip.show()
                time.sleep(wait_ms/1000.0)

def theater_chase_rainbow(strip, wait_ms=50, *args, **kwargs):
        """Rainbow movie theater light style chaser animation."""
        for j in range(256):
                for q in range(3):
                        for i in range(0, strip.numPixels(), 3):
                                strip.setPixelColor(i+q, wheel((i+j) % 255))
                        strip.show()
                        time.sleep(wait_ms/1000.0)
                        for i in range(0, strip.numPixels(), 3):
                                strip.setPixelColor(i+q, 0)

ANIMATIONS = {'theater_chase_rainbow': theater_chase_rainbow,
              'rainbow_cycle': rainbow_cycle,
              'rainbow': rainbow,
              'wheel': wheel,
              'theaterchase': theaterchase,
              'color_wipe': color_wipe,
              'bounce': bounce}
