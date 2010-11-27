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
    def __init__(self, color=(0,1,0,1) ):
        # A list of bullet entities
        self.bullets = set()

        # Various bullet firing parameters. This class doesn't enforce these,
        # just keep track of them
        self.maxbullets = 3
        self.maxtime = 50
        self.speed = 5
        self.rate = 15 # in frames
        self.damage = 1

        self._cooldown = 0

        self.color = color

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
                BulletEnt(pos, vel, self.maxtime, self.color)
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

# Is set upon first initialization of each color
# maps color tuples to display list numbers
bullet_dl = {}

class BulletEnt(entity.Entity):
    WRAPDIST = 25

    def __init__(self, pos, vel, ttl, color):
        super(BulletEnt, self).__init__(
                None,
                1
                )
        self.pos = numpy.array(pos, dtype=float)
        self.velocity = vel
        self.speed = numpy.linalg.norm(vel)

        # Total time
        self.ttl = ttl

        try:
            self.dl = bullet_dl[color]
        except KeyError:
            self.dl = util.get_displaylist()
            glNewList(self.dl, GL_COMPILE)
            glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, color)
            glutSolidSphere(5, 5, 5)
            glEndList()
            bullet_dl[color] = self.dl


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
        glCallList(self.dl)
        glPopMatrix()
