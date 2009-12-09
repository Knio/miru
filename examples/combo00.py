"""
Demo setting custom texture coordinates on a cube, rectangle, etc with reflections and lots
of other cool stuff.
"""
import os.path
import logging
from datetime import datetime
import time

from pyglet import options
options['debug_gl'] = 0
#options['debug_gl_trace'] = 1
#options['debug_gl_trace_args'] = 1
options['vsync'] = 0

import pyglet
from pyglet.graphics import Batch
from pyglet.image import load as load_image
from pyglet import clock
from pyglet import app
import pyglet.gl as gl

import miru
from miru.context import context
from miru.ext import geom
#import miru
#from miru.core import Object
#from miru.input import SimpleMouseControl
#from miru.ui import Window
#from miru.context import context
#from miru.ext.geom import Cube, get_vlist
#from miru.graphics import TextureBindGroup
#from miru.camera import LightGroup, DirectionalLight
from miru import effects

logger = logging.getLogger()

media_export = False

resource_base_path = r'/var/forge/testbed/pymgen_resources/examples'
#img_1 = r'py_flux_skin.png'
#img_1 = r'fluxcross.png'
#img_1 = r'fluxcross_nums.png'
#img_1 = r'fluxcross_nums_square_256.png'
#img_1 = r'fluxcross_white-bg.png'
#img_1 = r'fluxcross_white-bg_2048.png'
img_1 = r'demo_cross_01.png'
img_2 = r'py_logo_flux_only.png'
#img_1 = r'python-logo-master-v3-TM.png'
#img_1 = r'200x400.png'
#img_2 = r'/var/forge/testbed/text_tex.png'
#img_1 = r'fluxcross_nums_square.png'
#img_1 = r'numcross.png'
#img_1 = r'cross.png'
sky_1 = r'sky.png'
window_width = 480
window_height = 270
tablet_width = 600
tablet_height = 300
text_left_padding = 5
text_right_padding = 5
text_top_padding = 5
text_bottom_padding = 5

def setLogging(lvl='DEBUG', file_name=r'/var/forge/testbed/cloud3d-%s.log' % datetime.now().strftime('%Y%m%d-%H%M%S')):
    """Set up basic logging with the supplied log level."""
    logger.setLevel(logging.DEBUG)
    logging_file = logging.FileHandler(filename=file_name, mode='w')
    console = logging.StreamHandler()
    format='%(asctime)s %(name)-12s %(levelname)-8s: line %(lineno)s in file %(filename)s: %(message)s'
    formatter = logging.Formatter(format)
    logging_file.setFormatter(formatter)
    console.setFormatter(formatter)
    logger.addHandler(console)
    logger.addHandler(logging_file)
    
