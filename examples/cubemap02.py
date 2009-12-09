from pyglet import options
options['debug_gl'] = False
#options['debug_gl_trace'] = True
#options['debug_gl_trace_args'] = True
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
context.camera.pos.z = 7
context.control = miru.input.SimpleMouseControl()
context.osd.add_object(clock.ClockDisplay())

glEnable( GL_DEPTH_TEST )

cubemap = miru.graphics.Cubemap([
    os.path.join('docs', 'demo', 'cm-%s.png' % sfx) for sfx in (
        'left', 'forward', 'up', 'down', 'right', 'back'
        )
    ])

mesh_id = miru.graphics.load_mesh(
        (sys.argv[1:] and sys.argv[1]
            or os.path.join('docs', 'demo', 'yam.obj')))

batch = pyglet.graphics.Batch()
miru.graphics.batch_mesh(
        mesh_id, batch, cubemap.texture_group_b, False)
obj = core.Object(batch)
context.add_object(obj)

velocity = 20
def update(dt):
    delta = dt * velocity
    obj.angle.y += delta
clock.schedule_interval(update, 1/60.)

while not window.has_exit:
    clock.tick()
    window.clear()
    window.dispatch_events()
    context.render()
    window.flip()
window.close()




