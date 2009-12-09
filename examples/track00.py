from pyglet import font
from pyglet import clock

from miru.ui import TestWindow
from miru.context import context
from miru import input
from miru import utils
from miru.camera import *

# initialize the window
w = TestWindow(680, 400)
w.set_vsync(0)
utils.add_fps_display(context)
context.camera.pos = (0,0,10)
context.window = w

for i in range(-30,35,5):
    o = w._load_object()
    o.pos.x = i
    o.pos.z -= 5
w._load_object()

target = context.camera.objects[-1]
target.pos.z += 5
target.angle.x = 45
context.camera.track_target = target
step = 0.010


def main():
    global target, step
    while not w.has_exit:
        clock.tick()
        w.clear()
        
        target.pos.x += step
        if abs(target.pos.x) >= 17:
            step *= -1
        w.dispatch_events()
        context.render()
        w.flip()

def update(dt):
    global target, step
    #clock.tick()
    w.clear()
    
    target.pos.x += step
    if abs(target.pos.x) >= 17:
        step *= -1
    #w.dispatch_events()
    context.render()
    w.flip()
    if w.has_exit:
        from pyglet import app
        app.event_loop.exit()


print """The camera should rotate left to right to follow
the moving object.  Note that the camera does not change its
position.
"""


import sys
if sys.argv[1:] and sys.argv[1] == 'alpha':
    from pyglet import app
    clock.schedule(update)
    app.run()
else:
    main()


w.close()


