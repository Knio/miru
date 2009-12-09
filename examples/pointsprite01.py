from pyglet import options
options['debug_gl'] = 0
#options['debug_gl_trace'] = 1
#options['debug_gl_trace_args'] = 1
options['vsync'] = 0


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
context.camera.pos.z = 25
#context.camera.angle.x = -35
context.camera.depth_sort = True

def flatten(l):
    newl = []
    for p in l:
        newl.extend(p[:])
    return tuple(newl)

tex = pyglet.image.load(
        os.path.join('docs', 'demo', 'point.png')).get_texture()

batch = pyglet.graphics.Batch()

CT = (sys.argv[1:] and int(sys.argv[1]) or 3000) // 30

r = lambda : 5 - random.random() * 10

velocities = []
vlists = []
for point_size in range(1,31):
    point_sprite_group = miru.graphics.PointSpriteGroup(tex, point_size,
            attenuate=True)
    data = ('v3f', flatten([
            (-4 + random.random() * 8, (-4 + random.random() * 8), 0)
            for i in range(CT) ]))
    for i in range(CT):
        velocities.append([r(), r()])
    vlists.append(batch.add(CT, GL_POINTS, point_sprite_group, data))

print 'Rounded to:', len(velocities)

obj = miru.core.Object(batch)
context.add_object(obj)


def update(dt):
    # This is going to be slowwwwwwwwwww
    for (idx, vel) in enumerate(velocities):
        dx = vel[0] * dt
        dy = vel[1] * dt
        vlist = vlists[idx // CT]
        j = idx % CT
        vlist.vertices[j*3] += dx
        vlist.vertices[j*3+1] += dy
pyglet.clock.schedule_interval(update, 1/60.)

@window.event
def on_draw():
    window.clear()
    context.render()

pyglet.app.run()
#while not window.has_exit:
#    window.clear()
#    dt = pyglet.clock.tick()
#    window.dispatch_events()
#    context.render()
#    window.flip()
#window.close()

