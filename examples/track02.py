from pyglet import font
from pyglet import clock

from miru.ui import TestWindow
from miru.context import context
#from miru import input
from miru.track import PosTrack
from miru import utils
from miru.camera import *

# initialize the window
w = TestWindow(680, 400)
w.set_vsync(False)

context.camera.pos = (0,0,10)
context.window = w
#context.control = input.SimpleMouseControl()

utils.addFpsDisplay()

for i in range(-30,35,5):
    for j in (-1, 1):
        o = w._load_object()
        o.pos.x = i
        o.pos.y = j * (6 - abs(i) / 5.)
        o.pos.z -= 6 - abs(i) / 6.
target = w._load_object()

target.pos += (0,0,5)
target.angle.x = 45

track = PosTrack(context.camera, target)

#context.addobj(CoordPlane(color=(0,1,0,1)))
#context.addobj(CoordPlane(axes=(0,1,1),color=(1,0,0,1)))
#context.addobj(CoordPlane(axes=(1,1,0),color=(0,0,1,1)))

print """
The camera should follow the object at the center of the screen
along the x,y and z axes.
"""

step = 0.010
while not w.has_exit:
    clock.tick()
    w.clear()
    target.pos += (step, step, step)
    if abs(target.pos.x) >= 17:
        step *= -1
    w.dispatch_events()
    context.render()
    w.flip()


