from OpenGL.GL import glGenLists

def get_displaylist():
    new_list = glGenLists(1)
    if new_list == 0:
        raise RuntimeError("Could not allocate a display list")
    return new_list

