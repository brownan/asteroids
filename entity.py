from __future__ import division

from OpenGL.GL import *

import random
import numpy
import math

import model
import particle

def check_collide(ent1, ent2):
    dist = numpy.linalg.norm(ent1.pos - ent2.pos)
    return dist < ent1.radius + ent2.radius

class Entity(object):
    """An entity is anything that can be drawn on the screen at a particular
    position and orientation.

    This is a base class. Subclasses should implement the update() method,
    which is called each frame.

    """
    def __init__(self, model, radius):
        """Specify a model, and a radius for collision detection.
        """
        self.model = model
        self.radius = radius

    def draw(self):
        """Routine for drawing this entity. Subclasses should override this"""
        raise NotImplementedError()


    def update(self):
        """Override this with anything the entity may want to do each frame"""
        pass # Override this

# Can't import this before, the base class must be defined before other modules
# can be imported
from asteroids import WIDTH, HEIGHT

class FloatingEntity(Entity):
    """Given an initial velocity and rotational velocity, updates by those
    constants each frame. Good for asteroids and debris
    """
    WRAPDIST = 30
    def __init__(self, model, initpos, vel, radius, scale=1):
        """Create a new floating entity with the given model at the given
        initial position. It will have a the given velocity vel, in world units
        per frame.
        """

        assert len(initpos) == 3
        self.pos = numpy.array(initpos, dtype=float)
        self.rotangle = 0
        self.scale = float(scale)

        # Generate a random axis of rotation
        theta = random.uniform(0, 360)
        phi = random.uniform(0, 180)
        rotaxis = [
                math.cos(theta)*math.sin(phi),
                math.sin(theta)*math.sin(phi),
                math.cos(theta),
                ]
        self.rotaxis = numpy.array(rotaxis, dtype=float)

        # Generate a random rotational velocity in degrees per frame
        self.dtheta = random.uniform(-5, 5)

        self.vel = numpy.array(vel, dtype=float)

        super(FloatingEntity, self).__init__(model, radius)

    def draw(self):
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()

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

    def __init__(self, size, maxvel, initialpos=None):
        """Creates an asteroid randomly on the field with the specified size
        and maximum velocity

        size should be an integer >= 1

        If direction is specified, the asteroid is given a veloicty in the
        direction specified, with some variance.

        """
        # Generate a random starting pos
        # TODO: asteroids appear at the screen edge
        if initialpos is None:
            initialpos = [random.uniform(0,WIDTH),
                    random.uniform(0,HEIGHT), 0]

        # generate a random velocity
        vel = [random.uniform(-maxvel, maxvel) for _ in xrange(2)]
        vel.append(0)

        self.size = size
        self.maxvel = maxvel

        scale = (3*size**2 + size * 5)

        self.WRAPDIST = scale*2

        super(Asteroid, self).__init__(self.asteroidmodelclass(), initialpos, vel,
                1.5*scale, scale)

    def split(self):
        """Returns two new asteroids with the same momentum as this one."""
        particle.explosion(self.pos, (1,1,1))
        if self.size == 1:
            return ()
        return (Asteroid(self.size-1, self.maxvel*1.1, self.pos) for _ in xrange(2))
