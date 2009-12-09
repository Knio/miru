import math, time, ctypes
import euclid

from pyglet import options
options['debug_gl'] = 0

from pyglet.gl import *
from pyglet.window import key
import pyglet.graphics
import pyglet.clock

import miru.graphics
import miru.ui
import miru.input
import miru.core
import miru.math3d
import miru.ext.geom
from miru.context import context


class Window(miru.ui.BaseWindow):
    def on_resize(self, w, h):
        gen_shadow_map()

# 512x512 to make this trial easier.  For textures larger than
# window size, FBO would have to be used.
window = Window(1024, 512)
context.window = window

# CONSTANTS ####################################
shadow_width = window.width
shadow_height = window.height
ambient_light = (GLfloat * 4)( 0.2, 0.2, 0.2, 1.0 )
diffuse_light = (GLfloat * 4)( 0.7, 0.7, 0.7, 1.0 )
light_pos  = (GLfloat * 4)( 100.0, 300.0, 100.0, 1.0 )
camera_pos = [ 100.0, 150.0, 200.0, 1.0 ]
camera_zoom = 0.3
factor = 4.0
ambientShadowAvailable = False
texture_id = None
tex_matrix = None
showShadowMap = False
################################################

context.camera.pos = camera_pos


# Set up the models for drawing
batch = pyglet.graphics.Batch()

# A red cube
cube = miru.ext.geom.Cube(48)
miru.ext.geom.transform(cube, (0,10,0))
redgroup = miru.graphics.ColorGroup((0.9,0.3,0.3))
miru.ext.geom.get_vlist(cube, batch, redgroup)


cube2 = miru.ext.geom.Cube(38)
miru.ext.geom.transform(cube2, (50,0,40))
miru.ext.geom.get_vlist(cube2,
        batch, miru.graphics.ColorGroup((0.3,0.3,0.9)))

# A green sphere
sphere = miru.ext.geom.Sphere(radius=25.0)
miru.ext.geom.transform(sphere, (-60,0,0))
greengroup = miru.graphics.ColorGroup((0.3,0.9,0.3))
miru.ext.geom.get_vlist(sphere, batch, greengroup)

# A yellow sphere 
sphere2 = miru.ext.geom.Sphere(radius=17.0)
miru.ext.geom.transform(sphere2, (50,10,0))
yellowgroup = miru.graphics.ColorGroup((0.9,0.9,0.3))
miru.ext.geom.get_vlist(sphere2, batch, yellowgroup)

# A magenta torus
torus = miru.ext.geom.Torus(inner_radius=8.0, outer_radius=16.0)
miru.ext.geom.transform(torus, (0,0,60.))
magentagroup = miru.graphics.ColorGroup((0.9,0.3,0.9))
miru.ext.geom.get_vlist(torus, batch, magentagroup)

box = miru.ext.geom.Box(200)
box_vlist = miru.ext.geom.get_vlist(box)

def draw_models(draw_base_plane):
    if draw_base_plane:
        glPushMatrix()
        glColor3f(0.7,0.7,0.7)
        glTranslatef(0, 75, 0)
        box_vlist.draw(GL_QUADS)
        glPopMatrix()
    batch.draw()

