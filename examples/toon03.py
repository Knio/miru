from pyglet import options
options['debug_gl'] = 0
options['debug_gl_trace'] = 0
options['debug_gl_trace_args'] = 0
options['debug_graphics_batch'] = 0
options['debug_graphics_batch_quiet'] = 0
options['vsync'] = 0

import pyglet.gl as gl
import pyglet.graphics
import pyglet.clock

import miru.graphics
import miru.ui
import miru.input
import miru.core
import miru.camera
import miru.ext.geom
import miru.math3d

from miru.context import context

import euclid
import ctypes

window = miru.ui.BaseWindow(600,400, clear_color=(0.4,0.4,.4,1))
context.window = window
context.osd.add_object( pyglet.clock.ClockDisplay() )
context.control = miru.input.SimpleMouseControl()
context.camera.lights = miru.camera.LightGroup([])
context.camera.pos.z = 14
context.camera.angle.x = 0

gl.glDisable( gl.GL_LIGHTING )
gl.glEnable( gl.GL_CULL_FACE )

cell_shader = miru.graphics.CellShader()
texobjs = []
for color in [0.3, (0.7,0.,0), (0.0,0.7,0.0), (0.0,0,0.7), (0.7,0.7,0.0)]:
    color_table = cell_shader.create_color_table(color)
    texobjs.append( cell_shader.create_texobject( color_table ) )

geoms = [
    miru.ext.geom.Box(10),
    miru.ext.geom.Torus(divisions=27),
    miru.ext.geom.Cube(),
    miru.ext.geom.Torus(divisions=27),
    miru.ext.geom.Sphere(radius=2, slices=16, stacks=16)
    ]
objects = []
for (idx, pos) in enumerate( [(0,0,0),(-2.5,-2,0),(-2.5,2,0),(2.5,2,0),(2.5,-2,0)] ):
    geom = geoms[idx]
    objects.append( miru.core.Object(geom) )
    objects[-1].pos = pos
    if idx:
        objects[-1].angle.x = 45
    group = miru.core.ObjectGroup(
            objects[-1], parent=miru.graphics.TextureBindGroup(
                texobjs[idx],
                gl.GL_TEXTURE_1D,
                miru.graphics.tex_enable_group_1D))
    data = [ ('v3f', geom.vertex_data ),
             ('n3f', geom.normal_data ) ]
    indices = hasattr(geom, 'indices') and geom.indices or None
    cell_shader.add_vlist(
            len(geom.vertex_data) // geom.vertex_pitch,
            geom.drawing_mode,
            data, texobjs[idx], indices=indices, group=group )

obj = miru.core.Object(cell_shader.batch)
context.add_object( obj )

pyglet.clock.schedule_interval_soft( cell_shader.update, 1/60. )

camera_velocity = 15
def update_camera(dt):
    d = dt * camera_velocity
    context.camera.angle.y += d
pyglet.clock.schedule_interval(update_camera, 1/60.)

def pfps(dt):
    print pyglet.clock.get_fps()
pyglet.clock.schedule_interval(pfps, 3)

while not window.has_exit:
    window.clear()
    pyglet.clock.tick()
    window.dispatch_events()
    context.render()
    window.flip()
window.close()
