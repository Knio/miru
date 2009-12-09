import itertools
import random
import os

from euclid import Vector3

from pyglet.gl import *
from pyglet.window import key
import pyglet

from miru.ui import TestWindow
from miru import core
from miru.trees import Octree, OctreeDebug
from miru import utils
from miru.context import context
from miru import input
import miru.graphics

# initialize the window
w = TestWindow(680, 400, clear_color=(0,0,0,1))
w.set_vsync(0)

context.camera.pos = (155,130,485)
context.camera.angle = (0,45,0)
context.window = w
context.control = input.SimpleMouseControl()

utils.addFpsDisplay()

otree = Octree(width=256, max_population=20, min_width=1)
o = core.Object(OctreeDebug(otree))
context.add_object(o)

class Point(core.PositionalMixin):
    pass


batch = pyglet.graphics.Batch()
tex = pyglet.image.load(
        os.path.join('docs', 'demo',
                     'point.png')).get_texture()
point_sprite_group = miru.graphics.PointSpriteGroup(tex, 6)
data = ('v3f', [-99999] * 18000)
vlist = batch.add(6000, GL_POINTS, point_sprite_group, data)
index = 0
context.add_object(core.Object(batch))

biases = itertools.cycle([
    [(1,127),(1,127),(1,127)],
    [(1,127),(1,127),(128,255)],
    [(1,127),(128,255),(1,127)],
    [(1,127),(128,255),(128,255)],
    [(128,255),(1,127),(1,127)],
    [(128,255),(1,127),(128,255)],
    [(128,255),(128,255),(1,127)],
    [(128,255),(128,255),(128,255)],
    [(1,255),(1,255),(1,255)] ])
context.bias = [(1,255),(1,255),(1,255)]
REPEAT = 10

#@context.window.event
def on_key_press(k,modifiers):
    global index
    if k == key.B:
        for i in range(REPEAT):
            if index >= 6000:
                return
            x = random.randint(*context.bias[0])
            y = random.randint(*context.bias[1])
            z = random.randint(*context.bias[2])
            #points.drawable.points.append((x,y,z))
            idx = index * 3
            vlist.vertices[idx:idx+3] = (x,y,z)
            otree.addObject(Point(pos=(x,y,z)))
            index += 1
        return True
    if k == key.H:
        # Set a bias
        context.bias = biases.next()
        print 'current bias', context.bias
        

context.window.push_handlers(on_key_press)


print """
Hit the B key to begin adding green dots to the cube.
Hit the H key to concentrate on one of 8 octants.

With lots of dots added to the cube, overpopulated regions
will become subdivided.
"""

while not w.has_exit:
    pyglet.clock.tick()
    w.clear()
    w.dispatch_events()
    context.render()
    w.flip()

w.close()

result = raw_input("Did it work? [y/N] ")
from miru.test import reportFtest
reportFtest('octrees', result)

