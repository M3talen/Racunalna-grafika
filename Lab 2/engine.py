from pyglet.gl import *
import math
import numpy as np
from numpy.linalg import norm
from pyglet.window import key
import time
import cProfile
from camera import Camera
from pyrr import Vector3
from particle import ParticleBase
from particleSystem import ParticleSystem
import copy


class Window(pyglet.window.Window):
    global pyglet

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        start = time.time()
        self.set_minimum_size(600, 400)
        self.POV = 60
        self.source = [0, 0, 0]
        pyglet.clock.schedule_interval(self.update, 1.0/60.0)
        end = time.time()
        print(f'Load time : {end - start}')
        self.camera = Camera((0, 0, 1000))

        starTexture = pyglet.image.load('trace_01.png').get_texture()
        star2Texture = pyglet.image.load('trace_02.png').get_texture()
        twirtTexture = pyglet.image.load('light_01.png').get_texture()
        smoke01 = pyglet.image.load('smoke_10.png').get_texture()

        shootingStarsUp = ParticleBase(Vector3([0, 1, -5]), gravity=Vector3([0, -5000, 0]), params=[
                                       0, 0, 100., 20., 100., 3.], colorSystem=[[0.8, 0.1, 0.1], [0.4, 0.6, 0.4]], sizeSystem=[[100, 600], [50, 450]], rotationSystem=[False, 0, True])
        shootingStarsDown = ParticleBase(Vector3([0, -1, -5]), gravity=Vector3([0, 5000, 0]), params=[
                                         0, 0, 100., 50., 100., 3.], colorSystem=[[0.8, 0.1, 0.1], [0.4, 0.6, 0.4]], sizeSystem=[[100, 600], [50, 450]], rotationSystem=[False, 0, False])
        
        spining = ParticleBase(Vector3([0, 5, 0]), gravity=Vector3([0, 0, 0]), params=[0, 0, 0, 0, 0, 10], colorSystem=[
                               [0.8, 0.1, 0.1], [1, 0.1, 0.1]], sizeSystem=[[200, 200], [200, 200]], rotationSystem=[True, 1, False])

        smokeCirlce = ParticleBase(Vector3([0, 5, 0]), gravity=Vector3([0, 0, 0]), params=[0, 0, 0, 0, 0, 10], colorSystem=[
                               [0.01, 0.01, 0.01], [0.013, 0.013, 0.013]], sizeSystem=[[1000, 200], [1200, 300]], rotationSystem=[True, 1, False], billBoard=False)

        spiningParticleSystem = ParticleSystem(spining, twirtTexture, 10)
        starParticleSystem1 = ParticleSystem(shootingStarsUp, star2Texture, 100)
        starParticleSystem2 = ParticleSystem(shootingStarsDown, starTexture, 100)
        smokeCirlceParticleSystem2 = ParticleSystem(smokeCirlce, smoke01, 30)
    
        self.systems = [spiningParticleSystem,
                        starParticleSystem1, starParticleSystem2, smokeCirlceParticleSystem2]

    def on_key_press(self, key, modifiers):
        if modifiers == 18:
            if key == pyglet.window.key.UP:
                self.camera.lookAt[1] += 50
            elif key == pyglet.window.key.DOWN:
                self.camera.lookAt[1] -= 50
            elif key == pyglet.window.key.RIGHT:
                self.camera.lookAt[0] += 50
            elif key == pyglet.window.key.LEFT:
                self.camera.lookAt[0] -= 50
            elif key == pyglet.window.key.W:
                self.camera.lookAt[2] += 50
            elif key == pyglet.window.key.S:
                self.camera.lookAt[2] -= 50
        elif modifiers == 17:
            if key == pyglet.window.key.UP:
                self.camera.pos[2] -= 50
            elif key == pyglet.window.key.DOWN:
                self.camera.pos[2] += 50

        elif key == pyglet.window.key.UP:
            self.camera.pos[1] += 50
        elif key == pyglet.window.key.DOWN:
            self.camera.pos[1] -= 50
        elif key == pyglet.window.key.RIGHT:
            self.camera.pos[0] += 50
        elif key == pyglet.window.key.LEFT:
            self.camera.pos[0] -= 50

    def update(self, dt):
        for s in self.systems:
            s.update(dt)
        for i in range(len(self.systems)-1, -1, -1):
            if len(self.systems[i].particles) == 0:
                del self.systems[i]

    def drawOrigin(self):
        glPushMatrix()
        glColor3f(1, 1, 1)
        glBegin(GL_LINES)
        glVertex3f(0, 0, 0)
        glVertex3f(1000, 0, 0)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 800, 0)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, 600)
        glEnd()
        glPopMatrix()

    def on_draw(self):
        start = time.time()
        self.clear()
        glClear(GL_COLOR_BUFFER_BIT)
        self.drawOrigin()
        camera_positon = self.camera.get_postion()
        lookAt = self.camera.get_lookAt()

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.POV, self.width/self.height, 0.05, 10000)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        gluLookAt(camera_positon[0], camera_positon[1], camera_positon[2],
                  lookAt[0], lookAt[1], lookAt[2],
                  0.0, 1.0, 0.0)
        glPushMatrix()
        for s in self.systems:
            s.draw(camera_positon, lookAt)
        glPopMatrix()
        glFlush()

        end = time.time()
        #print(f'Frame time : {end - start}')


if __name__ == '__main__':
    window = Window(width=1000, height=500,
                    caption='Particle system', resizable=True)
    keys = key.KeyStateHandler()
    window.push_handlers(keys)

    #glClearColor(0.0, 0.0, 0.0 ,1)

    pyglet.app.run()
