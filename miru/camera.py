# -*- test-case-name: miru.test.test_camera -*-
# Copyright (c) 2008 Drew Smathers.
# See LICENSE for details
from pyglet import gl

from miru import imiru
from miru.utils import glvec
from miru import components
from miru import core
from miru import options

from euclid import Vector3
from UserList import UserList
import math

from zope.interface import implementer, implements
from twisted.python.components import registerAdapter

lightno = lambda i : eval('gl.GL_LIGHT%d' % i)

for LIGHT_CT_MAX in range(1000):
    try:
        lightno(LIGHT_CT_MAX)
    except Exception, e:
        #print 'Max lights count supported : ', LIGHT_CT_MAX
        break

def vlightno(n):
    off = n - LIGHT_CT_MAX
    return lightno(LIGHT_CT_MAX - 1) + off

def _constrain_lights(ct):
    assert ct <= LIGHT_CT_MAX,\
            'No more than %d lights can exist in a lightgroup' % LIGHT_CT_MAX
    if ct > 8:
        from warnings import warn
        warn("You're using more than 8 lights - this is not likely suppoted on other systems")


def _zcmp(o1, o2):
    return cmp(o1.pos.z, o2.pos.z)

class Camera(core.PositionalMixin):
    """Abstraction representing a camera - the viewer's perspective.
    The also acts a C{imiru.IRenderStage} for world objects which are drawn
    after the initial tranformation matrix is applied.

    @param wireframe: draw objects as wireframes (default: False)

    @type wireframe: C{bool}

    @param lights: Lighting for scene rendered by Camera

    @type lights: C{imiru.ILightGroup}

    @param projection: The C{imiru.IProjection} for the camera
        (default: C{PerspectiveProjection}.

    @param effects: List of optional effects

    @type effects: C{list}

    >>> from zope.interface.verify import verifyObject, verifyClass
    >>> verifyClass(imiru.IPositional, Camera)
    True
    >>> verifyObject(imiru.IPositional, Camera(light_group=None))
    True
    >>> verifyClass(imiru.ICamera, Camera)
    True
    >>> verifyObject(imiru.ICamera, Camera(light_group=None))
    True
    >>> verifyClass(imiru.IWorldRenderStage, Camera)
    True
    >>> verifyObject(imiru.IWorldRenderStage, Camera(light_group=None))
    True
    """
    implements(imiru.ICamera, imiru.IWorldRenderStage)
   
    ORBIT_MODE = 1
    ROTATE_MODE = 2
    rotation_mode = ORBIT_MODE
    track_target = None
    _render_idx = None

    def __init__(self, *p, **kw):
        self.wireframe = kw.get('wireframe', False)
        self.objects = self.visible = []
        self.lights = kw.get('lights', LightGroup())
        self.effects = kw.get('effects', [])
        self.window = kw.get('window', None)
        self.projection = kw.get('projection', PerspectiveProjection())
        self.depth_sort = kw.get('depth_sort', False)
        super(Camera, self).__init__(*p, **kw)

    def addobj(self, obj):
        """
        @deprecated - will become add_object
        """
        self.objects.append(obj)
        if self.depth_sort:
            self.objects.sort(_zcmp)
            if self._depth_sort not in obj.pos_listeners:
                obj.pos_listeners.append(self._depth_sort)

    add_object = addobj

    def delobj(self, obj):
        """
        @deprecated - will become remove_object
        """
        self.objects.remove(obj)
        if self.depth_sort:
            if self._depth_sort in obj.pos_listeners:
                obj.pos_listeners.remove(self._depth_sort)

    remove_object = delobj

    def _getprojection(self):
        return self._projection

    def _setprojection(self, proj):
        self._projection = proj
        self._projection.camera = self
        if self.window:
            self._projection.on_resize(
                    self.window.width,
                    self.window.height)
            return
        try:
            from miru.context import context
            if getattr(context, 'window', False):
                self._projection.on_resize(
                        context.window.width,
                        context.window.height)
        except ImportError:
            pass


    projection = property(_getprojection, _setprojection)

    def render(self, select_pass=0, visible=None, lights=None,
            effect_pass=0, before_render=None):

        if isinstance(self.projection, Viewport) and not select_pass:
            self.projection.enable()

        if not effect_pass or select_pass:
            for effect in self.effects:
                effect.enable()

        angle = self.angle

        if not select_pass:
            gl.glLoadIdentity()

        p = self.pos
        p = (-p.x, -p.y, -p.z)

        if self.track_target:
            t = self.track_target.pos
            up = (t - self.pos).normalized()
            eux = up.cross(Vector3(0,1,0))
            up = eux.cross(up)
            gl.gluLookAt(self.pos.x, self.pos.y, self.pos.z,
                    t.x, t.y, t.z, up.x, up.y, up.z)
        elif self.rotation_mode == Camera.ORBIT_MODE:
            if not select_pass:
                gl.glTranslatef(*p)
                gl.glRotatef(angle.z, 0, 0, 1)
                gl.glRotatef(angle.y, 0, 1, 0)
                gl.glRotatef(angle.x, 1, 0, 0)
        else:
            if not (select_pass or effect_pass):
                gl.glRotatef(angle.z, 0, 0, 1)
                gl.glRotatef(angle.y, 0, 1, 0)
                gl.glRotatef(angle.x, 1, 0, 0)
                gl.glTranslatef(*p)

        lights = (lights, self.lights)[lights is None]

        if not select_pass:
            if self.lights:
                lights.on()

        visible = visible or self.objects

        if not select_pass:
            if effect_pass:
                beforeRender = before_render or (lambda : None)
                beforeRender()
            for (idx,v) in enumerate(visible):
                self._render_idx = idx
                v.draw()
        else:
            for (idx,v) in enumerate([ v for v in visible if _translateable(v) ]):
                gl.glLoadName(idx)
                v.draw()

        if not select_pass and self.lights:
            lights.off()

        
        if not effect_pass or select_pass:
            for effect in self.effects:
                effect.disable()

        self._render_idx = None
    
    def _depth_sort(self, moved, pos, delta):
        if moved not in self.objects:
            # XXX this would be unusual?? hrmmm ... remove
            # from positional listeners?
            moved.pos_listeners.remove(self._check_zorder)
            return
        # This is uuuugly - but we want to avoid sorting potentially
        # large lists if we don't have to.
        # We do a custom sort in place as an optimization.
        if delta.z:
            idx = self.objects.index(moved)
            if idx:
                left = self.objects[idx-1]
                while pos.z < left.pos.z:
                    o = self.objects.pop(idx)
                    idx -= 1
                    self.objects.insert(idx, o)
                    if (idx - 1) < 0:
                        return
                    left = self.objects[idx - 1]
            if idx < len(self.objects) - 1:
                right = self.objects[idx+1]
                while pos.z > right.pos.z:
                    o = self.objects.pop(idx)
                    idx += 1
                    self.objects.insert(idx, o)
                    if (idx + 1) > len(self.objects) - 1:
                        return
                    right = self.objects[idx + 1]



    @property
    def nextObject(self):
        """The next object to render or None if the current is the
        last object to render or camera is not currently rendering.
        """
        if self._render_idx is None:
            return
        try:
            return self.objects[self._render_idx + 1]
        except IndexError:
            return

