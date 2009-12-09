# -*- test-case-name: miru.test.test_track -*-
# Copyright (c) 2008 Drew Smathers.
# See LICENSE for details

from pyglet import gl

from miru.camera import Camera, MetaCamera
from miru.imiru import ITrack
from miru import math3d

from zope.interface import implements

_tracked_reg = {}
_tracker_reg = {}
_tracker_tracked_reg = {}



def gettracks(tracker=None, tracked=None, track=None):
    if tracker:
        p = 0
    elif tracked:
        p = 1
    else:
        p = 2
    if p < 2: track = (0,0)
    key = (id(tracker), id(tracked), (id(track[0]), id(track[1])))[p]
    reg = (_tracker_reg, _tracked_reg, _tracker_tracked_reg)[p]
    return reg.get(key, [])

def deactivate(tracker=None, tracked=None):
    p = tracked is not None
    key = (id(tracker), id(tracked))[p]
    reg = (_tracker_reg, _tracked_reg)[p]
    if reg.has_key(key):
        for track in reg[key]:
            track.untrack()
            if _tracker_tracked_reg.has_key((id(track.tracker), id(track.tracked))):
                del _tracker_tracked_reg[(id(track.tracker), id(track.tracked))]
        del reg[key]

class Track(object):
    implements(ITrack)

    _bidir = None
    _called = False

    def __init__(self, tracker, tracked):
        self.tracker = tracker
        self.tracked = tracked
        l = _tracker_reg.setdefault(id(tracker), [])
        l.append(self)
        l = _tracked_reg.setdefault(id(tracked), [])
        l.append(self)
        l = _tracker_tracked_reg.setdefault((id(tracker),id(tracked)), [])
        l.append(self)
        
        try:
            self._bidir = gettracks(track=(tracked, tracker))[0]
            self._bidir._bidir = self
        except IndexError:
            pass
        

    def _alreadyCalled(self):
        if not self._bidir:
            return False
        if self._bidir._called:
            self._bidir._called = False
            return True
        self._called = True
        return False

    def deactivate(self):
        while self in self.tracked.pos_listeners:
            self.tracked.pos_listeners.remove(self)
        while self in self.tracked.angle_listeners:
            self.tracked.angle_listeners.remove(self)

    # Deprecated - this will go away in future version
    untrack = deactivate

class PosTrack(Track):
    """
    >>> from zope.interface.verify import verifyClass, verifyObject
    >>> verifyClass(ITrack, PosTrack)
    True
    """

    def __init__(self, tracker, tracked, axes=(1,1,1)):
        self.axes = axes
        super(PosTrack, self).__init__(tracker, tracked)
        self.tracked.pos_listeners.append(self)
        
    def __call__(self, obj, pos, delta):
        if self._alreadyCalled():
            return
        self.tracker.pos += (delta.x * self.axes[0],
                delta.y * self.axes[1],
                delta.z * self.axes[2])
    


class SSCameraTrack(Track):
    """Side-Scroller Camera Track.  Track an object until it reaches the edge of 
    the screen.  The edge point is defined as a percentage of the screen's width
    and height given as a number in the range [0,0.5].

    Assumption - view vector is parallel with the z-axis of the worldi.

    @param camera: the tracker Camera

    @type  camera: C{miru.camera.Camera}

    @param tracked: the object tracked by the camera

    @type  tracked: C{miru.core.PositionalMixin}

    @param window: view window

    @type  window: C{pyglet.window.Window}

    @param zminmax: optional (minimum, maximum) distance (delta z) between tracker and 
                    tracked

    @type  zminmax: C{tuple}

    @param edge: the edge factor in range [0,0.5] (default 0.2)

    @type  edge: C{float}

    >>> from zope.interface.verify import verifyClass, verifyObject
    >>> verifyClass(ITrack, SSCameraTrack)
    True
    """

    def __init__(self, camera, tracked, window, zminmax=None, edge=0.2):
        assert isinstance(camera, Camera)
        self.edge = edge
        self.window = window
        self.zminmax = zminmax
        super(SSCameraTrack, self).__init__(camera, tracked)
        self.tracked.pos_listeners.append(self)


    def __call__(self, obj, pos, delta):
        if self._alreadyCalled():
            return

        """
        # Project world coords to screen
        viewport = (gl.GLint * 4)()
        mvmatrix = (gl.GLdouble * 16)()
        projmatrix = (gl.GLdouble * 16)()
        gl.glGetIntegerv(gl.GL_VIEWPORT, viewport)
        gl.glGetDoublev(gl.GL_MODELVIEW_MATRIX, mvmatrix)
        gl.glGetDoublev(gl.GL_PROJECTION_MATRIX, projmatrix)
        wx = gl.GLdouble()
        wy = gl.GLdouble()
        wz = gl.GLdouble()
        gl.gluProject(pos.x, pos.y, pos.z, mvmatrix, projmatrix, viewport, wx, wy, wz)

        wx = wx.value
        wy = wy.value
        wz = wz.value
        """
        from miru.context import context
        if isinstance(context.camera, MetaCamera):
            self.tracker.render()

        wx, wy = math3d.projectXY(obj)

        w = self.window.width
        edge = w * self.edge
        if wx < edge or wx > (w - edge):
            self.tracker.pos += (delta.x,0,0)

        h = self.window.height
        edge = h * self.edge
        if wy < edge or wy > (h - edge):
            self.tracker.pos += (0,delta.y,0)

        if self.zminmax:
            zdelta = abs(pos.z - self.tracker.pos.z)
            if zdelta >= self.zminmax[1]:
                self.tracker.pos += (0,0,delta.z)
            elif zdelta <= self.zminmax[0]:
                self.tracker.pos += (0,0,delta.z)

