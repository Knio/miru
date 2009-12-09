from pyglet import options
options['debug_gl'] = True
#options['debug_gl_trace'] = True
#options['debug_gl_trace_args'] = True
options['vsync'] = False

from pyglet.gl import *

import miru.ui
from miru.context import context
import miru.graphics
import miru.input
import miru.camera

import pyglet.graphics
import pyglet.image
from pyglet import clock

import os, sys, random

window = miru.ui.TestWindow(600, 400)


ambient = (0.2, 0.2, 0.2, 1)
diffuse = (0.7, 0.7, 0.7, 1)

context.window = window
context.camera.rotation_mode = context.camera.ROTATE_MODE
context.camera.pos.z = 7
context.camera.lights = miru.camera.LightGroup([
    miru.camera.DirectionalLight(ambient=ambient, diffuse=diffuse)
        ])
#    miru.camera.PositionalLight(pos=(0,2,0))])
#miru.camera.PositionalLight(
#    pos=(0,1,0),#(100.0, 150.0, 200.0),
#    ambient=(0.2, 0.2, 0.2, 1),
#    diffuse=(0.7, 0.7, 0.7, 1),
#    )
#])
context.control = miru.input.SimpleMouseControl()

glEnable( GL_CULL_FACE )

batch = pyglet.graphics.Batch()
mesh_id = miru.graphics.load_mesh(
        (sys.argv[1:] and sys.argv[1]
            or os.path.join('docs', 'demo', 'yam.obj')))
miru.graphics.batch_mesh(mesh_id, batch)
#obj = mesh_id
#obj = miru.graphics.Object(batch)
obj = miru.core.Object(batch)
#obj = miru.graphics.load_wobj(batch)
#context.add_object(obj)
context.add_object(batch)
context.osd.add_object(clock.ClockDisplay())

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