def label2texture(label):#, newline_indices):
    vertices = []
    total_glyphs = label._get_glyphs()
    pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
    pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
    
    #texture = pyglet.image.Texture.create(canvas_width,
                                          #canvas_height,
                                          #pyglet.gl.GL_RGB,
                                          #rectangle=not canvas_width==canvas_height)
    #texture._is_rectangle = not canvas_width==canvas_height
    #texture = tex.get_texture(rectangle=True, force_rectangle=True)
    #canvas_width = total_width = xend - xstart
    canvas_width = label.content_width
    if canvas_width < tablet_width: #- text_left_padding - text_right_padding:
        canvas_width = tablet_width #- text_left_padding - text_right_padding
    print 'label\'s width:\t%s' % label.content_width
    print 'end canvas_width:\t%s' % canvas_width
    #canvas_height = total_height = ytop - ybottom
    canvas_height = label.content_height + (tablet_height * 2)
    if canvas_height < tablet_height: #- text_top_padding - text_bottom_padding:
        canvas_height = tablet_height #- text_top_padding - text_bottom_padding
    print 'label\'s height:\t%s' % label.content_height
    print 'end canvas_height:\t%s' % canvas_height
    img = pyglet.image.ImageData(canvas_width,
                                 canvas_height,
                                 'A',
                                 '\0'*(canvas_width*canvas_height))
                                 #'RGBA',
                                 #'\x00\x00\x00\xff'*(canvas_width*canvas_height))
    #img.anchor_x = img.width - img.anchor_x
    #img.anchor_y = img.height - img.anchor_y
    
    texture = img.get_texture(rectangle=not canvas_width==canvas_height,
                              force_rectangle=not canvas_width==canvas_height)
    
    
    #vertex_list = label._vertex_lists[0].vertices[:]
    char_idx = 0
    x_newline_offset = 0
    text = label.text
    #sentences = text.split('\n')
    lines = label._get_lines()
    line_idx = 0
    sentence_idx = 0
    #for vertex_idx, vertex_list in enumerate(label._vertex_lists):
    for line in lines:
        x_newline_offset = 0
        #sentence = sentences[vertex_idx]
        #if char_idx in newline_indices:
            #char_idx += 1
            #x_newline_offset = int(round(vertex_list.vertices[0]))
            #line_idx += 1
            #continue
        #glyphs = total_glyphs[char_idx:len(sentence) + char_idx]
        #line = lines[line_idx]
        if not line.boxes:
            line_idx += 1
            char_idx += 1
            #x_newline_offset = int(round(vertex_list.vertices[0]))
            continue
        box = line.boxes[0]
        glyphs = box.glyphs
        if not glyphs:
            line_idx += 1
            char_idx += 1
            #x_newline_offset = int(round(vertex_list.vertices[0]))
            continue
        line_idx += 1
        #char_idx += 1
        #vertices.extend(vertex_list.vertices[:])
        vertices = label._vertex_lists[sentence_idx].vertices[:]
        sentence_idx += 1
        xpos = map(int, vertices[::2])
        ypos = map(int, vertices[1::2])
        
        # spam spam spam
        if False:
            #texture = pyglet.font.base.GlyphTextureAtlas.create(tablet_width,
            texture = pyglet.image.Texture.create(tablet_width,
                                                  tablet_height,
                                                  pyglet.gl.GL_ALPHA,
                                                  rectangle=not tablet_width==tablet_height)
            for glyph in glyphs:
                #glyph_tex = glyph.get_texture()
                texture.blit_into(glyph.get_image_data(), 50 + glyph.x, 100 + glyph.y, 0)
                
            return texture
        # jtg_sister XXX: see if there needs to be a left and down shift of glyphs
        #y_min = min(ypos)
        #if y_min < 0:
            #y_offset = y_min
            #y_min = 0
        #else:
            #y_offset = 0
        #if y_offset:
            #ypos = [y - y_offset for y in ypos]
        x_min = min(xpos)
        if x_min != 0:
            x_offset = x_min
            x_min = 0
        else:
            x_offset = 0
        if x_offset or text_left_padding:
            xpos = [x - x_offset + text_left_padding for x in xpos]
        xstart = xpos[0]
        xend = xpos[-1] + glyphs[-1][1].width
        #canvas_width = total_width = xend - xstart
        total_width = xend - xstart
        #if canvas_width < tablet_width - text_left_padding - text_right_padding:
            #canvas_width = tablet_width - text_left_padding - text_right_padding
        #width = int(round(1.10 * (xend - xstart)))
        ytop = max(ypos)
        #yend = max(glyph.height+ystart for glyph in glyphs)
        #yend = max(ypos)
        ybottom = min(ypos)
        #height = int(round(1.10 * (yend - ytop)))
        #canvas_height = total_height = ytop - ybottom
        total_height = ytop - ybottom
        #if canvas_height < tablet_height - text_top_padding - text_bottom_padding:
            #canvas_height = tablet_height - text_top_padding - text_bottom_padding
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
        
        #texture = pyglet.image.Texture.create(canvas_width,
                                              #canvas_height,
                                              #pyglet.gl.GL_RGB,
                                              #rectangle=not canvas_width==canvas_height)
        #texture._is_rectangle = not canvas_width==canvas_height
        #texture = tex.get_texture(rectangle=True, force_rectangle=True)
        #canvas_width = canvas_width+text_left_padding+text_right_padding
        #canvas_height = canvas_height+text_top_padding+text_bottom_padding
        #img = pyglet.image.ImageData(canvas_width,
                                     #canvas_height,
                                     #'A',
                                     #'\0'*(canvas_width*canvas_height))
                                     #'RGBA',
                                     #'\x00\x00\x00\xff'*(canvas_width*canvas_height))
        #img.anchor_x = img.width - img.anchor_x
        #img.anchor_y = img.height - img.anchor_y
        #texture = img.get_texture(rectangle=not canvas_width==canvas_height,
                                  #force_rectangle=not canvas_width==canvas_height)
        for glyph_run, x, y in zip(glyphs, xpos[::4], ypos[::4]):
            #if newline_idx in newline_indices:
                #newline_idx += 1
                #x_newline_offset = x
                #continue
            char_idx += 1
            glyph_run_num, glyph = glyph_run
            data = glyph.get_image_data()
            #data.anchor_x = glyph.width - glyph.anchor_x
            #data.anchor_y = glyph.height - glyph.anchor_y
            pitch = data.pitch
            data_string = data.data
            new_data = list()
            num_iter = len(data_string) / pitch
            for idx in range(num_iter):
                new_data.append(data_string[-1 * ((idx + 1) * pitch):-1 * (idx * pitch) or None])
            data.set_data(data.format, data.pitch, ''.join(new_data))
            
            y = canvas_height - total_height + y - 1 - tablet_height
            x = x - x_newline_offset
            print (x, y)
            pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
            pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
            texture.blit_into(data, x, y, 0)
            
    #return texture.get_transform(flip_y=True)
    return texture

