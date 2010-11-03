from __future__ import division

from OpenGL.GL import *

import random
import numpy
import math

import model
from asteroids import WIDTH, HEIGHT

class Entity(object):
    """An entity is anything that can be drawn on the screen at a particular
    position and orientation.

    This is a base class. Subclasses should implement the update() method,
    which is called each frame.

    """
    def __init__(self, model, initpos, rotaxis, rotangle, scale=1):
        """Specify a model, initial position, and initial rotation.
        initpos is a triplet of coordinates to be passed into glTranslate
        rotaxis is a vector specifying the axis of rotation about the origin
        rotangle is an angle, in degrees to rotate the entity initially

        Give the scale to scale the model up or down
        """
        self.model = model
        assert len(initpos) == 3
        self.pos = numpy.array(initpos, dtype=float)
        assert len(rotaxis) == 3
        self.rotaxis = numpy.array(rotaxis, dtype=float)
        self.rotangle = float(rotangle)
        self.scale = float(scale)

    def draw(self):
        """Draws the model on the screen. You probably don't need to override
        this"""
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()

        # Set material with glMaterial
        # TODO

        # Do translations
        glTranslated(*self.pos)

        # Do scaling
        if self.scale != 1:
            glScaled(self.scale, self.scale, self.scale)

        # Do rotation
        glRotatef(self.rotangle, *self.rotaxis)

        # draw the model
        self.model.draw()

        glPopMatrix()

    def update(self):
        pass # Override this

class FloatingEntity(Entity):
    """Given an initial velocity and rotational velocity, updates by those
    constants each frame. Good for asteroids and debris
    """
    WRAPDIST = 30
    def __init__(self, model, initpos, vel, scale=1):
        """Create a new floating entity with the given model at the given
        initial position. It will have a the given velocity vel, in world units
        per frame.
        """
        # Generate a random axis of rotation
        theta = random.uniform(0, 360)
        phi = random.uniform(0, 180)
        rotaxis = [
                math.cos(theta)*math.sin(phi),
                math.sin(theta)*math.sin(phi),
                math.cos(theta),
                ]

        # Generate a random rotational velocity in degrees per frame
        self.dtheta = random.uniform(-5, 5)

        self.vel = numpy.array(vel, dtype=float)

        super(FloatingEntity, self).__init__(model, initpos, rotaxis, 0, scale)

    def update(self):
        self.pos += self.vel
        self.rotangle += self.dtheta

        if self.pos[0] > WIDTH + self.WRAPDIST:
            self.pos[0] = -self.WRAPDIST
        elif self.pos[0] < -self.WRAPDIST:
            self.pos[0] = WIDTH + self.WRAPDIST

        if self.pos[1] > HEIGHT + self.WRAPDIST:
            self.pos[1] = -self.WRAPDIST
        elif self.pos[1] < -self.WRAPDIST:
            self.pos[1] = HEIGHT + self.WRAPDIST

class Asteroid(FloatingEntity):
    """Represents an asteroid on the field"""
    asteroidmodelclass = model.AsteroidModel

    def __init__(self, size, maxvel):
        """Creates an asteroid randomly on the field with the specified size
        and maximum velocity

        size should be an integer >= 1

        If direction is specified, the asteroid is given a veloicty in the
        direction specified, with some variance.

        """
        # Generate a random starting pos
        initialpos = [random.uniform(0,WIDTH),
                random.uniform(0,HEIGHT), 0]

        # generate a random velocity
        vel = [random.uniform(-maxvel, maxvel) for _ in xrange(2)]
        vel.append(0)

        scale = (size**2 + size * 5)# / 10.0

        self.WRAPDIST = scale*2

        super(Asteroid, self).__init__(self.asteroidmodelclass(), initialpos, vel,
                scale)

    def split(self):
        """Returns two new asteroids with the same momentum as this one."""
