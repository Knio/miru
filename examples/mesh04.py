from pyglet import options
options['debug_gl'] = False
options['debug_gl_trace'] = True
options['debug_gl_trace_args'] = True
options['vsync'] = False

from pyglet.gl import *

import miru.ui
from miru.context import context
import miru.graphics
import miru.input
from miru import core

import pyglet.graphics
import pyglet.image
from pyglet import clock

import os, sys, random

window = miru.ui.TestWindow(600, 400)

context.window = window
context.camera.pos.z = 20
context.control = miru.input.SimpleMouseControl()
context.osd.add_object(clock.ClockDisplay())

# Create mesh object and add to batch
mesh_id = miru.graphics.load_mesh(
        (sys.argv[1:] and sys.argv[1]
            or os.path.join('docs', 'demo', 'alien.obj')))
batch = pyglet.graphics.Batch()
img = pyglet.image.load(
        os.path.join('docs', 'demo', 'orange.png'))
tex = miru.graphics.get_wrapped_texture(img)
tex_group = miru.graphics.TextureTransformGroup(texture=tex,
        translation=[0,0,0], rotation=[0,0,0])

miru.graphics.batch_mesh(
        mesh_id, batch, tex_group, False)

for i in range(35):
    x = -7.5 + random.random() * 15
    y = -7.5 + random.random() * 15
    z = -7.5 + random.random() * 15
    next_id = miru.graphics.mesh_transform(mesh_id, translation=(x,y,z))
    miru.graphics.batch_mesh(next_id, batch, tex_group, False)

velocity = 0.1
def update(dt):
    delta = dt * velocity
    tex_group.translation[0] += delta
clock.schedule_interval(update, 1/60.)


obj = core.Object(batch)
context.add_object(obj)

while not window.has_exit:
    clock.tick()
    window.clear()
    window.dispatch_events()
    context.render()
    window.flip()
window.close()