def animateText (text_tex, x, y, width, height, dx, dy, dz, duration_frames):
    #duration = fps * 10
    tex_list = []
    total_frames = duration_frames * fps
    #dy = -1 * int(round(text_tex.height / duration))
    for idx in range(int(round(total_frames))):
        text_tex_region = text_tex.get_region(x,
                                              y + (int(round(idx * dy))),
                                              width,
                                              height,)
        chunk_tex = pyglet.image.ImageData(text_tex_region.width,
                                           text_tex_region.height,
                                           'A',
                                           '\0' * (text_tex_region.width * text_tex_region.height)).get_texture(rectangle=True)
        chunk_tex.blit_into(text_tex_region.get_image_data(), 0, 0, 0)
        
        tex_list.append(chunk_tex)
    img_seq = pyglet.image.Animation.from_image_sequence(tex_list, 0.01, loop=True)
    #img_seq = pyglet.image.UniformTextureSequence()
    #img_seq.texture_sequence = tex_list

    return img_seq

def animMovie (obj, frame):
    second = int(round(frame/fps))
    # and now for something completely different
    if second < 10:
        pass
    elif second < 13:
        dx = -1 * 45 / 3 / fps
        obj.angle.x += dx
    elif second < 23:
        pass
    elif second < 26:
        dx = 45 / 3 / fps
        dy = 45 / 3 / fps
        obj.angle.x += dx
        obj.angle.y += dy

# video and frame recording
from subprocess import Popen, PIPE, call, check_call, STDOUT

frame_idx = 0 
fps = 29.97
render_time = 15    # seconds
frame_max = round(fps * render_time)
frame_file_name_format = 'test-%07d.png'
ffmpeg_exec_path = r'ffmpeg'
output_base_path = r'/var/forge/testbed/3dframes'
vid_out_path = r'/var/forge/testbed/cloud3d-%s.mp4' % datetime.now().strftime('%Y%m%d-%H%M%S')
text_anim_frame = 0

if media_export:
    setLogging()

maroon = (0.25, 0.0, 0.0, 1.0)
black = (0.0, 0.0, 0.0, 1.0)
start_time = time.time()
window = miru.ui.Window(window_width,window_height, clear_color=black)
context.window = window
context.osd.add_object(clock.ClockDisplay())
context.control = miru.input.SimpleMouseControl()
#main_light = miru.camera.DirectionalLight(pos=[1.0,1.0,0.5])
main_light = miru.camera.DirectionalLight(pos=[0.0,0.0,1.0])
#sky_light = miru.camera.DirectionalLight(pos=[0.0,1.0,0.0])
context.camera.lights = miru.camera.LightGroup([
    main_light,])
    #sky_light,])
