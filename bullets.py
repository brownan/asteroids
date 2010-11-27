from __future__ import division

from OpenGL.GLUT import glutSolidSphere
from OpenGL.GL import *

import numpy

import entity
import model
import util

from asteroids import WIDTH, HEIGHT

class Bullets(object):
    """A class to manage a set of bullets"""
    def __init__(self, ship):
        # A list of bullet entities
        self.bullets = set()

        self.ship = ship

        # Edit these instance variables to effect things
        self.maxbullets = 3
        self.maxtime = 50
        self.speed = 5
        self.rate = 5 # in frames

        self._cooldown = 0

    def fire(self):
        """Fire a bullet"""
        if len(self.bullets) >= self.maxbullets:
            return
        if self.ship._state not in (0, 1):
            return
        if self._cooldown > 0:
            return
        self._cooldown = self.rate

        shipdirection = self.ship.direction()

        # Fire the bullet from the ship's tip
        position = self.ship.pos.copy() + self.ship.direction()*20

        # Velocity has a base speed in the direction of the ship, and a
        # component from the ship's current velocity
        velocity = self.speed * shipdirection + self.ship.speed

        self.bullets.add(
                BulletEnt(position, velocity)
                )

    def update(self):
        """Call this once a frame. Updates the position of all bullets and
        removes any that have traveled their max distance
        """
        if self._cooldown > 0:
            self._cooldown -= 1
        toremove = []
        for b in self.bullets:
            b.update()
            if b.t > self.maxtime:
                toremove.append(b)

        for b in toremove:
            self.bullets.remove(b)

    def draw(self):
        for b in self.bullets:
            b.draw()

# Is set upon first initialization
bullet_dl = None

class BulletEnt(entity.Entity):
    WRAPDIST = 25

    def __init__(self, pos, vel):
        super(BulletEnt, self).__init__(
                None,
                1
                )
        self.pos = numpy.array(pos, dtype=float)
        self.velocity = vel
        self.speed = numpy.linalg.norm(vel)

        # Total time
        self.t = 0

        global bullet_dl
        if not bullet_dl:
            bullet_dl = util.get_displaylist()
            glNewList(bullet_dl, GL_COMPILE)
            glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, (0,1,0,1))
            glutSolidSphere(5, 5, 5)
            glEndList()


    def update(self):
        # update position
        self.pos += self.velocity
        self.t += 1

        if self.pos[0] > WIDTH + self.WRAPDIST:
            self.pos[0] = -self.WRAPDIST
        elif self.pos[0] < -self.WRAPDIST:
            self.pos[0] = WIDTH + self.WRAPDIST

        if self.pos[1] > HEIGHT + self.WRAPDIST:
            self.pos[1] = -self.WRAPDIST
        elif self.pos[1] < -self.WRAPDIST:
            self.pos[1] = HEIGHT + self.WRAPDIST

    def draw(self):
        glPushMatrix()
        glTranslated(*self.pos)
        glCallList(bullet_dl)
        glPopMatrix()
