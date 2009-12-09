# TODO - this will replace miru.environment

import miru.camera
from miru import osd2

_contexts = {}

class Context(object):

    _window = None
    _control = None

    def __init__(self, camera, osd=None, cameras=None,
            render_stages=None):
        self.camera = camera
        self.cameras = cameras
        if cameras is None:
            self.cameras = {}
        self.osd = osd
        self.objects = []
        if not self.cameras:
            self.cameras['main'] = camera
        # FIXME
        self.render_stages = render_stages or [ camera ]
        if osd and not render_stages:
            self.render_stages = [ camera, osd ]

    def render(self):
        for stage in self.render_stages:
            stage.render()

    def add_object(self, obj, render_stage=None):
        #if obj.on_add():
        #    self.objects.append(obj)
        # XXX
        self.objects.append(obj)
        if not render_stage:
            self.camera.add_object(obj)
        else:
            render_stage.add_object(obj)

    def remove_object(self, obj, render_stage=None):
         #obj.on_remove()
         if not render_stage:
            self.camera.remove_object(obj)
         else:
            render_stage.remove_object(obj)
         self.objects.remove(obj)

    def _get_window(self):
        return self._window

    def _set_window(self, window):
        self._window = window
        if self.control:
            self.control.enable()

    window = property(_get_window, _set_window)

    def _get_osd(self):
        return self._osd

    def _set_osd(self, osd):
        self._osd = osd
        if osd is not None:
            osd.context = self

    osd = property(_get_osd, _set_osd)


    def _get_control(self):
        return self._control

    def _set_control(self, control):
        self._control = control
        control.context = self
        control.enable()

    control = property(_get_control, _set_control)

def register_context(key, context):
    if _contexts.has_key(key):
        raise ContextException,\
                'context `%s\' already registered.'\
                ' You must unregister with delete_context() first.'
    _contexts[key] = context

def delete_context(key):
    ctx = _contexts[key]
    # FIXME - clean up vertex lists, etc.
    del _contexts[key]

def get_context(key):
    return _contexts[key]

context = Context(
        miru.camera.Camera( pos=(0,0,4),
            lights=miru.camera.LightGroup([
                miru.camera.PositionalLight(),
                miru.camera.DirectionalLight()
                ])),
        osd=osd2.OSD()
        )
register_context('main', context)

