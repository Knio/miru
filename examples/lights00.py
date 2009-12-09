try:
    from psyco import full
except ImportError:
    print 'no psyco'

from pyglet import options as pyglet_options
pyglet_options['debug_gl'] = False

import pyglet

from miru.ui import TestWindow
from miru.context import context
from miru import options as miru_options
from miru import camera
from miru import utils
from miru import input
from miru import graphics
from miru import core
from miru.ext import geom

import os
P = os.path.join


# initialize the window
w = TestWindow(680, 400)
w.set_vsync(False)

utils.addFpsDisplay()

context.window = w
context.control = input.SimpleMouseControl()
context.camera.pos += (0,1,2)
context.camera.angle = (10,0,0)

#context.handle.accessible = True

o = graphics.load_wobj(P('docs','demo','alien.obj'))
o.pos += (0,0.95,-0.6)
context.add_object(o)

# Play around with the spot light
context.camera.lights = camera.LightGroup([
    camera.DirectionalLight(diffuse=(0.1,0.1,0.1,1)),
    camera.PositionalLight(pos=(0,2,0), spot_cutoff=25,
        track_target=o, spot_exponent=10, kq=0.1),
    camera.PositionalLight(pos=(-0.54,1.3,2.5), diffuse=(0.9,0,0,1)),
    camera.PositionalLight(pos=(1.6,1.3,2.7), diffuse=(0,0.9,0,1)),
    camera.PositionalLight(pos=(-2.7,1.7,0.3), diffuse=(0,0,0.9,1)),
    ])

for i in range(1,len(context.camera.lights)):
    context.camera.lights[i].debug = True

batch = pyglet.graphics.Batch()
color_group = graphics.ColorGroup((0.5,0.5,0.5,1.0))
objs = []
for x in range(-3, 4):
    for z in range(-3, 4):
        sphere = geom.Cube(0.7)
        geom.transform(sphere, (x * 1.23, 0, z * 1.23))
        geom.get_vlist(sphere, batch, color_group)
context.add_object(core.Object(batch))



print """
You should see a small grid of objects with some
colored lights over it.  You should be able to click
on the bulb of a light to move it around.  The white
light is a spotlight which remains focussed on the
object floating above the grid.
"""

while not w.has_exit:
    pyglet.clock.tick()
    w.clear()
    w.dispatch_events()
    context.render()
    w.flip()



w.close()


