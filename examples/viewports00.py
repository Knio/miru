from pyglet import options
options['debug_gl'] = False

from pyglet.gl import *
import pyglet
from pyglet.window import key

from miru import ui
from miru import utils
from miru import camera
from miru import imiru
from miru import core
from miru.context import context
from miru import graphics
from miru import input

MOVE = False

# initialize the window
w = ui.TestWindow(680, 400)
w.set_vsync(False)
#w.set_fullscreen(True)

perspProj = camera.PerspectiveProjection()
lights = camera.LightGroup([
            camera.PositionalLight(), camera.DirectionalLight()])

cam1 = camera.Camera(pos=(0,0,4), angle=(0,0,0), lights=lights,
        projection=camera.Viewport((0.0,0.5),(0.5,1.0), perspProj))
cam2 = camera.Camera(pos=(0,2,8), angle=(45,180,0), lights=lights,
        projection=camera.Viewport((0.5,0.5),(1.0,1.0)))
cam3 = camera.Camera(pos=(0,1,7), angle=(90,0,0), lights=lights,
        projection=camera.Viewport((0.0,0.0),(0.5,0.5)))
cam4 = camera.Camera(pos=(0,1,5), angle=(0,50,0), lights=lights,
        projection=camera.Viewport((0.5,0.0),(1.0,0.5)))

context.camera = camera.MetaCamera(cam1, cam2, cam3, cam4)
cam4.objects = cam3.objects = cam2.objects = cam1.objects
context.camera.debug = True

utils.add_fps_display(context)

context.window = w
context.control = input.SimpleMouseControl()

for pos in ((0,0,0),(1,1,-4),(-1,-1,-2)):
    o = w._load_object()
    o.pos = pos
    #o.debug = True

#plane = mesh.newObject(
#        mesh.CoordPlane, color=(0.5,0.5,0.5,1)).inRenderStages(
#            imiru.IWorldRenderStage)
pattern = pyglet.image.CheckerImagePattern(
        (0,60,0,200), (0,30,0,200))
tex = pattern.create_image(64, 64).get_texture()
coords = []
for i in range(0, len(tex.tex_coords), 3):
    coords.extend(tex.tex_coords[i:i+3] + (0.125 / 2,))
batch = pyglet.graphics.Batch()
group = graphics.TextureBindGroup(tex.id)
batch.add(4, GL_QUADS, group,
        ('v3f', [-10, 0, -10, 10, 0, -10, 10, 0, 10, -10, 0, 10]),
        ('t4f', coords))
#context.add_object(core.Object(batch))

print """
You should see 4 viewports dividing the window evenly 
with different projections on the same scene containing
3 objects.
"""

def update(dt):
    cam2.angle.y += 35 * dt
    cam3.angle.x += 35 * dt
    cam4.angle.y += 35 * dt

if MOVE:
    clock.schedule_interval(update, 1/60.)

while not w.has_exit:
    pyglet.clock.tick()
    w.clear()
    w.dispatch_events()
    context.render()
    w.flip()
w.close()




