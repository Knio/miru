from pyglet import options
options['debug_gl'] = 0
#options['debug_gl_trace'] = 1
#options['debug_gl_trace_args'] = 1
options['vsync'] = 0

import pyglet.graphics
import pyglet.clock

import miru
from miru.context import context
from miru.ext import geom

window = miru.ui.Window(600,400)
context.window = window
context.osd.add_object(pyglet.clock.ClockDisplay())
context.control = miru.input.SimpleMouseControl()
context.camera.lights = miru.camera.LightGroup([
    miru.camera.DirectionalLight()])
context.camera.pos.z = 5
context.camera.angle.x = -15

batch = pyglet.graphics.Batch()
group = miru.graphics.ColorGroup(0.2)

torus = geom.Torus(divisions=75)
#torus.get_vlist(batch, group)
vlist = geom.get_vlist(torus, batch, group)
torus_obj = miru.core.Object(batch)
torus_obj.angle.z = 15
context.add_object(torus_obj)

v = 35
def update(dt):
    dy = dt * v
    torus_obj.angle.x += dy
pyglet.clock.schedule_interval(update, 1/60.)

while not window.has_exit:
    window.clear()
    pyglet.clock.tick()
    window.dispatch_events()
    context.render()
    window.flip()

