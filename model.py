from OpenGL.GL import *

import random
import numpy
from collections import defaultdict

class Model(object):
    """A model that can be drawn on the screen"""
    def draw(self):
        """The draw method should call glBegin, some number of draw
        functions, and glEnd"""
        raise NotImplementedError()

class _Material(object):
    """Defines a particular material"""
    def __init__(self, ambient, diffuse, specular=(0,0,0,0), emission=(0,0,0,0)):
        assert len(ambient)==4
        assert len(diffuse)==4
        assert len(specular)==4
        assert len(emission)==4
        self.ambient = ambient
        self.diffuse = diffuse
        self.specular = specular
        self.emission = emission

    def activate(self):
        glMaterialfv(GL_FRONT, GL_AMBIENT, self.ambient)
        glMaterialfv(GL_FRONT, GL_DIFFUSE, self.diffuse)
        glMaterialfv(GL_FRONT, GL_SPECULAR, self.specular)
        glMaterialfv(GL_FRONT, GL_EMISSION, self.emission)

class ObjModel(Model):
    """A model loaded from an obj file"""
    def __init__(self, fileobj):
        if isinstance(fileobj, (str, unicode)):
            fileobj = open(fileobj, 'r')

        # Internal list of ordered points referenced by the face definitions.
        # These arrays start at 1.
        self.vertices = [None]
        self.normals = [None]

        # The material map. Maps material names to _Material objects
        self.mats = {}

        # Stores all the ploygons for this model
        # Keys are material names
        # Each value is a polygon list
        # Each polygon list item is a list of (vertex, normal), where normal
        # and vertex are numpy vectors. Together, the list of points define a
        # single polygon
        self.polys = defaultdict(list)
        currentmat = None

        for line in fileobj:
            if not line.strip():
                continue
            lineparts = line.strip().split()

            if lineparts[0] == "v":
                # Define a vertex
                _, p1, p2, p3 = line.split()
                self.vertices.append(numpy.array((float(p1), float(p2), float(p3))))

            elif lineparts[0] == "vn":
                _, p1, p2, p3 = line.split()
                self.normals.append(numpy.array((float(p1), float(p2), float(p3))))

            elif lineparts[0] == "mtllib":
                for filename in lineparts[1:]:
                    self._parsemat(filename)

            elif lineparts[0] == "usemtl":
                currentmat = self.mats[line.split()[1]]

            elif lineparts[0] == "f":
                # Define a single polygon
                face_components = line.split(None, 1)[1].split()
                # Go over each point in this polygon and gather them in this
                # list
                points = []
                for component in face_components:
                    # one vertex component of this polygon
                    point, texture, normal = component.split("/")
                    vertex = self.vertices[int(point)]
                    normalv = self.normals[int(normal)]
                    points.append((vertex, normalv))

                # Now that all points have been parsed and mapped for this
                # polygon, put it in the polygon list for the current material
                self.polys[currentmat].append(points)

    def _parsemat(self, matfilename):
        f = open(matfilename, 'r')
        try:

            matname = None
            mat = None
            for line in f:
                lineparts = line.strip().split()
                if not lineparts:
                    continue

                if lineparts[0] == "newmtl":
                    # Save existing mat if one was defined already
                    if matname:
                        print "saved mat", matname
                        self.mats[matname] = _Material(*mat)

                    # Start a new material
                    matname = line.split()[1]
                    # Stores four quadruplets: ambient, diffuse, specular, emission
                    mat = [(0,0,0,0)] * 4

                elif lineparts[0] in ("Ka", "Kd", "Ks", "Ke"):
                    m = {'a':0, 'd':1, 's': 2, 'e': 3}
                    color = [float(x) for x in line.split()[1:]]
                    if len(color) == 1:
                        color *= 3
                        color.append(0.0)
                    elif len(color) == 3:
                        color.append(0.0)

                    mat[m[line[1]]] = color
            # Save the final one
            if matname:
                print "saved mat", matname
                self.mats[matname] = _Material(*mat)
        finally:
            f.close()

    def draw(self):
        # Draw polygons
        for texture, polygons in self.polys.iteritems():
            if texture:
                texture.activate()
            for p in polygons:
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

