from OpenGL.GL import *

def get_displaylist():
    new_list = glGenLists(1)
    if new_list == 0:
        raise RuntimeError("Could not allocate a display list")
    return new_list

def _make_dl_hud_prepare():
    """Makes a displaylist that prepares the projection and modelview matrices
    for drawing the hud"""
    dl_num = get_displaylist()
    glNewList(dl_num, GL_COMPILE)

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, 1, 0, 1, -1, 1)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glDisable(GL_DEPTH_TEST)
    glDepthMask(GL_FALSE)
    glDisable(GL_LIGHTING)

    glEndList()
    return dl_num

def _make_dl_hud_restore():
    """Makes a displaylist that restores the modelview and projection matrices
    """
    dl_num = get_displaylist()
    glNewList(dl_num, GL_COMPILE)

    glEnable(GL_DEPTH_TEST)
    glDepthMask(GL_TRUE)
    glEnable(GL_LIGHTING)

    glPopMatrix()

    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    
    glMatrixMode(GL_MODELVIEW)

    glEndList()
    return dl_num

def _make_dl_hud_static():
    """Returns a displaylist that draws static elements of the hud"""
    dl_num = get_displaylist()
    glNewList(dl_num, GL_COMPILE)

    glColor3f(0.0,1.0,0.0)
    glBegin(GL_LINE_LOOP)
    glVertex2d(0.5,0.5)
    glVertex2d(0.6,0.5)
    glVertex2d(0.6,0.6)
    glVertex2d(0.5,0.6)
    glEnd()

    glEndList()
    return dl_num

class HUD(object):
    def __init__(self):
        dl_hud_prepare = _make_dl_hud_prepare()
        dl_hud_restore = _make_dl_hud_restore()
        dl_static = _make_dl_hud_static()

        # create hud element display lists
        self.level_dl = get_displaylist()
        self.lives_dl = get_displaylist()
        self.shields_outline = get_displaylist()
        self.shields_level = get_displaylist()

        # initialize hud display list elements
        #self.set_level(0)
        #self.set_lives(3)
        #self.set_shields_max(5)
        #self.set_shields(5)

        # Create master display list
        self.master_dl = get_displaylist()
        glNewList(self.master_dl, GL_COMPILE)
        glCallList(dl_hud_prepare)
        glCallList(dl_static)
        glCallList(self.level_dl)
        glCallList(self.lives_dl)
        glCallList(self.shields_outline)
        glCallList(self.shields_level)
        glCallList(dl_hud_restore)
        glEndList()

    def draw(self):
        """Draws the hud"""
        glCallList(self.master_dl)

    def set_level(self, level):
        pass

    def set_lives(self, lives):
        pass

    def set_shields(self, amt):
        border = 0.000
        length = amt * 0.05 - border
        print "setting shields to", amt

        glNewList(self.shields_level, GL_COMPILE)
        glColor3f(0.0, 1.0, 0.0)
        glBegin(GL_QUADS)
        glVertex2d(0.5+border,       1-0.01-border)
        glVertex2d(0.5+border,       1-0.02+border)
        glVertex2d(0.5+length+border,1-0.02+border)
        glVertex2d(0.5+length+border,1-0.01-border)
        glEnd()

        glEndList()

    def set_shields_max(self, upper):
        length = upper * 0.05
        glNewList(self.shields_outline, GL_COMPILE)
        
        glColor3f(0.0,1.0,0.0)
        glBegin(GL_LINE_LOOP)
        glVertex2d(0.5,1-0.01)
        glVertex2d(0.5,1-0.02)
        glVertex2d(0.5+length,1-0.02)
        glVertex2d(0.5+length,1-0.01)
        glEnd()

        glEndList()
