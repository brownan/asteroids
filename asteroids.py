from __future__ import division

from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.GLU import *

import math
import numpy

# Define these constants above the imports, some modules use them
WIDTH = 1000
HEIGHT = 800
fov = 45

distance = HEIGHT/2 / math.tan(fov/2*math.pi/180)

import model
import entity
import ship
import particle
import levels
import hud
import enemy

# Constants to draw axis lines
c = [
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1],
        [1, 1, 1],
    ]
txt = ["+X", "+Y", "+Z"]
v = [
        [.5*WIDTH, 0, 0],
        [0, .5*HEIGHT, 0],
        [0, 0, 10],
        [0, 0, 0],
    ]

def draw_string(x, y, z, txt):
    glRasterPos3f(x, y, z)
    for c in txt:
        glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(c))



class Game(object):
    def __init__(self):

        # list of all asteroids
        self.asteroids = set()

        # Setup the HUD
        self.hud = hud.HUD()

        # Player
        self.ship = ship.Ship(hud=self.hud)

        self.level = 1
        self.hud.set_level(self.level)
        self._level_frame = 0

        # Set of enemies
        self.enemies = set()

        # Set up first level
        self.asteroids.update(
                levels.level[self.level].create_asteroids()
                )
        
        # Start the game
        self._update_func = self._update_during_level
        self.ship.fly_in()

    def draw(self):
        glMatrixMode(GL_MODELVIEW)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Draw reference lines around viewport
        if 0:
            glDisable(GL_LIGHTING)
            glColor3f(0,1,0)
            glBegin(GL_LINE_STRIP)
            glVertex2i(0,0)
            glVertex2i(WIDTH,0)
            glVertex2i(WIDTH,HEIGHT)
            glVertex2i(0,HEIGHT)
            glVertex2i(0,0)
            glEnd()
            for i in range(3):
                glBegin(GL_LINES)
                glColor3fv(c[i])
                glVertex3fv(v[i])
                glColor3fv(c[3])
                glVertex3fv(v[3])
                glEnd()
            glColor3f(1, 1, 1)
            draw_string( v[ 0 ][ 0 ], v[ 0 ][ 1 ], v[ 0 ][ 2 ], txt[ 0 ] )
            draw_string( v[ 1 ][ 0 ], v[ 1 ][ 1 ], v[ 1 ][ 2 ], txt[ 1 ] )
            draw_string( v[ 2 ][ 0 ], v[ 2 ][ 1 ], v[ 2 ][ 2 ], txt[ 2 ] )

        self.hud.draw()

        glEnable(GL_LIGHTING)

        # Draw things
        for a in self.asteroids:
            a.draw()

        self.ship.draw()

        particle.draw()

        for enemy in self.enemies:
            enemy.draw()

        # flush the command pipeline and swap the buffers to display this frame
        glFlush()
        glutSwapBuffers()

    def update(self, value):
        """Periodic update function"""
        # Set a callback for 20ms
        glutTimerFunc(20, self.update, 0)

        # Change things here
        for a in self.asteroids:
            a.update()

        for enemy in self.enemies:
            enemy.update()

        self.ship.update()

        self.collision()

        particle.update()

        self.game_update()

        self._level_frame += 1
        if self._level_frame % 500 == 0:
            newalien = levels.level[self.level].enter_alien(self.ship)
            if newalien:
                self.enemies.add(newalien)

        # Cause a re-display
        glutPostRedisplay()

    def keypress(self, key, x, y):
        """An ascii key was pressed"""
        try:
            {       GLUT_KEY_UP: lambda: self.ship.thrust(1),
                    GLUT_KEY_LEFT: lambda: self.ship.turn(1),
                    GLUT_KEY_RIGHT: lambda: self.ship.turn(-1),
                    ' ': lambda: self.ship.trigger(1),
            }[key]()
        except KeyError:
            pass

    def keyup(self, key, x, y):
        try:
            {       GLUT_KEY_UP: lambda: self.ship.thrust(0),
                    GLUT_KEY_LEFT: lambda: self.ship.turn(0),
                    GLUT_KEY_RIGHT: lambda: self.ship.turn(0),
                    ' ': lambda: self.ship.trigger(0),
            }[key]()
        except KeyError:
            pass

    def collision(self):
        """Collision detection routine. Checks:
        1) collisions between the ship and each asteroid
        2) The ship's bullets and each asteroid
        3) The enemy's bullets and the ship

        """
        # List of asteroid objects to add or remove at the end of this frame
        # (so as not to mutate the asteroid set while we're iterating over it)
        toremove = set()
        toadd = set()
        enemies_toremove = set()

        ship = self.ship
        for bullet in ship.bullets.bullets:
            # Check the ship's bullet against each asteroid
            for asteroid in self.asteroids:
                if entity.check_collide(bullet, asteroid):
                    # Collide the bullet with the asteroid
                    bullet.ttl = 0
                    newasteroids = asteroid.split()
                    toadd.update(newasteroids)
                    toremove.add(asteroid)

            # Check the player's bullets against alien ships
            for enemy in self.enemies:
                if entity.check_collide(bullet, enemy):
                    bullet.ttl = 0
                    # Damage the alien ship
                    if enemy.damage(ship.bullets.damage):
                        # enemy was destroyed
                        enemies_toremove.add(enemy)

        if ship.is_active():
            # Check the ship against each asteroid
            for asteroid in self.asteroids:
                distance = numpy.linalg.norm(ship.pos - asteroid.pos)
                if distance < ship.radius + asteroid.radius:
                    # Collide the ship
                    newasteroids = asteroid.split()
                    toadd.update(newasteroids)
                    toremove.add(asteroid)
                    # hitting an asteroid does 1 damage
                    ship.damage(1)
                    if not ship.is_active():
                        break # skip all other collision checks

            # Check alien bullets against the player ship
            for enemy in self.enemies:
                for bullet in enemy.bullets.bullets:
                    # Collide this bullet with the player
                    if entity.check_collide(bullet, self.ship):
                        # Destroy the bullet
                        bullet.ttl = 0
                        # Damage the ship
                        ship.damage(enemy.bullets.damage)

            # Check player ship for collisions with alien ships
            # TODO

        self.asteroids -= toremove
        self.asteroids |= toadd
        self.enemies -= enemies_toremove

    def game_update(self):
        """Do various game administration here, such as level progression"""
        self._update_func()

    # UPDATE FUNCS BELOW
    # one of the update functions will be set as self._update_func and called
    # each frame
    def _update_during_level(self):
        """A level is in progress
        Check to see if all asteroids are dead, or the ship is dead, and change
        state accordingly
        """
        dead = self.ship.is_dead()
        lvl_complete = len(self.asteroids) == 0 and len(self.enemies) == 0

        # TODO: if dead and out of lives, go to game over state

        if dead and lvl_complete:
            # Go to next level, skip the fly-out
            self._t = 0
            self._update_func = self._update_ship_next_level

        elif dead:
            # Do a fly-in
            self._t = 0
            self._update_func = self._update_respawn

        elif lvl_complete:
            # Do a fly-out
            self.ship.fly_out()
            self._update_func = self._update_ship_next_level

    def _update_ship_next_level(self):
        """The ship is flying out, we are transitioning to a new level.
        Check if it's done flying out, and then initialize the new level
        """
        if self.ship.is_flying():
            self._t = 0
        else:
            self._t += 1

        if self._t >= 100:
            # Init next level and fly-in
            self.level += 1
            self._level_frame = 0
            self.hud.set_level(self.level)
            self.asteroids.update( levels.level[self.level].create_asteroids() )
            if self.ship.is_dead():
                self.ship.new_ship()
            self.ship.fly_in()
            self._update_func = self._update_during_level

    def _update_respawn(self):
        """The ship is dead, and we're going to spawn a new one"""
        self._t += 1
        if self._t > 100:
            self.ship.new_ship()
            self.ship.fly_in()
            self._update_func = self._update_during_level