#context.camera.pos.z = 5
context.camera.pos= (0,1.25,4)
pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)

sky_img = pyglet.image.load(os.path.join(resource_base_path, sky_1))
sky_tex = sky_img.get_texture(rectangle=True, force_rectangle=True)
sky_batch = pyglet.graphics.Batch()
sky_shape = geom.Square(width=192, height=108, depth=0, tex=sky_tex)
sky_group = miru.graphics.TextureBindGroup(sky_tex, sky_tex.target, parent=None, gencoords=False)
sky_vlist = geom.get_vlist(sky_shape, sky_batch, sky_group)
sky_obj = miru.core.Object(sky_batch)
sky_obj.angle.x = 90
sky_obj.pos.y = 7
context.add_object(sky_obj)

skin_tex = load_image(os.path.join(resource_base_path, img_1)).get_texture()#rectangle=True, force_rectangle=True)
geom_batch = Batch()
tex_group = miru.graphics.TextureBindGroup(skin_tex, skin_tex.target, parent=None, gencoords=False)
geom_mesh = geom.Cube()
geom_mesh.texcoord_data = [
    0.245, 0.505, 0.245, 0.745, 0.005, 0.746, 0.005, 0.505, # left 
    0.495, 0.755, 0.495, 0.995, 0.255, 0.995, 0.255, 0.755, # back 
    0.745, 0.505, 0.745, 0.745, 0.505, 0.745, 0.505, 0.505, # right
    0.255, 0.745, 0.255, 0.505, 0.495, 0.505, 0.495, 0.745, # top
    0.255, 0.245, 0.255, 0.005, 0.495, 0.005, 0.495, 0.245, # bottom
    0.255, 0.495, 0.255, 0.255, 0.495, 0.255, 0.495, 0.495 ] # front

#cube_geom.texcoord_data = [
    #0.333, 0.500, 0.333, 0.750, 0.000, 0.750, 0.000, 0.500, #left
    #0.667, 0.750, 0.667, 1.000, 0.333, 1.000, 0.333, 0.750, #back
    #1.000, 0.500, 1.000, 0.750, 0.667, 0.750, 0.667, 0.500, #right
    #0.333, 0.750, 0.333, 0.500, 0.667, 0.500, 0.667, 0.750, #top
    #0.333, 0.250, 0.333, 0.000, 0.667, 0.000, 0.667, 0.250, #bottom
    #0.333, 0.500, 0.333, 0.250, 0.667, 0.250, 0.667, 0.500, #front
    #]
#geom_mesh.texcoord_data = [
            #-1.0, 0.0, -1.0, -1.0, 0.0, -1.0, 0.0, 0.0,    #left
            #-1.0, 0.0, -1.0, -1.0, 0.0, -1.0, 0.0, 0.0,    #back
            #-1.0, 0.0, -1.0, -1.0, 0.0, -1.0, 0.0, 0.0,    #right
            #0.0, -1.0, 0.0, 0.0, -1.0, 0.0, -1.0, -1.0,    #top
            #0.0, -1.0, 0.0, 0.0, -1.0, 0.0, -1.0, -1.0,    #bottom
            #0.0, -1.0, 0.0, 0.0, -1.0, 0.0, -1.0, -1.0 ]   #front
#geom_mesh.texcoord_data = [
            #20.0, 0.0, 20.0, 10.0, 0.0, 10.0, 0.0, 0.0,    #left
            #20.0, 0.0, 20.0, 10.0, 0.0, 10.0, 0.0, 0.0,    #back
            #20.0, 0.0, 20.0, 10.0, 0.0, 10.0, 0.0, 0.0,    #right
            #0.0, 10.0, 0.0, 0.0, 20.0, 0.0, 20.0, 10.0,    #top
            #0.0, 10.0, 0.0, 0.0, 20.0, 0.0, 20.0, 10.0,    #bottom
            #0.0, 10.0, 0.0, 0.0, 20.0, 0.0, 20.0, 10.0 ]   #front

