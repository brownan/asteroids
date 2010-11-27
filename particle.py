from __future__ import division

from OpenGL.GL import *
import numpy
from collections import deque
import random

"""This file holds a particle class, which tends to several particle effects

TODO: Rewrite this module as a C extension

"""

SPARK_DEGRADE = numpy.array([0.01, 0.05, 0.05], dtype=float)
DEBRIS_DEGRADE = numpy.array([0.05, 0.05, 0.05], dtype=float)

class Particles(object):
    def __init__(self):

        # Spark particles, which degrade their color to black and then disappear.
        # Each particle is a 3-tuple:
        # (pos, vel, color)
        self._sparks = deque(maxlen=70)
        self._debris = deque(maxlen=50)

    def update(self):

        # update pos and color
        for pos, vel, color in self._sparks:
            pos += vel
            color -= SPARK_DEGRADE
        for pos, vel, color in self._debris:
            pos += vel
            color -= DEBRIS_DEGRADE

        # Prune dead particles
        # XXX Could do this in an idle callback
        while self._sparks and self._sparks[0][2][0] <= 0:
            self._sparks.popleft()
        while self._debris and numpy.all(self._debris[0][2] <= 0):
            self._debris.popleft()

    def draw(self):
        # Draw all the particles on the screen
        glMatrixMode(GL_MODELVIEW)
        glPointSize(1)
        glBegin(GL_POINTS)

        for pos, _, color in self._sparks:
            glMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, color)
            glVertex3dv(pos)
        for pos, _, color in self._debris:
            glMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, color)
            glVertex3dv(pos)

        glEnd()

    def thrust(self, pos, direction):
        """Emits thrust particles from the given position in the given
        direction. direction should be normalized, but can have a different
        length to affect the speed.
        
        """
        for _ in xrange(random.randint(1, 3)):
            vel = direction + numpy.random.normal(0, scale=0.2, size=(3,))
            color = numpy.ones((3,))
            self._sparks.append(
                    (numpy.array(pos), vel, color)
                    )

    def explosion(self, pos, color, initvel=numpy.array([0,0,0],dtype=float)):
        for _ in xrange(random.randint(10,30)):
            vel = numpy.random.uniform(-4,4, size=(3,)) + initvel
            self._debris.append(
                    (numpy.array(pos, dtype=float), vel, numpy.array(color,dtype=float))
                    )

# A global particles object
particles = Particles()
update = particles.update
draw = particles.draw
thrust = particles.thrust
explosion = particles.explosion
