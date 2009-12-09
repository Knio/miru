from pyglet import options
options['debug_gl'] = 0

import pyglet.gl as gl
import pyglet.graphics

import miru.graphics
import miru.ui
import miru.core
import miru.input
import miru.ext.geom

from miru.context import context

window = miru.ui.BaseWindow(600,400, clear_color=(0.3,0,0.3,1))
context.window = window
context.control = miru.input.SimpleMouseControl()
context.camera.lights = miru.camera.LightGroup([
    miru.camera.PositionalLight(pos=(0,0,1)),
    miru.camera.PositionalLight(pos=(0,1,0)),
    miru.camera.PositionalLight(pos=(1,0,0))])
context.camera.pos = (0,0,10)

box = miru.ext.geom.Box()
batch = pyglet.graphics.Batch()
miru.ext.geom.get_vlist(box, batch)
greygroup = miru.graphics.ColorGroup(0.5)

obj = miru.core.Object(batch)
context.add_object(obj)

gl.glEnable( gl.GL_CULL_FACE )

while not window.has_exit:
    window.clear()
    pyglet.clock.tick()
    window.dispatch_events()
    context.render()
    window.flip()


