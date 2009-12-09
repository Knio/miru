from pyglet.gl import *
import pyglet

from miru.ui import TestWindow
from miru.track import PosTrack
from miru import effects
from miru import utils
from miru import input
from miru import core
from miru import graphics
from miru.context import context

fog = effects.Fog(density=0.075, color=(0.65,0.9,0.75,0.5), equation=effects.Fog.EQ_EXP)
w = TestWindow(680, 400, clear_color=fog.color)

w.set_vsync(False)

context.camera.pos=(0,1.25,4)
context.window = w
context.control = input.SimpleMouseControl()

utils.add_fps_display(context)

o = w._load_object()
o.pos += (2,0.55,-3)
o = w._load_object()
o.pos += (0.5,1.55,-10)
o = w._load_object()
o.pos += (-0.5,0.55,0)


pattern = pyglet.image.CheckerImagePattern(
        (90,0,0,200), (0,30,0,200))
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
refl = effects.Reflection(ground=ground, camera=context.camera)

context.camera.effects[:] = [refl, fog]


print """
You should see some objects in fog and reflections 
below them.
"""

while not w.has_exit:
    pyglet.clock.tick()
    w.clear()
    w.dispatch_events()
    context.render()
    w.flip()


w.close()



