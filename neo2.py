#!/usr/bin/env python

import serial
import time
import math
from collections import namedtuple
import pyglet

port = serial.Serial("/dev/ttyUSB0", baudrate=115200)
time.sleep(1.5)

def escape(c):
    if c in "#$}":
        return "}" + chr(ord(c) ^ 0x20)
    else:
        return c

def loadPixels(rgbs):
    msg = '$P' + ''.join(escape(b) for b in rgbs) + '#'
    port.write(msg)

rgb = namedtuple("rgb", "r g b")

black  = rgb(  0,   0,   0)
white  = rgb(255, 255, 255)
red    = rgb(255,   0,   0)
orange = rgb(255, 165,   0)
yellow = rgb(255, 255,   0)
green  = rgb(  0, 255,   0)
blue   = rgb(  0,   0, 255)
indigo = rgb( 75,   0, 130)
violet = rgb(159,   0, 255)

class Gradient(object):
    def __init__(self, stops):
        self.stops = stops[:]
        if stops[-1][0] != 1.0:
            self.stops.append((1.0, stops[0][1]))

    def __getitem__(self, t):
        while t < 0.0:
            t += 1.0
        while t >= 1.0:
            t -= 1.0

        #if t < 0.0:
        #    return self.stops[0][0]

        #if t >= 1.0:
        #    return self.stops[-1][0]

        for i in range(len(self.stops)-1):
            if self.stops[i+1][0] > t:
                break

        (t0, rgb0), (t1, rgb1) = self.stops[i], self.stops[i+1]

        m = (t - t0) / (t1 - t0)

        r = rgb0.r + (rgb1.r - rgb0.r) * m
        g = rgb0.g + (rgb1.g - rgb0.g) * m
        b = rgb0.b + (rgb1.b - rgb0.b) * m

        return rgb(r, g, b)

rainbow = Gradient([
    (0/7.0, red),
    (1/7.0, orange),
    (2/7.0, yellow),
    (3/7.0, green),
    (4/7.0, blue),
    (5/7.0, indigo),
    (6/7.0, violet),
])

rgbgrad = Gradient([
    (0/3.0, red),
    (1/3.0, green),
    (2/3.0, blue),
])

halloween = Gradient([
    (0.0, black),
    (0.5, orange),
])

sprite = Gradient([
    (0/4.0, yellow),
    (1/4.0, green),
    (2/4.0, blue),
    (3/4.0, white),
    (4/4.0, yellow),
])

coke = Gradient([
    (0/3.0, red),
    (1/3.0, white),
    (2/3.0, black),
])

pepsi = Gradient([
    (0/3.0, red),
    (1/3.0, white),
    (2/3.0, blue),
])

tron = Gradient([
    (0/10.0, black),
    (2/10.0, rgb(0, 255, 255)),
    (8/10.0, rgb(0, 255, 255)),
])

def pixel(rgb, v=1):
    return chr(int(v*rgb.r)) + chr(int(v*rgb.g)) + chr(int(v*rgb.b))

t = 0.0
grad = tron
brightness = 0.7

def update(grad, dt):
    global t
    rgbs = [grad[i/96.0 + t] for i in range(48)]
    #rgbs = rgbs[2:] + rgbs[:2]
    #brightness = 0.5*(1+math.sin(2*t*math.pi/20))
    pixels = ''.join(pixel(rgb, brightness) for rgb in rgbs)
    loadPixels(pixels)
    time.sleep(1.0/100)
    t += dt
    if t >= 48.0:
        t -= 48.0

if __name__ == "__main__":
    #pyglet.clock.schedule_interval(update, 1/30.0)
    #pyglet.app.run()
    while True:
        for g in (rainbow, rgbgrad, halloween, sprite, coke, pepsi, tron):
            for i in range(50):
                update(g, 1.0/100)

