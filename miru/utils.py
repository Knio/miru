# -*- test-case-name: miru.test.test_utils -*-
# Copyright (c) 2008 Drew Smathers.
# See LICENSE for details

import sys,ctypes

from twisted.python import filepath

from pyglet import gl
from pyglet import clock

def glvec(*args):
    return (gl.GLfloat * len(args))(*args)

## Debugging stuff

def show_caller(level):
    l = level + 1
    frame = sys._getframe(l)
    fname = frame.f_code.co_filename.split(os.path.sep)[-1]
    caller = frame.f_code.co_name
    lineno = frame.f_lineno
    print '%s %s %d' % (fname, caller, lineno)
showCaller = show_caller

_font_styles = {
    'mono' : ('VeraMono.ttf', 'Bitstream Vera Sans Mono'),
}
_defaultLoaded = False
def default_font(size=10, style='mono'):
    global _defaultLoaded
    from pyglet import font
    filename,face = _font_styles.get(style, _font_styles['mono'])
    if not _defaultLoaded:
        fontpath = filepath.FilePath(__file__).parent().child('data').child(filename)
        font.add_file(fontpath.path)
        _defaultLoaded = True
    return font.load(face, size)
defaultFont = default_font

def add_fps_display(context=None):
    if not context:
        from miru.context import context
    f = defaultFont(14)
    clock_display = clock.ClockDisplay(font=f, color=(0.,1.,0.,0.5))
    context.osd.add_object(clock_display)
addFpsDisplay = add_fps_display

def flatten(l, _cycle_checks=None):
    """Flatten a list of lists.
    """
    _cycle_checks = _cycle_checks or []
    newl = []
    for item in l:
        if isinstance(item, list):
            if item in _cycle_checks:
                raise ValueError, 'Cannot flatten cyclic lists'
            _cycle_checks.append(item)
            newl.extend(flatten(item, _cycle_checks))
        else:
            newl.append(item)
    return newl


def color(c0, c1=None, c2=None, c3=None):
    """Convert a color of any of the following formats RGB, RGBA, L, LA 
    from integral form in range [0,255] to floating point represetation
    in range [0.0, 1.0].  Internally, miru always uses the latter, so
    if you prefer the former, this function is your friend.
    """
    if c1 is None and c2 is None and c3 is None:
        return c0 / 255.
    if c2 is None and c3 is None:
        return (c0 / 255., c1 / 255.)
    if c3 is None:
        return (c0 / 255., c1 / 255., c2 / 255.)
    return (c0 / 255., c1 / 255., c2 / 255., c3 / 255.)

def point_in_rect(x, y, rx, ry, width, height):
    """2D point inside rectangle check
    """
    return (x >= rx) and (x <= rx + width) and\
           (y >= ry) and (y <= ry + height)

def change_cursor(style, window):
    cursor = window.get_system_mouse_cursor(style)
    window.set_mouse_cursor(cursor)


def scale_texcoords(texcoords, scale=1, format=2):
    c = list
    if type(texcoords) is tuple:
        c = tuple
    coords = []
    for i in range(0, len(texcoords), format):
        if format == 2:
            coords.extend(texcoords[i:i+format] + c((0,scale)))
        else:
            coords.extend(texcoords[i:i+format] + c((scale,)))
    return tuple(coords)



def select_object(x, y, objects=None):

    from miru.context import context

    if objects is None:
        objects = context.camera.objects

    # following technique is adapted from 
    # http://www.cse.msu.edu/~cse872/tutorial9.html
    
    w = context.window.width
    h = context.window.height


    select_buffer = ctypes.cast((100 * gl.GLuint)(), ctypes.POINTER(gl.GLuint))
    gl.glSelectBuffer(100, select_buffer)
  
    viewport = (4 * gl.GLint)()
    gl.glGetIntegerv(gl.GL_VIEWPORT, viewport)
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glLoadIdentity()

    # rotate the camera first
    angle = context.camera.angle
    gl.glRotatef(angle.z, 0, 0, 1)
    gl.glRotatef(angle.y, 0, 1, 0)
    gl.glRotatef(angle.x, 1, 0, 0)

    gl.gluPickMatrix(x, y, 3, 3, viewport)
    gl.glRenderMode(gl.GL_SELECT)
    gl.gluPerspective(45., w / float(h), 0.1, 1000.)
    gl.glMatrixMode(gl.GL_MODELVIEW)

    gl.glInitNames()
    gl.glPushName(-1)
    
    context.camera.render(select_pass=1, visible=objects)

    gl.glFlush()
    hits = gl.glRenderMode(gl.GL_RENDER)
    gl.glPopName()

    selected = None
    if hits:
        try:
            m = sys.maxint << 100
            idx = 0
            for i in range(0, 100, 4):
                if not select_buffer[i]:
                    selected = objects[idx]
                    break
                m = min(select_buffer[i+1], m)
                if m == select_buffer[i+1]:
                    idx = select_buffer[i+3]
        except IndexError:
            pass
    
    context.window.on_resize(context.window.width, context.window.height)

    return selected