def _translateable(o):
    try:
        th = imiru.ITranslationHandler(o)
    except TypeError:
        return False
    return True


class BaseProjection(object):
    """
    >>> from zope.interface import verify
    >>> verify.verifyClass(imiru.IProjection, BaseProjection)
    True
    >>> verify.verifyObject(imiru.IProjection, BaseProjection())
    True
    """
    implements(imiru.IProjection)
    camera = None
    clear_color = (0.2, 0.2, 0.2, 1)

    def __init__(self, **kw):
        self.clear_color = kw.get('clear_color',
                BaseProjection.clear_color)

    def on_resize(self, width, height, x=0, y=0):
        raise NotImplementedError

    def _setLightsAndEffects(self):
        fNoLight = (4 * gl.GLfloat)()
        fNoLight[:] = [0,0,0,0]
        gl.glLightModelfv(gl.GL_LIGHT_MODEL_AMBIENT, fNoLight);
        gl.glClearColor(*self.clear_color)
        for effect in self.camera.effects:
            effect.enable()

class PerspectiveProjection(BaseProjection):

    def on_resize(self, width, height, x=0, y=0):
        gl.glViewport(x, y, width, height)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        height = height or 1
        gl.gluPerspective(45., width / float(height), 0.1, 1000.)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        self._setLightsAndEffects()


