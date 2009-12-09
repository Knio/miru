from pyglet import font
from pyglet import clock

from miru.ui import TestWindow
from miru import graphics
from miru import input
from miru.context import context
from miru.track import SSCameraTrack, PosTrack
from miru import utils

import os

# initialize the window
w = TestWindow(680, 400)
w.set_vsync(False)

context.camera.pos = (0,5,10)
context.window = w

utils.addFpsDisplay()

target = w._load_object()
#target = loadObj(os.path.join('docs', 'demo', 'yam.obj'))
#target.angle = (0,45,0)
#context.addobj(target)

target.pos += (0,5,5)
target.angle.x = 45

# Here we set up two tracks.  The first is a side scroller
# track the will move the camera only as the object reaches
# the edge of the screen.  The second is a normal positional
# track - but only on the z coordinate of the object.
track = SSCameraTrack(context.camera, target, context.window)
track2 = PosTrack(context.camera, target, axes=(0,0,1))

#context.addobj(CoordPlane(magnitude=50, step=1, color=(1,1,0,1)))


print """
The camera should follow the object only as it approaches
the edge of the window.  The object does not get further
from the camera on the z-axis (as it moves further into the
screen).
"""

step = 0.010
ct = 0
while not w.has_exit:
    clock.tick()
    w.clear()
    if ct in (0,1):
        target.pos += (step, 0, step)
        if abs(target.pos.x) >= 10:
            step *= -1
            ct += 1
            ct %= 4
    else:
        target.pos += (0,step,step)
        if abs(target.pos.y) >= 10:
            step *= -1
            ct += 1
            ct %= 4
    w.dispatch_events()
    context.render()
    w.flip()
w.close()


