
from pyglet.gl import gl
import pyglet

import miru
from miru.ext import geom

def checker_quad(size=64, scale=0.125, color1=(1,1,1,1),
        color2=(0,0,0,1)):
    """
    This returns a two-tuple consisting of:

        texture coords: scaled by factor given in scale argument
        Texture object: this can be added to miru.graphics.TextureBindGroup
    """
    c1 = tuple([ int(channel * 255) for channel in color1 ])
    c2 = tuple([ int(channel * 255) for channel in color2 ])
    pattern = pyglet.image.CheckerImagePattern(
            c1, c2)
    tex = pattern.create_image(size, size).get_texture()
    coords = []
    for i in range(0, len(tex.tex_coords), 3):
        coords.extend(tex.tex_coords[i:i+3] + (scale / 2,))
    return coords, tex


class CoordinatePlane(object):
    drawing_mode = gl.GL_LINES
    vertex_pitch = 3

    def __init__(self, size=40, step=0.5):
        self.vertex_data = []
        steps = int(size / step)
        w = int(size * 0.5)
        z = steps/2
        print 'Z', z
        for i in range(-z, z + 1):
            x = i * step
            self.vertex_data.extend([x, 0, -w, x, 0, w, w, 0, x, -w, 0, x])
        

def batch_coordplane(size=40, step=0.5, color=(1,1,1,1), batch=None,
        lighting=False):
    """
    This function simplifies steps for building a CoordinatePlane
    and adding it to a graphics.Batch - if this is the desired behavior.
    """
    parent = None
    if not lighting:
        parent = miru.graphics.ColorMaterialGroup(lighting=False)
    group = miru.graphics.ColorGroup(color, parent=parent)
    if not batch:
        batch = pyglet.graphics.Batch()
    coordplane = CoordinatePlane(size, step)
    geom.get_vlist(coordplane, batch, group)
    return batch
     