class OrthographicProjection(BaseProjection):

    def on_resize(self, width, height, x=0, y=0):
        gl.glViewport(x, y, width, height)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        h = height or 1
        w = width / float(h)
        gl.glOrtho(-w, w, -1, 1, -1, 1000.)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        self._setLightsAndEffects()


class DebugView:
    """
    >>> from zope.interface.verify import verifyClass, verifyObject
    >>> verifyClass(imiru.IDebuggingRenderStage, DebugView)
    True
    >>> verifyObject(imiru.IDebuggingRenderStage, DebugView())
    True
    """
    implements(imiru.IDebuggingRenderStage)

    def __init__(self, objects=None):
        self.objects = (objects, [])[objects is None]

    def render(self):
        for o in self.objects:
            o.draw()

    def addobj(self, obj):
        self.objects.append(obj)

    def delobj(self, obj):
        self.objects.remove(obj)

class BlittableView:
    """
    >>> from zope.interface.verify import verifyClass, verifyObject
    >>> verifyClass(imiru.IBlittableRenderStage, BlittableView)
    True
    >>> verifyObject(imiru.IBlittableRenderStage, BlittableView())
    True
    """
    implements(imiru.IBlittableRenderStage)

    def __init__(self):
        self.objects = []

    def _cmp(self, o1, o2):
        return cmp(o1.pos.z, o2.pos.z)

    def _check_zorder(self, moved, pos, delta):
        if moved not in self.objects:
            # XXX this would be unusual?? hrmmm ... remove
            # from positional listeners?
            moved.pos_listeners.remove(self._check_zorder)
            return
        # This is uuuugly - but we want to avoid sorting potentially
        # large lists if we don't have to.
        # We do a custom sort in place as an optimization.
        if delta.z:
            idx = self.objects.index(moved)
            if idx:
                left = self.objects[idx-1]
                while pos.z < left.pos.z:
                    o = self.objects.pop(idx)
                    idx -= 1
                    self.objects.insert(idx, o)
                    if (idx - 1) < 0:
                        return
                    left = self.objects[idx - 1]
            if idx < len(self.objects) - 1:
                right = self.objects[idx+1]
                while pos.z > right.pos.z:
                    o = self.objects.pop(idx)
                    idx += 1
                    self.objects.insert(idx, o)
                    if (idx + 1) > len(self.objects) - 1:
                        return
                    right = self.objects[idx + 1]

    def render(self):
        gl.glPushAttrib(gl.GL_ENABLE_BIT)
        gl.glEnable(gl.GL_BLEND)
        gl.glDisable(gl.GL_DEPTH_TEST)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

        gl.glEnable(gl.GL_TEXTURE_2D)
        gl.glPushClientAttrib(gl.GL_CLIENT_VERTEX_ARRAY_BIT)

        for o in self.objects:
            o.draw()

        gl.glPopClientAttrib()
        gl.glPopAttrib()
    
    def addobj(self, o):
        self.objects.append(o)
        if self._check_zorder not in o.pos_listeners:
            o.pos_listeners.append(self._check_zorder)
        self.objects.sort(self._cmp)


    def delobj(self, o):
        if self._check_zorder in o.pos_listeners:
            o.pos_listeners.remove(self._check_zorder)
        self.objects.remove(o)