def main():
    # Init window
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WIDTH, HEIGHT)
    glutCreateWindow("Asteroids")

    g = Game()

    # Setup callbacks
    glutDisplayFunc(g.draw)
    glutTimerFunc(0, g.update, 0)
    glutKeyboardFunc(g.keypress)
    glutKeyboardUpFunc(g.keyup)
    glutSpecialFunc(g.keypress)
    glutSpecialUpFunc(g.keyup)
    # TODO: glutReshapeFunc

    # Set up a perspective projection
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    gluPerspective(fov, WIDTH/HEIGHT, 10, distance+100)

    # Set up model transformations
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(
            # Eye coordinates:
            WIDTH/2.0, HEIGHT/2.0, distance+10,
            # Reference point coordinates
            WIDTH/2.0,HEIGHT/2.0,0,
            # direction of "up"
            0, 1, 0
            )

    # Lighting
    ambience = [0, 0, 0, 0]
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, ambience)
    glLightfv(GL_LIGHT0, GL_POSITION, (1,1,2,0))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2,0.2,0.2,1))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (.6,.6,.6,1))
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    # Blending
    glDisable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Interpolate shadows with GL_SMOOTH or render each face a single color
    # with GL_FLAT
    glShadeModel(GL_SMOOTH)

    # Setup Background color
    glClearDepth(1.0)
    glClearColor(0, 0, 0, 0)

    # For proper z-depth testing
    glEnable(GL_DEPTH_TEST)

    # For proper lighting calculation on scaled objects
    glEnable(GL_RESCALE_NORMAL)

    glutMainLoop()

if __name__ == "__main__":
    main()
