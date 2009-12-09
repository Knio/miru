from pyglet import options
options['debug_gl'] = False
options['graphics_vbo'] = True

import miru.graphics
import miru.ui
import miru.utils
import miru.input
from miru.context import context

import pyglet.gl as gl
from pyglet import clock
import pyglet.graphics

import sys
import time
import random

gl.glEnable( gl.GL_CULL_FACE )

USAGE = 'static'

window = miru.ui.TestWindow(680, 400, clear_color=(0,0.5,0,1))
window.set_vsync(0)

batch = pyglet.graphics.Batch()
obj = miru.graphics.Object(batch)
mat_group = miru.graphics.ColorMaterialGroup()

ct = sys.argv[1:] and int(sys.argv[1]) or 5000
if sys.argv[2:]:
    USAGE = sys.argv[2].lower()
print 'vertex usage', USAGE
before = time.time()
for i in xrange(ct):
    (blx, bly) = (-2.5 + random.random() * 5, -1.5  + random.random() * 3)
    width = 0.1 + random.random() * 0.5
    r = random.random()
    color = [r,r,r,random.random()]#r,r]#,random.random()]
    z = -10 + (i / float(ct)) * 20
    quad = batch.add(4, gl.GL_QUADS, mat_group, 'v3f/%s' % USAGE, 'c4f/%s' % USAGE)
    quad.vertices[:] = [
                blx, bly, z,
                blx, bly + width, z,
                blx + width, bly + width, z,
                blx + width, bly, z
                ]
    quad.colors[:] = color * 4
elapsed = time.time() - before
print 'loaded : %4.4fs' % elapsed

context.window = window
context.control = miru.input.SimpleMouseControl()
context.add_object(obj)
context.osd.add_object(clock.ClockDisplay())

context.camera.pos.z = 15

def on_draw():
    window.clear()
    context.render()

av = 15
def update(dt):
    dy = av * dt
    context.camera.angle.y += dy
clock.schedule_interval(update, 1/1000.)


while not window.has_exit:
    window.clear()
    dt = clock.tick()
    window.dispatch_events()
    on_draw()
    window.flip()



