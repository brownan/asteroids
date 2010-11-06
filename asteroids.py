from __future__ import division

from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.GLU import *

import model, entity

import math
import numpy

import profilerun

WIDTH = 800
HEIGHT = 600

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


fov = 45
distance = HEIGHT/2 / math.tan(fov/2*math.pi/180)

class Game(object):
    def __init__(self):
        # Players
        self.p = []

        # Master list of entities
        self.e = []

        # Initialize entities
        self.e.append(
                entity.Ship()
                )

        self.e.append( entity.Asteroid(4,1))
        self.e.append( entity.Asteroid(3,1))
        self.e.append( entity.Asteroid(2,1))
        self.e.append( entity.Asteroid(1,1))

        self.t = 0
        self.frameno = 0

    def draw(self):
        glMatrixMode(GL_MODELVIEW)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Draw reference lines around viewport
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
        glEnable(GL_LIGHTING)

        # Draw things
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.8,0.8,0.8]);
        for e in self.e:
            e.draw()

        # ??
        glFlush()
        glutSwapBuffers()

    def update(self, value):
        """Periodic update function"""
        # Set a callback for 20ms
        glutTimerFunc(20, self.update, 0)

        # Change things here
        for e in self.e:
            e.update()

        if 0:
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            t = self.t
            gluLookAt(
                    # Eye coordinates:
                    math.sin(t)*WIDTH+WIDTH/2, HEIGHT/2.0, math.cos(t)*(distance+10),
                    # Reference point coordinates
                    WIDTH/2.0,HEIGHT/2.0,0,
                    # direction of "up"
                    0, 1, 0
                    )
            glLightfv(GL_LIGHT0, GL_POSITION, (-1,0,0,0))
            self.t += 0.03
        # Cause a re-display
        glutPostRedisplay()

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
    # TODO: glutReshapeFunc

    # Set up a perspective projection
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    #gluPerspective(fov, WIDTH*1.0/HEIGHT, distance-100, distance+100)
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
