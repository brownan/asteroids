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
    def __init__(self):
        # A list of bullet entities
        self.bullets = set()

        # Various bullet firing parameters. This class doesn't enforce these,
        # just keep track of them
        self.maxbullets = 3
        self.maxtime = 50
        self.speed = 5
        self.rate = 15 # in frames

        self._cooldown = 0

    def can_fire(self):
        """Returns true if, according to the constraints, should be allowed to
        fire its weapon"""
        if len(self.bullets) >= self.maxbullets:
            return False
        if self._cooldown > 0:
            return False
        return True

    def fire(self, pos, vel):
        """Fire a bullet"""
        self._cooldown = self.rate

        self.bullets.add(
                BulletEnt(pos, vel, self.maxtime)
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
            if b.ttl <= 0:
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

    def __init__(self, pos, vel, ttl):
        super(BulletEnt, self).__init__(
                None,
                1
                )
        self.pos = numpy.array(pos, dtype=float)
        self.velocity = vel
        self.speed = numpy.linalg.norm(vel)

        # Total time
        self.ttl = ttl

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
        self.ttl -= 1

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
