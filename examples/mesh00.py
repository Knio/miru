from pyglet import options
options['debug_gl'] = 0
options['debug_gl_trace'] = True
options['debug_gl_trace_args'] = True
options['vsync'] = False

from pyglet.gl import *

import miru.ui
import miru.input
from miru.context import context
import miru.graphics
from pyglet import clock
import pyglet.graphics

import itertools
import os
import random
import time

window = miru.ui.TestWindow(600, 400)

context.window = window
context.osd.window = context.window
context.osd.add_object(clock.ClockDisplay())
context.control = miru.input.SimpleMouseControl()

#(vlist, count, mode, group, batch) = miru.graphics.load_wfobj(
#        os.path.join('docs', 'demo', 'alien.obj'))
batch = pyglet.graphics.Batch()
mesh_id = miru.graphics.load_mesh(
        os.path.join('docs', 'demo', 'alien.obj'))
vlist, mode = miru.graphics.mesh_vlist(mesh_id)
img = pyglet.image.load(os.path.join('docs', 'demo', 'alien.png'))
tex = img.get_texture()
group = miru.graphics.TextureBindGroup(tex)

obj = miru.core.Object(batch)
context.add_object(obj)

before = time.time()
for i in range(100):
    #for pos in ((1,1,-4),(1.5,1.5,-3),(-1,-1,-2),(0,0,0)):
    pos = (-3.5 + random.random() * 7, -3 + random.random() * 6, -45 + random.random() * 40)
    vertices = vlist.vertices[:]
    for i in xrange(0, len(vertices), 3):
        vertices[i] += pos[0]
        vertices[i+1] += pos[1]
        vertices[i+2] += pos[2]
    data = [('v3f', vertices),
            ('t2f', list(vlist.tex_coords)),
            ('n3f', list(vlist.normals))]
    if mode == GL_QUADS:
        count = len(vertices) // 4
    else:
        count = len(vertices) // 3
    batch.add(count, mode, group, *data)
elapsed = time.time() - before
print 'Loading took %4.4fs' % elapsed
#vlist.delete()

while not window.has_exit:
    clock.tick()
    window.clear()
    window.dispatch_events()
    context.render()
    window.flip()
window.close()




