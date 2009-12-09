
# Classes used throughout miru such as PositionalMixin
# and Object

import zope.interface as zi
from twisted.python import components

try:
    import euclid
except ImportError:
    euclid = _vector3

import pyglet.gl as gl
import pyglet.graphics


from miru import _vector3
from miru import imiru

###########################################################
# Some ugly plumbing to provide attribute-change-listening
# on PositionalMixin

def _getX(attr):
    a = '_%s' % attr
    def m(self):
        return getattr(self, a)
    return m

def _setX(attr):
    a = '_%s' % attr
    def m(self, value):
        if value is None:
            return
        if type(value) is tuple:
            value = euclid.Vector3(*value)

        constraints = getattr(self, '%s_constraints' % attr)
        for constr in constraints:
            value = constr.constrain(value)

        curr = getattr(self,a)
        if curr._last_value is not None:
            v = euclid.Vector3(*curr._last_value)
            if curr != v:
                setattr(self, a, _vector3.Vector3(
                        value[0], value[1], value[2],
                        parent=self, attr=a[1:]))
        else:
            v = getattr(self, a)
            setattr(self, a, _vector3.Vector3(
                value[0], value[1], value[2],
                parent=self, attr=a[1:]))
        listeners =  getattr(self, '%s_listeners' % attr)
        if v is not None:
            for f in listeners:
                f(self, value, value - v)
    return m

# end ugly plumbing
###########################################################

class PositionalMixin(object):
    """Positional object have pos and angle attributes
    which we can easily add listeners to do for immediate
    notification of changes.

    Example usage:

    >>> class Foo(PositionalMixin): pass
    ...
    >>> def myListener(object, pos, delta):
    ...    print 'Called:', tuple(pos), tuple(delta)
    ...
    >>> foo = Foo(pos_listeners=[myListener])
    >>> foo.pos = (1,1,1)
    Called: (1, 1, 1) (1, 1, 1)
    >>> foo.pos += (2,2,2)
    Called: (3, 3, 3) (2, 2, 2)
    """
    zi.implements(imiru.IPositional)

    def __init__(self, *p, **kw):
        for a in ('pos', 'angle', 'scale'):
            if kw.has_key(a):
                v = tuple(kw[a])
                setattr(self, '_%s' % a, _vector3.Vector3(v[0], v[1], v[2],
                    parent=self, attr=a))
            else:
                if a == 'scale':
                    setattr(self, '_%s' % a, _vector3.Vector3(
                        1,1,1, parent=self, attr=a))
                else:
                    setattr(self, '_%s' % a, _vector3.Vector3(
                        0,0,0, parent=self, attr=a))
        self.pos_listeners = kw.get('pos_listeners', [])
        self.angle_listeners = kw.get('angle_listeners', [])
        self.pos_constraints = kw.get('pos_constraints', [])
        self.angle_constraints = kw.get('angle_constraints', [])

        #experimental
        self.scale_listeners = kw.get('scale_listeners', [])
        self.scale_constraints = kw.get('scale_constraints', [])

    _getpos = _getX('pos')
    _setpos = _setX('pos')
    pos = property(_getpos, _setpos)

    _getangle = _getX('angle')
    _setangle = _setX('angle')
    angle = property(_getangle, _setangle)
    
    #experimental
    _getscale = _getX('scale')
    _setscale = _setX('scale')
    scale = property(_getscale, _setscale)


class Object(PositionalMixin):
    """
    >>> from zope.interface.verify import verifyObject, verifyClass
    >>> verifyClass(imiru.IPositional, Object)
    True
    >>> verifyObject(imiru.IPositional, Object())
    True
    """
    zi.implements(imiru.IObject)

    def __init__(self, drawable=None, **kw):
        self.drawable = drawable
        if self.drawable:
            self.drawable._wrapper = self
        # experimental part of this interface
        super(Object, self).__init__(self, **kw)
        self.render_stages = getattr(self.drawable,
                'render_stages',
                (imiru.IWorldRenderStage))

    def draw(self):
        if self.drawable is None:
            return
        if not getattr(self.drawable, 'skip_transform', False):
            self.transform_start()
            self.drawable.draw()
            self.transform_end()
        else:
            self.drawable.draw()

    def transform_start(self):
        angle = self.angle
        scale = self.scale
        gl.glPushMatrix()
        gl.glTranslatef(*tuple(self.pos))
        gl.glRotatef(angle.z, 0, 0, 1)
        gl.glRotatef(angle.y, 0, 1, 0)
        gl.glRotatef(angle.x, 1, 0, 0)
        
        #experimental
        gl.glScalef(*tuple(scale))

    def transform_end(self):
        gl.glPopMatrix()


    def in_render_stages(self, *render_stages):
        self.render_stages = tuple(render_stages)
        return self

    def __repr__(self):
        return '<miru.mesh.Object at %x %r>' % (id(self), self.drawable)


