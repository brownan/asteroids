from __future__ import division

from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.GLU import *

import model, entity

import math
import numpy

WIDTH = 800
HEIGHT = 600

class Game(object):
    def __init__(self):
        # Players
        self.p = []

        # Master list of entities
        self.e = []

        # Initialize entities
        self.e.append(
                entity.Entity(
                    
                    model.ObjModel("ship.obj"),
                    (WIDTH/2,HEIGHT/2,0),
                    (0,0,0),
                    0.0,
                    10,
                    )
                )

        self.e.append( entity.Asteroid(4,5))
        self.e.append( entity.Asteroid(3,5))
        self.e.append( entity.Asteroid(2,5))
        self.e.append( entity.Asteroid(1,5))

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

        # Cause a re-display
        glutPostRedisplay()

def main():
    g = Game()

    # Init window
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WIDTH, HEIGHT)
    glutCreateWindow("Asteroids")

    # Setup callbacks
    glutDisplayFunc(g.draw)
    glutTimerFunc(0, g.update, 0)
    # TODO: glutReshapeFunc

    # Set up a perspective projection
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    fov = 45
    distance = HEIGHT/2.0 / math.tan(fov/2.0*math.pi/180.0)

    gluPerspective(fov, WIDTH*1.0/HEIGHT, 0.001, 100000000)

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

    # Interpolate shadows with GL_SMOOTH or render each face a single color
    # with GL_FLAT
    glShadeModel(GL_SMOOTH)

    # Setup Background color
    glClearDepth(1.0)
    glClearColor(0, 0, 0, 0)
    glEnable(GL_DEPTH_TEST)

    # Lighting
    #ambience = [1, 1, 1, 0]
    #glLightModelfv(GL_LIGHT_MODEL_AMBIENT, ambience)
    glLightfv(GL_LIGHT0, GL_POSITION, (1,1,-2,0))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.1,0.1,0.1,1))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (1.0,1.0,1.0,1))
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    glutMainLoop()

if __name__ == "__main__":
    main()
