# Copyright (c) 2008 Drew Smathers.
# See LICENSE for details
from pyglet import window
from pyglet import image
from pyglet.window import key
from pyglet import gl

from miru.context import context
from miru import graphics

import random
import os

from itertools import cycle

RANDOM_BENCHMARK = True
_bmark_choices = [ 'alien' ]

_configs = [
    gl.Config(double_buffer=True, depth_size=24,
           sample_buffers=1, samples=4),
    gl.Config(double_buffer=True, depth_size=24,
           sample_buffers=1, samples=2),
    gl.Config(double_buffer=True, depth_size=24),
    gl.Config(double_buffer=True, depth_size=16),
]

class Window(window.Window):

    def __init__(self, *p, **kw):
        clear_color = kw.pop('clear_color', False)
        if clear_color:
            self.clear_color = clear_color
        #self.effects = safepop(kw, 'effects', [])
        for config in _configs:
            try:
                kw['config'] = config
                super(BaseWindow, self).__init__(*p, **kw)
                break
            except:
                pass
        # FIXME - use pkg_resource ...
        try:
            img = image.load(os.path.join(
                os.path.dirname(__file__), 'data', 'icon.png'))
            self.set_icon(img)
        except:
            pass

    def on_resize(self, w, h):
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glEnable( gl.GL_BLEND )
        gl.glEnable( gl.GL_MULTISAMPLE )
        gl.glEnable( gl.GL_DEPTH_TEST )
        context.camera.projection.on_resize(w, h)

    def _getclear_color(self):
        return context.camera.projection.clear_color

    def _setclear_color(self, clear_color):
        context.camera.projection.clear_color = clear_color

    clear_color = property(_getclear_color, _setclear_color)

BaseWindow = Window


class TestWindow(BaseWindow):
    """Used for miru functional test suite.
    """

    def __init__(self, *p, **kw):
        if not kw.has_key('resizable'):
            kw['resizable'] = True
        super(TestWindow, self).__init__(*p, **kw)

    def _load_object(self):
        if RANDOM_BENCHMARK:
            fname = 'docs/demo/%s.obj' % random.choice(_bmark_choices)
            o = graphics.load_wobj(fname)
            print 'loaded [random]', o
        else:
            o = graphics.load_wobj('docs/demo/alien.obj')
            print 'loaded', o
        context.add_object(o)
        return o

    bkey = _load_object

    def on_key_press(self, pressed, modifiers):
        self._key_pressed = pressed
        self._modifiers = modifiers
        if pressed == key.ESCAPE:
            self.has_exit = True
        elif pressed == key.B:
            self.bkey()
        elif pressed == key.F:
            print '__MIRU_FTEST__RESULT__ : FAILED'