_debugView = DebugView()
components.registerUtility(imiru.IDebuggingRenderStage, _debugView)
_blittableView = BlittableView()
components.registerUtility(imiru.IBlittableRenderStage, _blittableView)

class LightMixin(object):

    light_no = gl.GL_LIGHT0

    def __init__(self, *p, **kw):
        #self.pos = kw.get('pos', (0.5,0.5,1.0))
        #self.angle = Vector3(0.0, 0.0, 0.0)  # XXX setting the angle has no effect
        self.ambient = kw.get('ambient', (0.5,0.5,0.5,1))
        self.specular = kw.get('specular', (0.9,0.9,0.9,1))
        self.diffuse = kw.get('diffuse', (1,1,1,1))
        super(LightMixin, self).__init__(*p, **kw)

    def _getspecular(self):
        # TODO
        # get value from gl.GL vector - maximize space
        return self._specular

    def _setspecular(self, specular):
        self._specular = specular
        self.lspec = glvec(*specular)

    def _getdiffuse(self):
        return self._diffuse

    def _setdiffuse(self, diffuse):
        self._diffuse = diffuse
        self.ldifs = glvec(*diffuse)
    
    def _getambient(self):
        return self._ambient

    def _setambient(self, ambient):
        self._ambient = ambient
        self.lambient = glvec(*ambient)

    specular = property(_getspecular, _setspecular)
    diffuse = property(_getdiffuse, _setdiffuse)
    ambient = property(_getambient, _setambient)
    

def _update_light_pos(self, pos, _delta):
    self._pos = pos
    self.lpos = glvec(*(tuple(pos) + (self.W,)))

class DirectionalLight(LightMixin, core.PositionalMixin):

    W = 0.0

    def __init__(self, *p, **kw):
        # change default for pos
        if not kw.has_key('pos'):
            kw['pos'] = (0.5,0.5,1.0)
        super(DirectionalLight, self).__init__(*p, **kw)
        self.pos_listeners.append(_update_light_pos)
        _update_light_pos(self, self.pos, None)

    def on(self):

        lno = self.light_no
        gl.glEnable(lno)

        # Define a simple function to create ctypes arrays of floats:

        gl.glLightfv(lno, gl.GL_POSITION, self.lpos)
        gl.glLightfv(lno, gl.GL_SPECULAR, self.lspec)
        gl.glLightfv(lno, gl.GL_DIFFUSE, self.ldifs)
        gl.glLightfv(lno, gl.GL_AMBIENT, self.lambient)

    def clone(self):
        return DirectionalLight(ambient=tuple(self.ambient),
                specular=tuple(self.specular),
                diffuse=self.diffuse,
                pos=tuple(self.pos),
                angle=tuple(self.angle))


