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
context.camera.rotation_mode = context.camera.ROTATE_MODE
context.camera.pos = (0,0,7)
context.control = miru.input.MouseControl()
#context.osd.add_object(clock.ClockDisplay())

cubemap = miru.graphics.Cubemap([
    os.path.join('docs', 'demo', 'cm-%s.png' % sfx) for sfx in (
        'left', 'forward', 'up', 'down', 'right', 'back'
        )
    ])
#reflection_group = miru.graphics.ReflectionMapGroup()

# Create mesh object and add to batch

#class CubeWorldGroup(pyglet.graphics.Group):
#
#    def set_state(self):
#        glTexGeni( GL_S, GL_TEXTURE_GEN_MODE, GL_REFLECTION_MAP )
#        glTexGeni( GL_T, GL_TEXTURE_GEN_MODE, GL_REFLECTION_MAP )
#        glTexGeni( GL_R, GL_TEXTURE_GEN_MODE, GL_REFLECTION_MAP )
#        glEnable( GL_TEXTURE_CUBE_MAP )
#        glTexEnvi( GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL )

batch1 = pyglet.graphics.Batch()

extent = 15
batch1.add(24, GL_QUADS, cubemap.texture_group_a,
    ('v3f', (
        -extent, -extent, extent,
        -extent, -extent, -extent,
        -extent, extent, -extent,
        -extent, extent, extent,
        extent, -extent, -extent,
        extent, -extent, extent,
        extent, extent, extent,
        extent, extent, -extent,
        -extent, -extent, -extent,
        extent, -extent, -extent,
        extent, extent, -extent,
        -extent, extent, -extent,
        extent, -extent, extent,
        -extent, -extent, extent,
        -extent, extent, extent,
        extent, extent, extent,
        -extent, extent, extent,
        -extent, extent, -extent,
        extent, extent, -extent,
        extent, extent, extent,
        -extent, -extent, -extent,
        -extent, -extent, extent,
        extent, -extent, extent,
        extent, -extent, -extent)),
    ('t3f', (
        -1.0, -1.0, 1.0,
        -1.0, -1.0, -1.0,
        -1.0, 1.0, -1.0,
        -1.0, 1.0, 1.0,
        1.0, -1.0, -1.0,
        1.0, -1.0, 1.0,
        1.0, 1.0, 1.0,
        1.0, 1.0, -1.0,
        -1.0, -1.0, -1.0,
        1.0, -1.0, -1.0,
        1.0, 1.0, -1.0,
        -1.0, 1.0, -1.0,
        1.0, -1.0, 1.0,
        -1.0, -1.0, 1.0,
        -1.0, 1.0, 1.0,
        1.0, 1.0, 1.0,
        -1.0, 1.0, 1.0,
        -1.0, 1.0, -1.0,
        1.0, 1.0, -1.0,
        1.0, 1.0, 1.0,
        -1.0, -1.0, -1.0,
        -1.0, -1.0, 1.0,
        1.0, -1.0, 1.0,
        1.0, -1.0, -1.0)))

batch2 = pyglet.graphics.Batch()
mesh_id = miru.graphics.load_mesh(
        (sys.argv[1:] and sys.argv[1]
            or os.path.join('docs', 'demo', 'yam.obj')))
miru.graphics.batch_mesh(
        mesh_id, batch2, cubemap.texture_group_b, False)

obj = core.Object(batch1)
context.add_object(obj)
obj = core.Object(batch2)
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