geom_vlist = geom.get_vlist(geom_mesh, geom_batch, tex_group)
geom_obj = miru.core.Object(geom_batch)
geom_obj.pos = (3.5, 1.50, -5)
context.add_object(geom_obj)
pattern = pyglet.image.SolidColorImagePattern(color=(0,0,0,200))
#pattern = pyglet.image.CheckerImagePattern(
        #(255,255,255,200), (0,0,0,200))
bg_tex = pattern.create_image(64, 64).get_texture()
coords = []
for i in range(0, len(bg_tex.tex_coords), 3):
    coords.extend(bg_tex.tex_coords[i:i+3] + (0.125 / 2,))
ground_batch = pyglet.graphics.Batch()
bg_group = miru.graphics.TextureBindGroup(bg_tex, bg_tex.target, parent=None, gencoords=False)
ground_batch.add(4, pyglet.gl.GL_QUADS, bg_group,
        ('v3f', [-100, 0, -100, 100, 0, -100, 100, 0, 100, -100, 0, 100]),
        ('t4f', coords))
ground_obj = miru.core.Object(ground_batch)
#ground_obj.pos.y = -1.5

#context.add_object(ground_obj)
refl = effects.Reflection(camera=context.camera, ground=ground_obj, objects=[geom_obj])
context.camera.effects.append(refl)

text_color = (0, 255, 255, 255)
text_string = '''This is the first sentence.  This is a second connected sentence.
This is a third newlined sentence.

Finally, this is a fourth sentence with a blank line separaring it (two newlines).

Cheers'''
#text_string = 'one.  two\nthree\n\nfour'
#newline_indices = [idx for idx, char in enumerate(text_string) if char == '\n']

text_batch = pyglet.graphics.Batch()
label = pyglet.text.Label(text=text_string,
                          font_name='Helvetica',
                          font_size=30,
                          bold=True,
                          italic=False,
                          color=text_color,
                          x=0,
                          y=0,
                          width=tablet_width,
                          multiline=True,
                          halign='center')
                          #batch=text_batch)
html_string = '''
<h1>HTML labels in pyglet</h1>

<p align="center"><img src="%s" /></p>

<p>HTML labels are a simple way to add formatted text to your application.
Different <font face="Helvetica,Arial" size=+2>fonts</font>, <em>styles</em>
and <font color=maroon>colours</font> are supported.

<p>This window has been made resizable; text will reflow to fit the new size.
'''
location = pyglet.resource.FileLocation(resource_base_path)
html_label = pyglet.text.HTMLLabel(location=location,
                                   text=html_string % img_2,
                                   )
text_tex = label2texture(label)#, newline_indices)
#text_img = pyglet.image.load(os.path.join(resource_base_path, img_1))
#text_tex = text_img.get_texture()
#text_batch.add(4, pyglet.gl.GL_QUADS, text_group,
        #('v3f', [-1, 1.5, 0, -1, -1.5, 0, 1, -1.5, 0, 1, 1.5, 0]),
        #('t2f', (0,text_tex.height,
                 #0,0,
                 #text_tex.width,0,
                 #text_tex.width,text_tex.height)))
text_height = tablet_height
text_bottom = text_tex.height - tablet_height
text_left = 0
text_width = text_tex.width #- text_left_padding - text_right_padding
duration = 10
dx = dz = 0
dy = -1 * (text_tex.height - tablet_height) / (duration * fps)
text_anim_credits = animateText(text_tex,
                                text_left,
                                text_bottom,
                                text_width,
                                text_height,
                                dx,
                                dy,
                                dz,
                                duration)
#text_tex_region = text_tex.get_region(text_left,
                                      #text_bottom,
                                      #text_width,
                                      #text_height,)
#chunk_tex = pyglet.image.ImageData(text_tex_region.width,
                                   #text_tex_region.height * 3,
                                   #'A',
                                   #'\0' * (text_tex_region.width * text_tex_region.height * 3)).get_texture(rectangle=True)