class PositionalLight(LightMixin, core.PositionalMixin):
    """A positinal light's pos is the actual position in 3D space coords.
    The attenuation can be adjusted via the three properties kc, kl and kq
    which are constant, linear and quadratic parts.

    Additionaly, a positional light can be turned into a spotlight by
    specifying a spot_cutoff with value in the range [0,90].  By default
    the spot_cutoff is the special value 180 and behaves as a normal
    positional light source.  Other parameters related to spot lights
    (spot_dir, spot_exponent and track_target) will have no effect if
    spot_cutoff is set to 180.

    Related formula:

    attenuation = 1 / (k_c + k_l*d + k_q*d^2)

    k_c = gl.GL_CONSTANT_ATTENUATION
    k_l = gl.GL_LINEAR_ATTENUATION
    k_q = gl.GL_QUADRATIC_ATTENUATION

    @param kc: constant attenuation

    @param kl: linear attenuation

    @param kq: quadratic attenuation

    @param spot_cutoff: spot cut off in range [0,90] or 180 for all directions

    @param spot_exponent: the spot exponent in range [0,128]

    @param spot_dir: the spot direction (unit vector)

    @param track_target: positional object the spot light should track

    """

    W = 1.0

    _debug = False
    _debugGlobe = None
    _debugTrack = None

    def __init__(self, *p, **kw):
        self.kc = kw.get('kc', 0.0)
        self.kl = kw.get('kl', 0.0)
        if not self.kc and not self.kl:
            self.kq = kw.get('kq', 0.5)
        else:
            self.kq = kw.get('kq', 0.0)
        self.spot_cutoff = kw.get('spot_cutoff', 180.0)
        self.spot_dir = kw.get('spot_dir', (0.0,0.0,-1.0))
        self.spot_exponent = float(kw.get('spot_exponent', 3))
        self.track_target = kw.get('track_target', None)
        # change default for pos
        if not kw.has_key('pos'):
            kw['pos'] = (0.5,1.0,1.0)
        super(PositionalLight, self).__init__(*p, **kw)
        self.pos_listeners.append(_update_light_pos)
        _update_light_pos(self, self.pos, None)
        if options['debug_view'] or kw.get('debug'):
            self.debug = True

    def on(self):

        lno = self.light_no
        gl.glEnable(lno)

        gl.glLightf(lno, gl.GL_CONSTANT_ATTENUATION, self.kc)
        gl.glLightf(lno, gl.GL_LINEAR_ATTENUATION, self.kl)
        gl.glLightf(lno, gl.GL_QUADRATIC_ATTENUATION, self.kq)

        if self.is_spot:
            if self.track_target:
                self._track()
            gl.glLightf(lno, gl.GL_SPOT_CUTOFF, self._spot_cutoff)
            gl.glLightfv(lno, gl.GL_SPOT_DIRECTION, self.lspot_dir)
            gl.glLightfv(lno, gl.GL_SPOT_EXPONENT, self.spot_exponent)

        gl.glLightfv(lno, gl.GL_POSITION, self.lpos)
        gl.glLightfv(lno, gl.GL_SPECULAR, self.lspec)
        gl.glLightfv(lno, gl.GL_DIFFUSE, self.ldifs)
        gl.glLightfv(lno, gl.GL_AMBIENT, self.lambient)

    def _track(self):
        v = (self.track_target.pos - self._pos).normalize()
        self.spot_dir = v

    def _getspotcutoff(self):
        return self._spot_cutoff

    def _setspotcutoff(self, angle):
        assert angle == 180.0 or (angle >= 0.0 and angle <= 90.0)
        self.is_spot = (angle != 180.0)
        self._spot_cutoff = angle

    def _getspotdir(self):
        return self._spot_dir

    def _setspotdir(self, direction):
        self._spot_dir = Vector3(*direction)
        self.lspot_dir = glvec(*direction)

    def _getspotexponent(self):
        return self._spot_exponent

    def _setspotexponent(self, exp):
        self._spot_exponent = (1 * gl.GLfloat)()
        self._spot_exponent[:] = [exp]

    spot_cutoff = property(_getspotcutoff, _setspotcutoff)
    spot_dir = property(_getspotdir, _setspotdir)
    spot_exponent = property(_getspotexponent, _setspotexponent)


    def clone(self):
        return PositionalLight(
                pos=tuple(self.pos),
                angle=tuple(self.angle),
                diffuse=tuple(self.diffuse),
                ambient=tuple(self.ambient),
                kc=self.kc, kl=self.kl, kq=self.kq,
                spot_cutoff=self.spot_cutoff,
                spot_exponent=self.spot_exponent[0],
                spot_dir=tuple(self.spot_dir))


