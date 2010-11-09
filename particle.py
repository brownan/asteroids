from __future__ import division

from OpenGL.GL import *
import numpy
from collections import deque
import random

"""This file holds a particle class, which tends to several particle effects

"""

SPARK_DEGRADE = numpy.array([0.01, 0.05, 0.05], dtype=float)

class Particles(object):
    def __init__(self):

        # Spark particles, which degrade their color to black and then disappear.
        # Each particle is a 3-tuple:
        # (pos, vel, color)
        self._sparks = deque()

    def update(self):

        # update sparks
        for pos, vel, color in self._sparks:
            pos += vel
            color -= SPARK_DEGRADE

        # Prune dead sparks
        # XXX Could do this in an idle callback
        while self._sparks and self._sparks[0][2][0] <= 0:
            self._sparks.popleft()

    def draw(self):
        # Draw all the particles on the screen
        glMatrixMode(GL_MODELVIEW)
        glPointSize(1)
        glBegin(GL_POINTS)

        for pos, _, color in self._sparks:
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
                    (pos.copy(), vel, color)
                    )
