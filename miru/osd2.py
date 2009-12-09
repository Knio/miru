# Copyright (c) 2008 Drew Smathers.
# See LICENSE for details
"""On screen display
"""

from UserList import UserList

from pyglet import gl

from miru import imiru
from miru import core

from zope.interface import implements

class OSD(object):
    """The OSD is a container for objects that can be rendered in 2D
    to overlay the 3D sceen.  To add objects:

        osd = OSD(window)
        osd.add_object(thingy)

    The OSD object's on_resize method should be pushed on the event
    stack for handling resize events:

        event.push_handlers('on_resize', osd.on_resize)

    """
    implements(imiru.IOSDRenderStage)
    context = None

    def __init__(self):
        self.objects = []
        self.clickable = []
        self.widgets = self.clickable

    def _set_2d(self, near, far):
        w = self.context.window
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glPushMatrix()
        gl.glLoadIdentity()
        gl.glOrtho(0, w.width, 0, w.height, near, far)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glPushMatrix()
        gl.glLoadIdentity()

    def _unset_2d(self):
        gl.glPopMatrix()
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glPopMatrix()
        gl.glMatrixMode(gl.GL_MODELVIEW)

    def render(self):
        """Draw contained objects.
        """
        if not self.objects:
            return

        r = 32
        self._set_2d(0, r*4)
        gl.glPushAttrib(gl.GL_ENABLE_BIT)
        gl.glEnable(gl.GL_BLEND)
        gl.glDisable(gl.GL_DEPTH_TEST)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        
        import miru.graphics

        for v in self.objects:
            v.draw()
            #print '-- %r' % v
            #print '\n'.join([ str(t) for t in miru.graphics.TextureTool.current_parameters()])
        gl.glColor4f(1,1,1,1)
        gl.glPopAttrib()
        self._unset_2d()



    def pop(self, index=-1):
        obj = self.objects.pop(index)
        if obj in self.clickable:
            self.clickable.remove(obj)
        return obj

    def __iter__(self):
        return iter(self.objects)

    def add_object(self, obj):
        self.objects.append(obj)
        if isinstance(obj, core.Object) and imiru.IDraggable.providedBy(obj.drawable):
            self.clickable.append(obj)

    def remove_object(self, obj):
        self.objects.remove(obj)
        if obj in self.clickable:
            self.clickable.remove(obj)


