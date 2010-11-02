from OpenGL.GL import *

import random
import numpy

class Model(object):
    """A model that can be drawn on the screen"""
    def draw(self):
        """The draw method should call glBegin, some number of draw
        functions, and glEnd"""
        raise NotImplementedError()

class ObjModel(Model):
    """A model loaded from an obj file"""
    def __init__(self, fileobj):
        if isinstance(fileobj, (str, unicode)):
            fileobj = open(fileobj, 'r')

        self.vertices = [None]
        self.normals = [None]

        # list of polygons
        # each item is a list of (vertex, normal), where normal and vertex are
        # indicies into the normal and vertices array
        self.triangles = []
        self.quads = []
        self.polys = []

        for line in fileobj:
            if not line.strip():
                continue

            if line[0] == "v":
                # Define a vertex
                _, p1, p2, p3 = line.split()
                self.vertices.append(numpy.array((float(p1), float(p2), float(p3))))

            if line[0:2] == "vn":
                _, p1, p2, p3 = line.split()
                self.normals.append(numpy.array((float(p1), float(p2), float(p3))))

            if line[0] == "f":
                # Define a single polygon
                face_components = line.split(None, 1)[1].split()
                points = []
                for component in face_components:
                    # one vertex component of this polygon
                    point, texture, normal = component.split("/")
                    vertex = self.vertices[int(point)]
                    normalv = self.normals[int(normal)]
                    points.append((vertex, normalv))

                if len(points) == 3:
                    self.triangles.append(points)
                elif len(points) == 4:
                    self.quads.append(points)
                else:
                    self.polys.append(points)

    def draw(self):
        # Draw triangles
        if self.triangles:
            glBegin(GL_TRIANGLES)
            for tri in self.triangles:
                (p1,n1),(p2,n2),(p3,n3) = tri
                glNormal3dv(n1)
                glVertex3dv(p1)
                glNormal3dv(n2)
                glVertex3dv(p2)
                glNormal3dv(n3)
                glVertex3dv(p3)
            glEnd()

        # Draw quadralaterals
        if self.quads:
            glBegin(GL_QUADS)
            for quad in self.quads:
                (p1,n1),(p2,n2),(p3,n3),(p4,n4) = quad
                #print "->%s\n  %s\n  %s\n  %s" % (n1,n2,n3,n4)
                glNormal3dv(n1)
                glVertex3dv(p1)

                glNormal3dv(n2)
                glVertex3dv(p2)

                glNormal3dv(n3)
                glVertex3dv(p3)

                glNormal3dv(n4)
                glVertex3dv(p4)
            glEnd()

        # Draw polygons
        for p in self.polys:
            glBegin(GL_POLYGON)
            for pt, n in p:
                glNormal3dv(n)
                glVertex3dv(pt)
            glEnd()


class AsteroidModel(ObjModel):
    def __init__(self):
        """Generate a randomized asteroid. Starts with a base asteroid.obj, and
        randomly adjusts the magnitudes of all vertices"""
        super(AsteroidModel, self).__init__("asteroid.obj")

        for vertex in self.vertices[1:]:
            vertex *= random.uniform(0.7,1.3)

class MichaelAsteroidModel(Model):
    asteroid_verticies = numpy.array([
            [0.0, 0.0, 1.0], # Top

            # Upper Ring
            [0.0, 1.0, 0.33], # 1
            [-0.66, 0.66, 0.33],
            [-1.0, 0.0, 0.33],
            [-0.66, -0.66, 0.33],
            [0.0, -1.0, 0.33],
            [0.66, -0.66, 0.33],
            [1.0, 0.0, 0.33],
            [0.66, 0.66, 0.33], # 8

            [0.0, 0.0, -1.0], # Bottom

            # Lower Ring
            [0.0, 1.0, -0.33], # 10
            [-0.66, 0.66, -0.33],
            [-1.0, 0.0, -0.33],
            [-0.66, -0.66, -0.33],
            [0.0, -1.0, -0.33],
            [0.66, -0.66, -0.33],
            [1.0, 0.0, -0.33],
            [0.66, 0.66, -0.33]
        ])
    def __init__(self):
        raise NotImplementedError()
        max_variance = 0.3
        min_variance = 0.2
        variance = random.uniform(min_variance, max_variance)
        
        self.vertices = self.asteroid_verticies.copy()
        for (x,y), value in numpy.ndenumerate(self.vertices):
            self.vertices[x,y] += random.uniform(-variance, variance)

    def _v(self, n):
        glNormal3dv(self.vertices[n])
        glVertex3d(-self.vertices[n,0], -self.vertices[n,1], -self.vertices[n,2])

    def draw(self):
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.2, 0.2, 0.2])

        v = self._v

        # top fan
        glBegin(GL_TRIANGLE_FAN)
        for i in xrange(9):
            v(i)
        v(1)
        glEnd()

        glBegin(GL_TRIANGLES)
        for i in xrange(1,8):
            v(i); v(i+9); v(i+1)
            v(i+1); v(i+9); v(i+10)
        v(8); v(17); v(1)
        v(1); v(17); v(10)
        v(1); v(10); v(10);
        v(10); v(10); v(11);
        glEnd()

        glBegin(GL_TRIANGLE_FAN)
        for i in xrange(9, 18):
            v(i)
        v(10)
        glEnd()
