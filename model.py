from OpenGL.GL import *
from OpenGL.GLUT import glutSolidSphere

import random
import numpy
from collections import defaultdict
import util

class Model(object):
    """A model that can be drawn on the screen"""

    def __init__(self):
        self._create_displaylist()

    def _create_displaylist(self, scale=1):
        """Create the display list.
        Sub-classes *should* call this sometime during the initialization
        """
        self.renderlist = util.get_displaylist()
        glNewList(self.renderlist, GL_COMPILE)
        if scale != 1:
            glPushMatrix()
            glScaled(scale, scale, scale)
        self.render()
        if scale != 1:
            glPopMatrix()
        glEndList()

    def render(self):
        """Override this method. This code renders the object and stores it in
        a display list.
        It should call glBegin, have some drawing methods, and then call glEnd
        """
        raise NotImplementedError()
    
    def draw(self):
        glCallList(self.renderlist)

class Sphere(Model):
    def render(self):
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, (1,0,0,0))
        glutSolidSphere(5, 5, 5)

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

    def __repr__(self):
        return "_Material(%r,%r,%r,%r)" % (self.ambient, self.diffuse, self.specular, self.emission)

    def activate(self):
        glMaterialfv(GL_FRONT, GL_AMBIENT, self.ambient)
        glMaterialfv(GL_FRONT, GL_DIFFUSE, self.diffuse)
        #glMaterialfv(GL_FRONT, GL_SPECULAR, self.specular)
        #glMaterialfv(GL_FRONT, GL_EMISSION, self.emission)

class ObjModel(Model):
    """A model loaded from an obj file"""
    def __init__(self, fileobj, scale=1):
        self._parse_model(fileobj)
        self._create_displaylist(scale)

    def _parse_model(self, fileobj):
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
        # Each polygon list item is a tuple: (triangles, quadralaterals, polygons).
        # Each of those is a list of (vertex, normal), where normal
        # and vertex are numpy vectors. Together, the list of points define a
        # single polygon
        self.polys = defaultdict(lambda: ([],[],[]))
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
                if len(points) == 3:
                    i = 0
                elif len(points) == 4:
                    i = 1
                else:
                    i = 2
                self.polys[currentmat][i].append(points)

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
                self.mats[matname] = _Material(*mat)
        finally:
            f.close()

    def render(self):
        # Draw polygons
        for texture, polygons in self.polys.iteritems():
            if texture:
                texture.activate()
            triangles, quads, polys = polygons
            if triangles:
                glBegin(GL_TRIANGLES)
                for (pt1,n1),(pt2,n2),(pt3,n3) in triangles:
                    glNormal3dv(n1)
                    glVertex3dv(pt1)
                    glNormal3dv(n2)
                    glVertex3dv(pt2)
                    glNormal3dv(n3)
                    glVertex3dv(pt3)
                glEnd()

            if quads:
                glBegin(GL_QUADS)
                for (pt1,n1),(pt2,n2),(pt3,n3),(pt4,n4) in quads:
                    glNormal3dv(n1)
                    glVertex3dv(pt1)
                    glNormal3dv(n2)
                    glVertex3dv(pt2)
                    glNormal3dv(n3)
                    glVertex3dv(pt3)
                    glNormal3dv(n4)
                    glVertex3dv(pt4)
                glEnd()

            for p in polys:
                glBegin(GL_POLYGON)
                for pt, n in p:
                    glNormal3dv(n)
                    glVertex3dv(pt)
                glEnd()

class AsteroidModel(ObjModel):
    parsed = None
    origverts = None

    def __init__(self):
        """Generate a randomized asteroid. Starts with a base asteroid.obj, and
        randomly adjusts the magnitudes of all vertices"""
        if AsteroidModel.parsed is None:
            super(AsteroidModel, self)._parse_model("asteroid.obj")
            AsteroidModel.parsed = dict(self.__dict__)
            AsteroidModel.origverts = [v.copy() for v in self.vertices[1:]]
        else:
            self.__dict__ = dict(AsteroidModel.parsed)

        # Since the vertices array holds objects that are also references by
        # the polys array, we can't change the objects in the vertices array.
        # But we can edit the values since numpy arrays are mutable
        # So, edit the vertex objects in-place, which changes them for every
        # instance, but it's okay since we take the snapshot into a displaylist
        # right after
        for vertex, origvertex in zip(self.vertices[1:], AsteroidModel.origverts):
            vertex[:] = origvertex * random.uniform(0.7, 1.3)

        super(AsteroidModel, self)._create_displaylist()