class ObjectGroup(pyglet.graphics.Group):

    def __init__(self, obj, parent=None):
        super(ObjectGroup, self).__init__(parent=parent)
        self.obj = obj
        self.set_state = self.obj.transform_start
        self.unset_state = self.obj.transform_end

_adptReg = []

@zi.implementer(imiru.ITranslationHandler)
def _worldobj_on_translate(control, target, x, y, dx, dy):

    from miru.context import context
    from miru import camera
    
    self = control


    if isinstance(context.camera, camera.MetaCamera):
        context.camera.focussed.render()

    viewport = (gl.GLint * 4)()
    mvmatrix = (gl.GLdouble * 16)()
    projmatrix = (gl.GLdouble * 16)()
    gl.glGetIntegerv(gl.GL_VIEWPORT, viewport)
    gl.glGetDoublev(gl.GL_MODELVIEW_MATRIX, mvmatrix)
    gl.glGetDoublev(gl.GL_PROJECTION_MATRIX, projmatrix)
    wx = gl.GLdouble()
    wy = gl.GLdouble()
    wz = gl.GLdouble()

    sz = gl.GLdouble()
    ex = target.pos.x
    ey = target.pos.y
    ez = target.pos.z
    gl.gluProject(ex, ey, ez, mvmatrix, projmatrix,
            viewport, wx, wy, sz)
    gl.gluUnProject(x, y, sz,
            mvmatrix, projmatrix, viewport, wx, wy, wz)

    if self.axis == self.AXIS_X:
        target.pos = (wx.value, wz.value, target.pos.z)
    elif self.axis == self.AXIS_Y:
        target.pos = (target.pos.x, wy.value, wz.value)
    elif self.axis == self.AXIS_Z:
        tz = dy * 0.01
        tz += (dx * 0.01)
        target.pos += (0, 0, tz)
    else:
        target.pos = (wx.value, wy.value, wz.value)

def _worldobj_on_translate_adpt(_context):
    return _worldobj_on_translate
_adptReg.append((_worldobj_on_translate_adpt, imiru.IObject, imiru.ITranslationHandler))

#def _object_on_translate_adpt(obj):
#    return imiru.ITranslationHandler(obj.drawable)
#_adptReg.append((_object_on_translate_adpt, imiru.IObject, imiru.ITranslationHandler))

@zi.implementer(imiru.IRotationHandler)
def _worldobj_on_rotate(control, target, x, y, dx, dy):
    self = control
    if self.axis == self.AXIS_Y:
        tx = dy * 0.35
        target.angle +=  (tx, 0, 0)
        target.angle.x %= 360.
    elif self.axis == self.AXIS_X:
        ty = dx * 0.35
        target.angle += (0, ty, 0)
        target.angle.y %= 360.
    elif self.axis == self.AXIS_Z:
        tz = (dy + dx) * 0.35
        target.angle += (0, 0, tz)
        target.angle.z %= 360.
    else:
        tx, ty = dx * 0.35, dy * 0.35
        target.angle += (ty, tx, 0)
        target.angle.x %= 360.
        target.angle.y %= 360.


def _worldobj_on_rotate_adpt(_context):
    return _worldobj_on_rotate

_adptReg.append((_worldobj_on_rotate_adpt, imiru.IObject, imiru.IRotationHandler))

def registerDeviceHandlers():
    for a in _adptReg:
        components.registerAdapter(*a)
# FIXME - this should NOT be default behavior
registerDeviceHandlers()

def unregisterDeviceHandlers():
    reg = components.getRegistry()
    for (adptFactory, origInterface, interfaceClasses) in _adptReg:
        reg.unregister([origInterface], interfaceClasses, '', adptFactory)