def gen_shadow_map():
    global tex_matrix
    # scene's bounding radius
    scene_radius = 95.0
    light_to_scene_distance = math.sqrt(
            light_pos[0]**2 + light_pos[1]**2 + light_pos[2]**2)
    print 'Light to scene distance:', light_to_scene_distance
    near_plane = light_to_scene_distance - scene_radius
    print 'Near plane:', near_plane
    field_of_view = miru.math3d.radians_to_degrees(2.0 *
            math.atan(scene_radius / float(light_to_scene_distance)))
    print 'Field of view:', field_of_view
    

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(field_of_view, 1.0, near_plane,
            near_plane + (2.0 * scene_radius))
    light_projection = euclid.Matrix4()
    tmp = (GLfloat * 16)()
    glGetFloatv(GL_PROJECTION_MATRIX, tmp)
    light_projection[0:16] = tmp[:]
    
    # Switch to light's point of view
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(light_pos[0], light_pos[1], light_pos[2],
              0.0, 0.0, 0.0, 0.0, 1.0, 0.0)
    light_mview = euclid.Matrix4()
    glGetFloatv(GL_MODELVIEW_MATRIX, tmp)
    light_mview[0:16] = tmp[:]
    glViewport(0, 0, shadow_width, shadow_height)

    # Clear the depth buffer only
    glClear(GL_DEPTH_BUFFER_BIT)

    # All we care about here is resulting depth values
    glShadeModel(GL_FLAT)
    glDisable(GL_LIGHTING)
    glDisable(GL_COLOR_MATERIAL)
    glDisable(GL_NORMALIZE)
    glColorMask(0, 0, 0, 0)

    # Overcome imprecision
    glEnable(GL_POLYGON_OFFSET_FILL)

    # Draw objects in the scene except base plane
    # which never shadows anything
    draw_models(False)

    # Copy depth values into depth texture
    glCopyTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT,
                     0, 0, shadow_width, shadow_height, 0)

    # Restore normal drawing state
    glShadeModel(GL_SMOOTH)
    glEnable(GL_LIGHTING)
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_NORMALIZE)
    glColorMask(1, 1, 1, 1)
    glDisable(GL_POLYGON_OFFSET_FILL)

    # Set up texture matrix for shadow map projection,
    # which will be rolled into the eye linear
    # texture coordinate generation plane equations
    #M3DMatrix44f tmp_matrix
    #m3dLoadIdentity44(tmp_matrix)
    tex_matrix = euclid.Matrix4()
    #m3dTranslateMatrix44(tmp_matrix, 0.5f, 0.5f, 0.5f)
    tex_matrix.translate(0.5, 0.5, 0.5).scale(0.5, 0.5, 0.5)
    #m3dScaleMatrix44(tmp_matrix, 0.5f, 0.5f, 0.5f)
    #tex_matrix.scale(0.5, 0.5, 0.5)
    #m3dMatrixMultiply44(tex_matrix, tmp_matrix, light_projection)
    tex_matrix = (tex_matrix * light_projection) * light_mview
    #m3dMatrixMultiply44(tmp_matrix, tex_matrix, light_mview)
    #tex_matrix = tex_matrix * light_mview


    # transpose to get the s, t, r, and q rows for plane equations
    #m3dTransposeMatrix44(tex_matrix, tmp_matrix)
    #print tmp_matrix
    #tex_matrix = 
    tex_matrix.transpose()
    # XXX
    #tex_matrix[:] = [1.084, -0.452, -1.385, 165.831,
    #    -1.267, 0.292, -1.267, 165.831,
    #    -0.677, -2.031, -0.677, 213.331,
    #    -0.302, -0.905, -0.302, 331.662 ]
    print tex_matrix


def setup_rc():
    global texture_id
    # Black background
    glClearColor(0.0, 0.0, 0.0, 1.0)

    # Hidden surface removal
    glEnable( GL_CULL_FACE )
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glPolygonOffset(factor, 0.0)
    glEnable(GL_MULTISAMPLE)
    glEnable(GL_SMOOTH)

    # Set up some lighting state that never changes
    glShadeModel(GL_SMOOTH)
    glEnable(GL_LIGHTING)
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_NORMALIZE)
    glEnable(GL_LIGHT0)

    # Set up some texture state that never changes
    texture_id = GLuint()
    glGenTextures(1, ctypes.byref(texture_id))
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_DEPTH_TEXTURE_MODE, GL_INTENSITY)
    if ambientShadowAvailable:
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_COMPARE_FAIL_VALUE_ARB,
                        0.5)
    glTexGeni(GL_S, GL_TEXTURE_GEN_MODE, GL_EYE_LINEAR)
    glTexGeni(GL_T, GL_TEXTURE_GEN_MODE, GL_EYE_LINEAR)
    glTexGeni(GL_R, GL_TEXTURE_GEN_MODE, GL_EYE_LINEAR)
    glTexGeni(GL_Q, GL_TEXTURE_GEN_MODE, GL_EYE_LINEAR)

    gen_shadow_map()

class RenderPass:

    def enable(self):
        raise NotImplementedError, 'Subclass RenderPass to implement'

    def disable(self):
        raise NotImplementedError, 'Subclass RenderPass to implement'

class DepthBufferPass(RenderPass):

    _shade_model = None

    def enable(self):
        self._shade_model = GLint()
        glGetIntegerv( GL_SHADE_MODEL, self._shade_model )
        glPushAttrib( GL_ENABLE_BIT )
        glShadeModel( GL_FLAT )
        glDisable( GL_LIGHTING )
        glDisable( COLOR_MATERIAL )
        glDisable( GL_NORMALIZE )

    def disable(self):
        glPopAttrib()
        glShadeModel( self._shade_model.value )