class LightGroup(UserList):
    """Known issue:

    On slicing the light group list a sublist of copies (vs. same instances)
    is returned.  Current workaround is to only get instances via indexing
    into the light group.

    @param lights: List of lights to add to the group
    """

    def __init__(self, lights=None, enforce_limit=True):
        UserList.__init__(self)
        self.enforce_limit = enforce_limit
        self.extend(lights or [])
        

    def on(self):
        gl.glPushMatrix()
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glPushAttrib(gl.GL_LIGHTING_BIT)
        gl.glEnable(gl.GL_LIGHTING)
        for l in self:
            l.on()
    
    def off(self):
        gl.glPopAttrib()
        #gl.glDisable(gl.GL_DEPTH_TEST)
        gl.glPopMatrix()

    def append(self, light):
        if self.enforce_limit:
            _constrain_lights(len(self) + 1)
            light.light_no = lightno(len(self))
        else:
            light.light_no = vlightno(len(self))
        UserList.append(self, light)

    def extend(self, lights):
        if self.enforce_limit:
            _constrain_lights(len(self) + len(lights))
        lts = []
        for i, l in enumerate(lights):
            if self.enforce_limit:
                l.light_no = lightno(len(self) + i)
            else:
                l.light_no = vlightno(len(self) + i)
            lts.append(l)
        UserList.extend(self, lts)


def _camera_on_translate(control, target, x, y, dx, dy):
    self = control

    # XXX for backwards compat
    if hasattr(self, 'camera_move_factor'):
        f = self.camera_move_factor
    else:
        f = self.sensitivity

    if self.axis == self.AXIS_X:
        target.pos += (f * dx, 0, 0)
    elif self.axis == self.AXIS_Y:
        target.pos += (0, f * dy, 0)
    elif self.axis == self.AXIS_Z:
        d = math.sqrt(dx**2 + dy**2)
        d *= (3,-3)[dy < 0]
        target.pos += (0, 0, f * d)
    else:
        target.pos += (f * dx, f * dy, 0)

@implementer(imiru.ITranslationHandler)
def _camera_on_translate_adpt(_context):
    return _camera_on_translate

registerAdapter(_camera_on_translate_adpt, imiru.ICamera, imiru.ITranslationHandler)

@implementer(imiru.IRotationHandler)
def _camera_on_rotate_adpt(_context):
    return core._worldobj_on_rotate

registerAdapter(_camera_on_rotate_adpt, imiru.ICamera, imiru.IRotationHandler)


###############
# Experimental 

def _setFocussed(m):
    def _m(self, *p, **kw):

        #from miru.environment import env
        from miru.context import context
        from miru import input
        #from miru import controls

        x,y = input.mouseXY()

        for c in self.cameras:
            vp = c.projection

            bl_x = vp.bl[0] * context.window.width
            bl_y = vp.bl[1] * context.window.height
            tr_x = vp.tr[0] * context.window.width
            tr_y = vp.tr[1] * context.window.height

            if (x >= bl_x and x <= tr_x) and (y >= bl_y and y <= tr_y):
                self._focussed = c
                break
        else:
            self._focussed = self.cameras[0]
        return m(self, *p, **kw)
    _m.__name__ = m.__name__
    return _m

