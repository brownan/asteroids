from __future__ import division

from OpenGL.GL import *
from OpenGL.GLUT import *

import numpy
import math

import entity
import bullets
import bezier
import model
from asteroids import WIDTH, HEIGHT, distance
import particle

SHIP_ACCEL = 0.1
SHIP_ROTSPEED = 4
SHIP_SHIELD_FADE = 0.08

# Ship states
SHIP_DEAD = 4 
SHIP_ACTIVE = 1
SHIP_FLYING_IN = 2
SHIP_FLYING_OUT = 3

class Ship(entity.Entity):
    """Represents a player ship.
    
    """
    WRAPDIST = 25
    modelfile = "ship.obj"

    def __init__(self, playernum=0, hud=None):
        # Don't call super method, we do our own initialization
        self.model = model.ObjModel(self.modelfile)
        self.pos = numpy.array((WIDTH/2, HEIGHT/2, 0),dtype=float)
        self.scale = 15
        self.radius = 2*self.scale

        self.lives = 3
        hud.set_lives(self.lives)

        if playernum != 0:
            # Change the body color of the ship
            pass # TODO
        
        self.hud = hud

        # States:
        # 0 - control disabled, nothing happening
        # 1 - ship under normal control for in game
        # 2 - flying in
        # 3 - flying out
        # 4 - Blown up
        self._state = 0

        # Store the ship's orientation as three angles:
        # theta is the rotation about the Z axis. When phi is 0, this is the
        # angle the ship is pointing on the X/Y plane. 0 is straight up, and
        # increasing angles turn the ship clockwise.
        self.theta = 30

        # phi is the counterclockwise rotation about the X axis (out of the
        # page) Together with theta they describe the ship's direction
        self.phi = 0

        # rot is the rotation about the ship's axis (Y). When phi is 90, this
        # variable is equivilant to theta
        self.rot = 0

        # translational velocity
        self.speed = numpy.array([0,0,0], dtype=float)

        # Acceleration, in world units per frame^2
        self.accel = 1

        # The player's bullets
        self.bullets = bullets.Bullets(self)

        self.shieldmax = 5
        self.shields = self.shieldmax
        if self.hud:
            self.hud.set_shields_max(self.shieldmax)
            self.hud.set_shields(self.shields)

        # Initialize movement state vars
        self._thrusting = 0
        self._turning = 0

        # Shield visibility
        self._shield_vis = 0

    def direction(self):
        """Computes the unit vector representing the ship's direction"""
        # Start with the ship's un-rotated direction, as a column vector
        direction = numpy.matrix("[0;1;0]", dtype=float)

        # Apply a rotation about the X axis
        cosphi = math.cos(self.phi*math.pi/180)
        sinphi = math.sin(self.phi*math.pi/180)
        xrot = numpy.matrix([
                             [1, 0, 0],
                             [0, cosphi, -sinphi],
                             [0, sinphi, cosphi],
                             ], dtype=float)
        # Apply a rotation about the Z axis
        costheta = math.cos(self.theta*math.pi/180)
        sintheta = math.sin(self.theta*math.pi/180)
        zrot = numpy.matrix([
                             [costheta, -sintheta, 0],
                             [sintheta, costheta, 0],
                             [0, 0, 1],
                             ], dtype=float)

        return numpy.array(zrot * xrot * direction).squeeze()

    def update(self):
        # Choose the appropriate update function based on the current state
        p = lambda: None
        [p, self._update_normal, # 0 and 1
                self._update_bezier, self._update_bezier, # 2 and 3
                p][self._state]()

        # Thrusting?
        if self._thrusting:
            direction = self.direction()
            self.speed += SHIP_ACCEL * direction
            particle.thrust(self.pos-direction*4, self.speed - direction*2)
        if self._turning:
            self.theta += SHIP_ROTSPEED * self._turning
            self.rot = self.theta

        # update bullets
        self.bullets.update()

        if self._shield_vis > 0:
            self._shield_vis -= SHIP_SHIELD_FADE

    def _update_normal(self):
        # Update position based on current speed
        self.pos += self.speed

        # Looping around:
        if self.pos[0] > WIDTH + self.WRAPDIST:
            self.pos[0] = -self.WRAPDIST
        elif self.pos[0] < -self.WRAPDIST:
            self.pos[0] = WIDTH + self.WRAPDIST

        if self.pos[1] > HEIGHT + self.WRAPDIST:
            self.pos[1] = -self.WRAPDIST
        elif self.pos[1] < -self.WRAPDIST:
            self.pos[1] = HEIGHT + self.WRAPDIST

    def _update_bezier(self):
        direction = self.direction()
        particle.thrust(self.pos-direction*4, self.speed - direction*2)
        self._t += 1
        self.rot += 2
        current = self._bezier.B(self._t)
        self.pos = current[:3]
        self.theta = current[3]
        self.phi = current[4]
        if self._t >= self._bezier.tmax:
            if self._state == 2:
                self._state = 1
            else:
                self._state = 0

    def thrust(self, on):
        """Turns thrust on or off"""
        if self._state != 1:
            return
        self._thrusting = on

    def turn(self, dir):
        """Turns left or right"""
        if self._state != 1:
            return
        self._turning = dir

    def draw(self):
        """Our own draw method, for alternate rotation"""
        # Draw our bullets
        self.bullets.draw()

        if self._state == 4:
            return

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()

        glTranslated(*self.pos)
        glScaled(self.scale, self.scale, self.scale)

        # Do the rotations. The ship normally faces (0,1,0) into the page
        # normal turn
        glRotated(self.theta, 0,0,1)

        phi = self.phi
        # skip common case: phi is 0
        if phi:
            glRotated(phi, 1,0,0)

        # ship's axis rotation. Do this last, so it's always along the ship's
        # axis, not the world's Y axis
        glRotated(self.rot, 0,1,0)

        self.model.draw()

        # Draw shields
        if self._shield_vis > 0:
            glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, (0,1,0,self._shield_vis,))
            glDepthMask(GL_FALSE)
            glEnable(GL_BLEND)
            glutSolidSphere(2, 6, 6)
            glDepthMask(GL_TRUE)
            glDisable(GL_BLEND)

        glPopMatrix()

    def _reset(self):
        """Resets movement parameters"""
        print "movement reset"
        self.speed[:] = 0
        self._turning = 0
        self._thrusting = 0

    def fly_in(self):
        """Initiates a fly-in"""
        self._state = 2
        self._reset()

        # Set up a quadratic bezier curve with p0 just behind the camera, p1 at
        # some point near the x/y plane, and p2 at our destination: the center
        # of the screen on the x/y plane

        # first 3 are position, second two are theta and phi
        p0 = numpy.array([
                          WIDTH*0.6,
                          HEIGHT/2,
                          distance * 1.1,
                          90.0,
                          -90.0], dtype=float)
        p1 = numpy.array([
                          WIDTH*0.6,
                          HEIGHT/2,
                          distance * 0.3,
                          90.0,
                          -80.0], dtype=float)
        p2 = numpy.array([
                          WIDTH/2,
                          HEIGHT/2,
                          0,
                          90,
                          0], dtype=float)

        # Set the ship at p0
        self.pos[:] = p0[:3]
        self.theta = p0[3]
        self.phi = p0[4]

        self._t = 0

        # Specify the number of frames to take as the 4th parameter
        self._bezier = bezier.Quadratic(p0,p1,p2,100)

    def fly_out(self):
        self._state = 3
        self._reset()
        
        # Starting point: the ship's current position
        p0 = numpy.empty((5,))
        p0[:3] = self.pos
        p0[3] = self.theta
        p0[4] = self.phi


        # Ending point: behind the camera
        p2 = numpy.array([
                          WIDTH*0.6,
                          HEIGHT/2,
                          distance * 1.1,
                          0.0,
                          90.0], dtype=float)

        # Compute the mid-point by computing the ship's current direction and
        # going forward a bit
        p1 = p0.copy()
        p1[:3] += self.direction() * 200
        # adjust the angles a bit too
        p1[3:] = (0.2*p0[3:] + 1.8*p2[3:]) / 2

        self._t = 0

        self._bezier = bezier.Quadratic(p0,p1,p2,200)

    def damage(self, source):
        """The ship has taken damage.
        Source 0 is an asteroid
        source 1 is a bullet
        """
        if self.shields == 0:
            # KABOOM
            print "Kaboom"
            particle.explosion(self.pos, (0,10,0))
            self.lives -= 1
            self.hud.set_lives(self.lives)
            self._state = 4
            self._reset()
        else:
            self.shields -= 1
            if self.hud:
                self.hud.set_shields(self.shields)
            self._shield_vis = 1
            print "Shields:", self.shields

    def new_ship(self):
        """Resets stats and such"""
        self.shields = self.shieldmax
        if self.hud:
            self.hud.set_shields(self.shields)
    
    def is_active(self):
        """Returns true if the state of this ship is active in the game, able
        to fire and take damage."""
        return self._state == 1

    def is_flying(self):
        return self._state == 2 or self._state == 3

    def is_dead(self):
        return self._state == SHIP_DEAD
