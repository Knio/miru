import ctypes as c
import optparse

from pyglet import font
from pyglet import clock
from pyglet.gl import *

from miru.ui import Window
from miru import shader, components
from miru import imiru
from miru import utils
from miru import graphics
from miru.ext import geom
from miru.context import context
from miru import core
from miru import input


class ShaderWindow(Window):

    def on_resize(self, w, h):
        context.camera.projection.on_resize(w,h)


# initialize the window
config = Config(sample_buffers=1, samples=4, depth_size=16, double_buffer=True)
w = ShaderWindow(680, 400, config=config)
w.set_vsync(False)
context.window = w
context.control = input.SimpleMouseControl()

utils.add_fps_display(context)

VERTEX_SHADER = """
uniform vec3 lightPos[1];

void main(void)
{
    // normal MVP transform
    gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;

    vec3 N = normalize(gl_NormalMatrix * gl_Normal);
    vec4 V = gl_ModelViewMatrix * gl_Vertex;
    vec3 L = normalize(lightPos[0] - V.xyz);
    vec3 H = normalize(L + vec3(0.0, 0.0, 1.0));
    const float specularExp = 128.0;

    // calculate diffuse lighting
    float NdotL = max(0.0, dot(N, L));
    vec4 diffuse = gl_Color * vec4(NdotL);

    // calculate specular lighting
    float NdotH = max(0.0, dot(N, H));
    vec4 specular = vec4(0.0);
    if (NdotL > 0.0) 
        specular = vec4(pow(NdotH, specularExp));

    // sum the diffuse and specular components
    gl_FrontColor = diffuse + specular;
}
"""


vshaders = []
fshaders = []

parser = optparse.OptionParser()
parser.add_option('-v', '--vertex-shader', dest='vshader')
parser.add_option('-f', '--fragment-shader', dest='fshader')
opts, args = parser.parse_args()
if opts.vshader:
    for f in opts.vshader.split(','):
        data  = open(f).read()
        vs = shader.VertexShader(data)
        vshaders.append(vs)
else:
    vshaders.append(shader.VertexShader(VERTEX_SHADER))
if opts.fshader:
    for f in opts.fshader.split(','):
        data = open(f).read()
        fs = shader.FragmentShader(data)
        fshaders.append(fs)

print 'creating program with:', vshaders + fshaders
program = shader.createProgram(*(vshaders + fshaders))

batch = pyglet.graphics.Batch()
shader_group = shader.ShaderGroup(program)

color_group1 = graphics.ColorGroup((0.0,1.0,1.0), parent=shader_group)
sphere1 = geom.Sphere( radius=0.63 )
geom.transform(sphere1, (-0.93,0,0))
geom.get_vlist(sphere1, batch, color_group1)

color_group2 = graphics.ColorGroup((0.0,1.0,0.0), parent=shader_group)
sphere2 = geom.Sphere( radius=0.63 )
geom.transform(sphere2, (0,-0.93,0))
geom.get_vlist(sphere2, batch, color_group2)

color_group3 = graphics.ColorGroup((1.0,0.0,0.0), parent=shader_group)
sphere3 = geom.Sphere( radius=0.63 )
geom.transform(sphere3, (0,0.93,0))
geom.get_vlist(sphere3, batch, color_group3)

color_group4 = graphics.ColorGroup((1.0,0.0,1.0), parent=shader_group)
sphere4 = geom.Sphere( radius=0.63 )
geom.transform(sphere4, (0.93,0,0))
geom.get_vlist(sphere4, batch, color_group4)



context.add_object(core.Object(batch))


print """You should see four spheres with pretty
shading.
"""

while not w.has_exit:
    clock.tick()
    w.clear()
    w.dispatch_events()
    context.render()
    w.flip()

w.close()


