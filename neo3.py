#!/usr/bin/env python

import serial
import math
from collections import namedtuple
import pygame
import pygame.image
import pygame.time

pygame.init()

port = serial.Serial("/dev/ttyUSB0", baudrate=115200, timeout=0.5)

def escape(c):
    if c in "#$}":
        return "}" + chr(ord(c) ^ 0x20)
    else:
        return c

def loadPixels(rgbs):
    msg = '$P' + ''.join(escape(b) for b in rgbs) + '#'
    while True:
        port.write(msg)
        ack = port.read()
        if ack == '+':
            break

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
        t = math.modf(t)[0]
#        if t < 0.0:
#            return self.stops[0][1]
#        if t >= 1.0:
#            return self.stops[-1][1]

        for i in range(len(self.stops)-1):
            if self.stops[i+1][0] > t:
                break

        (t0, rgb0), (t1, rgb1) = self.stops[i], self.stops[i+1]

        alpha = (t - t0) / (t1 - t0)

        r = rgb0.r + (rgb1.r - rgb0.r) * alpha
        g = rgb0.g + (rgb1.g - rgb0.g) * alpha
        b = rgb0.b + (rgb1.b - rgb0.b) * alpha

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
brightness = 0.7
grads = (sprite, rainbow, rgbgrad, halloween, sprite, coke, pepsi, tron)

def update(dt):
    global t
    global grads
    #rgbs = [grads[0][(i+5*t)/48.0] for i in range(48)]
    #rgbs = [grads[0][(i+5*t)/48.0] for i in range(8)] 
    rgbs = [grads[0][i/16.0+t] for i in range(16)] * 3
    brightness = (1+math.sin(2*math.pi*t/5))/2
    #brightness = 0.6
    pixels = ''.join(pixel(rgb, brightness) for rgb in rgbs)
    loadPixels(pixels)
    t += dt
    if t > 5.0:
        t -= 5.0
        grads = grads[1:] + grads[:1]
        print clock.get_fps()


class ImageScanner(object):
    def __init__(self, filename):
        self.image = pygame.transform.flip(pygame.transform.scale(pygame.image.load(filename), (32, 16)), False, True)
        self.x = -32

    def get(self, x, y):
        x = int(x)
        y = int(y)
        if 0 <= x < 32 and 0 <= y < 16:
            (r, g, b, a) = self.image.get_at((x, y))
            return chr(r)+chr(g)+chr(b)
        else:
            return "\0\0\0"

    def update(self, dt):
        pixels = []
        x = int(5*self.x)
        w = 64
        for y in range(16):
            pixels.append(self.get((x+0) % w, y))
        for i in range(16):
            theta = 2 * math.pi * (i-0) / 16.0
            pixels.append(self.get((x + int(16-5*math.sin(theta))) % w, 8+int(4*math.cos(theta))))
        for y in range(16):
            pixels.append(self.get((x+31) % w, y))
        loadPixels(''.join(pixels))
        self.x += dt


import sys
filename = sys.argv[1]
#tiger = ImageScanner("sprite.png")
tiger = ImageScanner(filename)

clock = pygame.time.Clock()

if __name__ == "__main__":

    while True:
        update(clock.tick(60) / 1000.0)
        #tiger.update(clock.tick(60) / 1000.0)