#chunk_tex.blit_into(text_tex_region.get_image_data(), 0, 0, 0)
frame = 0
chunk_tex = text_anim_credits.frames[frame].image.get_texture()
text_tablet = geom.Square(width=6,
                          height=3,
                          depth=0,
                          tex=chunk_tex)

text_bind_group = miru.graphics.TextureBindGroup(chunk_tex, chunk_tex.target, parent=None, gencoords=False)
#text_transform_group = miru.graphics.TextureTransformGroup(texture=text_tex,
                                                           #translation=(5, 5, 0),)
                                                           #group=text_bind_group)

tablet_vlist = geom.get_vlist(text_tablet, text_batch, text_bind_group)
tablet_obj = miru.core.Object(text_batch)
tablet_obj.pos = (-2.25, 1.50, -5)
#tablet_obj.angle.y = 30
#tablet_obj.angle.x = -45

context.add_object(tablet_obj)

v = 35
def update(dt):
    #global text_bottom
    global frame
    global text_anim_frame
    dy = dt * v
    geom_obj.angle.y += dy
    #text_bottom -= 10
    #chunk_tex = animateText(text_tex, text_left, text_bottom, text_width, text_height)
    frame += 1
    text_anim_frame += 1
    if text_anim_frame >= len(text_anim_credits.frames):
        text_anim_frame = 0
    chunk_tex = text_anim_credits.frames[text_anim_frame].image.get_texture()
    text_bind_group.texture = chunk_tex
    animMovie(tablet_obj, frame)
    
clock.schedule_interval(update, 1/fps)
#clock.schedule(update)

if not os.path.exists(output_base_path):
    os.mkdir(output_base_path)

#@window.event
#def on_draw():
while not window.has_exit and not frame_idx > frame_max:
    window.clear()
    pyglet.clock.tick()
    window.dispatch_events()
    #pyglet.gl.glPolygonMode(pyglet.gl.GL_FRONT_AND_BACK, pyglet.gl.GL_LINE)
    pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
    pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
    context.render()
    #text_tex.blit(x=0, y=0)
    #label.draw()
    window.flip()
    if media_export:
        frame_path = os.path.join(output_base_path, frame_file_name_format % frame_idx)
        pyglet.image.get_buffer_manager().get_color_buffer().save(frame_path,)
        frame_idx += 1
    
#pyglet.app.run()
stop_time = time.time()
elapsed_time = stop_time - start_time
print 'This crap took %s minutes and %s seconds to create' % (int(round(elapsed_time / 60)), elapsed_time % 60) 

if media_export:
    cmd_list = []
    cmd_list.append(ffmpeg_exec_path)
    #cmd_list.append('-vpre')
    #cmd_list.append('%(preset)' % kwargs)
    cmd_list.append('-y')
    cmd_list.append('-vpre')
    cmd_list.append('libx264-hq')
    cmd_list.append('-vpre')
    cmd_list.append('libx264-ipod640')
    cmd_list.append('-f')
    cmd_list.append('image2')
    cmd_list.append('-i')
    cmd_list.append(os.path.join(output_base_path, frame_file_name_format))
    
    cmd_list.append('-r')
    cmd_list.append(str(fps))
    cmd_list.append('-s')
    cmd_list.append('%(width)sx%(height)s' % {'width': window_width, 'height': window_height})
    cmd_list.append('-f')
    cmd_list.append('mp4')
    cmd_list.append('-vcodec')
    cmd_list.append('libx264')
    
    #cmd_list.append('-aspect')
    #cmd_list.append('16:9')
    cmd_list.append('-crf')
    cmd_list.append('18.0')
    cmd_list.append(vid_out_path)
    
    p = Popen(cmd_list, stdout=PIPE, stderr=STDOUT)
    stdoutdata, stderrdata = p.communicate()
    logger.debug('Path:%s\n\tstdout:%s\t\n\tstderr:\t%s' % (vid_out_path,
                                                            stdoutdata,
                                                            stderrdata))