def render():

    # Track camera angle
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    if (window.width > window.height):
        ar = window.width / float(window.height)
        glFrustum(-ar * camera_zoom, ar * camera_zoom,
                -camera_zoom, camera_zoom, 1.0, 1000.0)
    else:
        ar = window.height / float(window.width)
        glFrustum(-camera_zoom, camera_zoom,
                -ar * camera_zoom, ar * camera_zoom, 1.0, 1000.0)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(camera_pos[0], camera_pos[1], camera_pos[2],
              0.0, 0.0, 0.0, 0.0, 1.0, 0.0)

    glViewport(0, 0, window.width, window.height)
    
    # Track light position
    glLightfv(GL_LIGHT0, GL_POSITION, light_pos)

    # Clear the window with current clearing color
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    if showShadowMap:
        # Display shadow map for educational purposes
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glMatrixMode(GL_TEXTURE)
        glPushMatrix()
        glLoadIdentity()
        glEnable(GL_TEXTURE_2D)
        glDisable(GL_LIGHTING)
        glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_COMPARE_MODE, GL_NONE)
        # Show the shadowMap at its actual size relative to window
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex2f(-1.0, -1.0)
        glTexCoord2f(1.0, 0.0)
        glVertex2f((shadow_width/float(window.width)) * 2.0 - 1.0,
                   -1.0)
        glTexCoord2f(1.0, 1.0)
        glVertex2f((shadow_width/float(window.width)) * 2.0 - 1.0,
                   (shadow_height/float(window.height)) * 2.0 - 1.0)
        glTexCoord2f(0.0, 1.0)
        glVertex2f(-1.0,
                   (shadow_height/float(window.height))*2.0-1.0)
        glEnd()
        glDisable(GL_TEXTURE_2D)
        glEnable(GL_LIGHTING)
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        gluPerspective(45.0, 1.0, 1.0, 1000.0)
        glMatrixMode(GL_MODELVIEW)
        return
    
    if not ambientShadowAvailable:
        low_ambient = (GLfloat * 4)(0.1, 0.1, 0.1, 1.0)
        low_diffuse = (GLfloat * 4)(0.35, 0.35, 0.35, 1.0)
        # Because there is no support for an "ambient"
        # shadow compare fail value, we'll have to
        # draw an ambient pass first...
        glLightfv(GL_LIGHT0, GL_AMBIENT, low_ambient)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, low_diffuse)
        # Draw objects in the scene, including base plane
        draw_models(True)
        # Enable alpha test so that shadowed fragments are discarded
        glAlphaFunc(GL_GREATER, 0.7)
        glEnable(GL_ALPHA_TEST)
    
    glLightfv(GL_LIGHT0, GL_AMBIENT, ambient_light)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse_light)

    # Set up shadow comparison
    glEnable(GL_TEXTURE_2D)
    glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_COMPARE_MODE,
                    GL_COMPARE_R_TO_TEXTURE)

    # Set up the eye plane for projecting the shadow map on the scene
    glEnable(GL_TEXTURE_GEN_S)
    glEnable(GL_TEXTURE_GEN_T)
    glEnable(GL_TEXTURE_GEN_R)
    glEnable(GL_TEXTURE_GEN_Q)
    glTexGenfv(GL_S, GL_EYE_PLANE,
           (GLfloat * 4)(*tex_matrix[0:4]))
    glTexGenfv(GL_T, GL_EYE_PLANE,
           (GLfloat * 4)(*tex_matrix[4:8]))
    glTexGenfv(GL_R, GL_EYE_PLANE,
           (GLfloat * 4)(*tex_matrix[8:12]))
    glTexGenfv(GL_Q, GL_EYE_PLANE,
           (GLfloat * 4)(*tex_matrix[12:16]))

    # Draw objects in the scene, including base plane
    draw_models(True)

    glDisable(GL_ALPHA_TEST)
    glDisable(GL_TEXTURE_2D)
    glDisable(GL_TEXTURE_GEN_S)
    glDisable(GL_TEXTURE_GEN_T)
    glDisable(GL_TEXTURE_GEN_R)
    glDisable(GL_TEXTURE_GEN_Q)

@window.event
def on_key_press(symbol, modifiers):
    if symbol == key.UP:
        light_pos[0] += 5
    if symbol == key.DOWN:
        light_pos[0] -= 5
    gen_shadow_map()

setup_rc()
#time.sleep(0.2)

while not window.has_exit:
    window.clear()
    pyglet.clock.tick()
    window.dispatch_events()
    render()
    window.flip()

