from __future__ import division

from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.GLU import *

import math
import numpy

# Define these constants above the imports, some modules use them
WIDTH = 800
HEIGHT = 600
fov = 45

distance = HEIGHT/2 / math.tan(fov/2*math.pi/180)

import model
import entity
import ship
import particle
import levels
import hud

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
        # Players
        self.p = []

        # list of all asteroids
        self.asteroids = set()

        # Setup the HUD
        self.hud = hud.HUD()

        # Initialize entities
        self.p.append(
                ship.Ship(hud=self.hud)
                )

        self.level = 0

        # Set up first level
        self.asteroids.update(
                levels.level[self.level].create_asteroids()
                )

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

        for p in self.p:
            p.draw()

        particle.draw()

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

        for player in self.p:
            player.update()

        self.collision()

        particle.update()

        self.game_update()

        # Cause a re-display
        glutPostRedisplay()

    def keypress(self, key, x, y):
        """An ascii key was pressed"""
        try:
            {       GLUT_KEY_UP: lambda: self.p[0].thrust(1),
                    GLUT_KEY_LEFT: lambda: self.p[0].turn(1),
                    GLUT_KEY_RIGHT: lambda: self.p[0].turn(-1),
                    ' ': lambda: self.p[0].bullets.fire(),
            }[key]()
        except KeyError:
            pass

    def keyup(self, key, x, y):
        try:
            {       GLUT_KEY_UP: lambda: self.p[0].thrust(0),
                    GLUT_KEY_LEFT: lambda: self.p[0].turn(0),
                    GLUT_KEY_RIGHT: lambda: self.p[0].turn(0),
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

        # Check the ship's bullet against each asteroid
        for ship in self.p:
            for bullet in ship.bullets.bullets:
                for asteroid in self.asteroids:
                    if entity.check_collide(bullet, asteroid):
                        # Collide the bullet with the asteroid
                        bullet.t = 999
                        newasteroids = asteroid.split()
                        toadd.update(newasteroids)
                        toremove.add(asteroid)


        # Check the ship against each asteroid
        for ship in self.p:
            if not ship.is_active():
                continue
            for asteroid in self.asteroids:
                distance = numpy.linalg.norm(ship.pos - asteroid.pos)
                if distance < ship.radius + asteroid.radius:
                    # Collide the ship
                    newasteroids = asteroid.split()
                    toadd.update(newasteroids)
                    toremove.add(asteroid)
                    ship.damage(0)
                    if not ship.is_active():
                        break # go to next ship in ship list

        self.asteroids -= toremove
        self.asteroids |= toadd

    def game_update(self):
        """Do various game administration here, such as level progression"""
        ship = self.p[0]
        if len(self.asteroids) == 0:
            if ship.is_active():
                ship.fly_out()
            elif not ship.is_flying():
                # Go to next level
                self.level += 1
                self.asteroids.update( levels.level[self.level].create_asteroids() )
                ship.fly_in()

def main():
    # Init window
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(800, 600)
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

    gluPerspective(fov, WIDTH*1.0/HEIGHT, 10, distance+100)

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