class MetaCamera(object):
    implements(imiru.ICamera, imiru.IWorldRenderStage)

    # These default to None so that projection and
    # lights can be customized on child cameras.
    _projection = None
    _lights = None
    _debug_lines = None

    effects = []

    def __init__(self, *cameras):
        from warnings import warn
        warn('MetaCamera is experimental - expect things to break')
        self.cameras = cameras
        self._focussed = self.cameras[0]
        self._resetProjection = PerspectiveProjection()
        self._resetProjection.camera = self

    def render(self, *p, **kw):
        #from miru.environment import env
        from miru.context import context
        for c in self.cameras:
            c.render(*p, **kw)
        self._resetProjection.on_resize(
                context.window.width, context.window.height)


    @property
    def projection(self):
        return _MetaProjection(self, [c.projection for c in self.cameras])


    def _getlights(self):
        return self.cameras[0].lights

    def _setlights(self, lights):
        for c in self.cameras:
            c.lights = lights
        self._lights = lights

    lights = property(_getlights, _setlights)


    @_setFocussed
    def _getangle(self):
        return self._focussed.angle
    
    @_setFocussed
    def _setangle(self, angle):
        self._focussed.angle = angle

    angle = property(_getangle, _setangle)

    @_setFocussed
    def _getpos(self):
        return self._focussed.pos

    @_setFocussed
    def _setpos(self, pos):
        self._focussed.pos = pos

    pos = property(_getpos, _setpos)

    @property
    @_setFocussed
    def objects(self):
        return self._focussed.objects


    @property
    @_setFocussed
    def focussed(self):
        return self._focussed

    # FIXME

    def add_object(self, obj):
        self.cameras[0].addobj(obj)

    def remove_object(self, obj):
        self.cameras[0].delobj(obj)


    def _getdebug(self):
        return self._debug

    def _setdebug(self, debug):
        from miru.context import context
        self._debug = debug
        if debug:
            if not self._debug_lines:
                self._debug_lines = core.Object(ViewportOutline(self))
            context.add_object(self._debug_lines)
        else:
            context.remove_object(self._debug_lines)

    debug = property(_getdebug, _setdebug)


class _MetaProjection(BaseProjection):

    def __init__(self, camera, projections):
        self.camera = camera
        self.projections = projections

    def on_resize(self, width, height, x=0, y=0):
        for p in self.projections:
            p.on_resize(width, height)


class Viewport(BaseProjection):
    """GL viewport. bl and tr are bottom-left and top-right coordinates
    of the viewports.  (0,0) is given for the left and bottom and (1,1)
    for the top and right of the window.

    @param bl: bottom-left of the viewport

    @param tr: top-right of the viewport
    """

    def __init__(self, bl=(0.,0.), tr=(1.,1.), contextProjection=None):
        self.contextProjection = contextProjection or PerspectiveProjection()
        self.bl = bl
        self.tr = tr
        self.window = 0
        self.height = 0
        self.x = 0
        self.y = 0
        self.viewport_on = True

    def on_resize(self, width, height, x=None, y=None):
        
        self.height = int((self.tr[1] - self.bl[1]) * height)
        self.width = int((self.tr[0] - self.bl[0]) * width)
        self.x = int(self.bl[0] * width)
        self.y = int(self.bl[1] * height)
        self.contextProjection.on_resize(self.width, self.height,
                self.x, self.y)


    def enable(self):
        if self.viewport_on:
            self.contextProjection.on_resize(self.width, self.height,
                self.x, self.y)

    def _getcamera(self):
        return self.contextProjection.camera

    def _setcamera(self, camera):
        self.contextProjection.camera = camera

    camera = property(_getcamera, _setcamera)


class ViewportOutline(object):

    implements(imiru.IDrawable)
    renderStages = (imiru.IOSDRenderStage,)

    def __init__(self, metaCamera, color=(0.2,0,0,1)):
        self.metaCamera = metaCamera
        self.color = color

    def draw(self):
        from miru.context import context
        gl.glEnable(gl.GL_LINE_STIPPLE)
        gl.glLineStipple(1, 0x51315)
        gl.glColor4f(*self.color)
        for c in self.metaCamera.cameras:

            vp = c.projection

            x = vp.x == 0 and 1 or vp.x
            width = vp.x == 0 and vp.width - 1 or vp.width
            width = (vp.x + vp.width) >= context.window.width and width - 1 or width

            y = vp.y == 0 and 1 or vp.y
            height = vp.y == 0 and vp.height - 1 or vp.height
            height = (vp.y + vp.height) >= context.window.height and height - 1 or height

            gl.glBegin(gl.GL_LINE_LOOP)
            gl.glVertex2f(x, y)
            gl.glVertex2f(x, y + height)
            gl.glVertex2f(x + width, y + height)
            gl.glVertex2f(x + width, y)
            gl.glEnd()
        gl.glDisable(gl.GL_LINE_LOOP)
        gl.glColor4f(1,1,1,1)

