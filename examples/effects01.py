from pyglet.gl import *
import pyglet

from miru.ui import TestWindow
from miru.camera import *
from miru.track import PosTrack
from miru.context import context
from miru import effects
from miru import utils
from miru import input
from miru import graphics

# Create the fog effect and add to effects in window -
# that is, the effect will get applied on once per window resize
fog = effects.Fog(density=0.1, color=(0.9,0.8,0.75,0.5), equation=effects.Fog.EQ_EXP)
w = TestWindow(680, 400, clear_color=fog.color)
w.set_vsync(False)

context.camera.effects = [fog]

utils.add_fps_display(context)

context.camera.pos= (0,1.25,4)
context.window = w
context.control = input.SimpleMouseControl()

o = w._load_object()
o.pos += (2,0.55,-3)
o = w._load_object()
o.pos += (0.5,1.55,-10)
o = w._load_object()
o.pos += (-0.5,0.55,0)


pattern = pyglet.image.CheckerImagePattern(
        (90,0,0,255), (0,30,0,255))
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
context.add_object(ground)

print """
You should see some objects in fog.
"""

while not w.has_exit:
    pyglet.clock.tick()
    w.clear()
    w.dispatch_events()
    context.render()
    w.flip()

w.close()


