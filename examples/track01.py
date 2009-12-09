from pyglet import font
from pyglet import clock

from miru.ui import TestWindow
from miru.context import context
from miru import utils
from miru import input

# initialize the window
w = TestWindow(680, 400)
w.set_vsync(False)
context.window = w

utils.add_fps_display(context)

context.camera.pos = (0,0,10)
context.control = input.SimpleMouseControl()

for i in range(-30,35,3):
    o = w._load_object()
    o.pos.x = i
    o.pos.y = 6 - abs(i) / 5.
    o.pos.z -= 6 - abs(i) / 6.
w._load_object()

target = context.camera.objects[-1]
target.pos.z += 5
target.pos.y = 2
target.angle.x = 45
context.camera.track_target = target
context.camera.pos.y = 3
step = 0.010


print """
The camera should be looking down at the moving object
and following it as it oscillates left to right.
The camera does not change its position.
"""

while not w.has_exit:
    clock.tick()
    w.clear()
    target.pos.x += step
    if abs(target.pos.x) >= 17:
        step *= -1
    w.dispatch_events()
    context.render()
    w.flip()


w.close()

