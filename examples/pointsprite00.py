from pyglet import options
options['debug_gl'] = False
options['debug_gl_trace'] = False
options['debug_gl_trace_args'] = False
options['vsync'] = False


from pyglet.gl import *
import pyglet.clock
import pyglet.graphics

import miru.graphics
import miru.ui
import miru.input
import miru.core
from miru.context import context

import os, random, sys



window = miru.ui.BaseWindow(600,400)
context.window = window
context.osd.add_object(pyglet.clock.ClockDisplay())
context.control = miru.input.SimpleMouseControl()
context.camera.pos.z = 12
context.camera.angle.x = -35

CT = (sys.argv[1:] and int(sys.argv[1]) or 15000) // 30
print 'Rounded:', CT * 30

def flatten(l):
    newl = []
    for p in l:
        newl.extend(p[:])
    return tuple(newl)

tex = pyglet.image.load(
        os.path.join('docs', 'demo', 'point.png')).get_texture()

batch = pyglet.graphics.Batch()


for point_size in range(1,31):
    point_sprite_group = miru.graphics.PointSpriteGroup(tex, point_size)
    data = ('v3f', flatten([
            (-4 + random.random() * 8, (-4 + random.random() * 8), 0)
            for i in range(CT) ]))
    batch.add(CT, GL_POINTS, point_sprite_group, data)

obj = miru.core.Object(batch)
context.add_object(obj)

while not window.has_exit:
    window.clear()
    dt = pyglet.clock.tick()
    window.dispatch_events()
    context.render()
    window.flip()
window.close()

