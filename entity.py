from __future__ import division

from OpenGL.GL import *

import random
import numpy
import math

import model
import asteroids

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

class Ship(Entity):
    """Represents a player ship.
    
    """

    modelfile = "ship.obj"

    def __init__(self, playernum=0):
        # Don't call super method, we do our own initialization
        self.model = model.ObjModel(self.modelfile)
        self.pos = numpy.array((asteroids.WIDTH/2, asteroids.HEIGHT/2, 0))
        self.scale = 10
        
        if playernum != 0:
            # Change the body color of the ship
            pass # TODO

        # States:
        # 0 - ship under control, weapons disabled
        # 1 - ship under normal control for in game
        # 2 - flying in
        self._state = 0

        # Instead of defining a rotation axis and angle for this entity, store
        # the ship's direction configuration as: a unit vector for the
        # direction it's pointing, and a rotation angle about its axis.
        self.direction = numpy.array((0,1,0))
        self.rotangle = 0

    def draw(self):
        """Our own draw method, for alternate rotation"""
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glTranslated(*self.pos)
        glScaled(self.scale, self.scale, self.scale)

        # Do the rotations. The ship normally faces (0,1,0), so if
        # self.direction is that, no rotation is done
        # Common case: on the x/y plane
        if self.direction[2] == 0:
            sintheta = self.direction[0]
            costheta = self.direction[1]
            glRotated(math.acos(costheta), 0, 0, 1)

        self.model.draw()
        glPopMatrix()

    def fly_in(self):
        """Initiates a fly-in"""
        # Set the ship just behind the camera
        self.pos[0] = asteroids.HEIGHT/2
        self.pos[1] = asteroids.WIDTH/2 + asteroids.WIDTH/10
        self.pos[2] = asteroids.distance * 1.1
        # Aim it towards the field


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

        if self.pos[0] > asteroids.WIDTH + self.WRAPDIST:
            self.pos[0] = -self.WRAPDIST
        elif self.pos[0] < -self.WRAPDIST:
            self.pos[0] = asteroids.WIDTH + self.WRAPDIST

        if self.pos[1] > asteroids.HEIGHT + self.WRAPDIST:
            self.pos[1] = -self.WRAPDIST
        elif self.pos[1] < -self.WRAPDIST:
            self.pos[1] = asteroids.HEIGHT + self.WRAPDIST

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
        initialpos = [random.uniform(0,asteroids.WIDTH),
                random.uniform(0,asteroids.HEIGHT), 0]

        # generate a random velocity
        vel = [random.uniform(-maxvel, maxvel) for _ in xrange(2)]
        vel.append(0)

        scale = (size**2 + size * 5)# / 10.0

        self.WRAPDIST = scale*2

        super(Asteroid, self).__init__(self.asteroidmodelclass(), initialpos, vel,
                scale)

    def split(self):
        """Returns two new asteroids with the same momentum as this one."""
