
from pyglet.gl import *
import pyglet

from miru.ui import TestWindow
from miru.track import PosTrack
from miru import effects
from miru import utils
from miru import graphics
from miru.context import context
from miru import input
from miru import core

class Window(TestWindow):
    def on_resize(self,w,h):
        context.camera.projection.on_resize(w,h)

# initialize the window
w = Window(680, 400)
w.set_vsync(False)

utils.add_fps_display(context)

context.camera.pos= (0,1.25,4)
context.window = w
context.control = input.SimpleMouseControl()

o = w._load_object()
o.pos += (2,0.55,-3)
o = w._load_object()
o.pos += (0.5,1.55,-2)
o = w._load_object()
o.pos += (-0.5,0.55,0)



print """
You should see 3 objects with their
reflection on the plane beneath them.
"""


pattern = pyglet.image.CheckerImagePattern(
        (255,255,255,100), (0,0,0,100))
tex = pattern.create_image(64, 64).get_texture()

coords = []
for i in range(0, len(tex.tex_coords), 3):
    coords.extend(tex.tex_coords[i:i+3] + (0.125 / 2,))
batch = pyglet.graphics.Batch()
group = graphics.TextureBindGroup(tex.id)
batch.add(4, GL_QUADS, group,
        ('v3f', [-10, 0, -10, 10, 0, -10, 10, 0, 10, -10, 0, 10]),
        ('t4f', coords))
ground = core.Object(batch)

refl = effects.Reflection(camera=context.camera, ground=ground)
context.camera.effects.append(refl)

while not w.has_exit:
    pyglet.clock.tick()
    w.clear()
    w.dispatch_events()
    context.render()
    w.flip()
w.close()


