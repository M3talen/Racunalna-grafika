import sys
import time
import math
from pyglet.gl import *
from random import *
from pyrr import Vector3
import numpy as np
 

# params:
#   1. x Pos max offset
#   2. y Pos max offset
#   3. x,z velocity min/max
#   4. y velocity inital
#   5. y velocity offset
#   6. max lifetime


class ParticleBase:
    def __init__(self, pos, gravity=Vector3([0., -100, 0.]), params=[25, 50, 20, 300, 50, 1], colorSystem=[[1, 1, 1], [1, 1, 1]], sizeSystem=[[5, 5], [1, 1]], rotationSystem=[False,0,False], billBoard=True):
        self.pos = pos.copy()
        self.gravity = gravity.copy()
        self.vel = Vector3([0, 0, 0])
        self.lifeTime = time.time() + 1
        self.params = params
        self.colorSystem = colorSystem
        self.currentColor = colorSystem[0]
        self.sizeSystem = sizeSystem
        self.currentSize = sizeSystem[0]
        self.rotationSystem = rotationSystem
        self.currentRotation = 0
        self.billBoard = billBoard
        self.at = 0

    def randomize(self):
        self.pos[0] += gauss(0, self.params[0])
        self.pos[1] += uniform(0, self.params[1])
        self.vel = Vector3([uniform((-self.params[2]), self.params[2]),
                            self.params[3]+uniform(-self.params[4], self.params[4]), uniform((-self.params[2]), self.params[2])])
        self.lifeTime = time.time() + abs(gauss(0.0, self.params[5]))
        if(self.rotationSystem[0]):
            self.currentRotation = uniform(-self.rotationSystem[1]*50, 50*self.rotationSystem[1])

    def update(self, dt):
        if(self.rotationSystem[2]==True):
            self.pos -= self.vel * dt
            self.vel -= self.gravity * dt
        else:
            self.pos += self.vel * dt
            self.vel += self.gravity * dt
        c0 = lerp(self.colorSystem[0][0], self.colorSystem[1][0], self.at)
        c1 = lerp(self.colorSystem[0][1], self.colorSystem[1][1], self.at)
        c2 = lerp(self.colorSystem[0][2], self.colorSystem[1][2], self.at)
        self.currentColor = [c0, c1, c2]
        s0 = lerp(self.sizeSystem[0][0], self.sizeSystem[1][0], self.at)
        s1 = lerp(self.sizeSystem[0][1], self.sizeSystem[1][1], self.at)
        self.currentSize = [s0, s1]
        self.at += dt
        if(self.rotationSystem[0] is True):
            self.currentRotation += self.rotationSystem[1]


def lerp(a,  b,  f):
    return a + f * (b - a)
