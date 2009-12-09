# Copyright (c) 2008 Drew Smathers.
# See LICENSE for details

"""Experimental shader functions.

Building and using a shader fuction:

    from miru.shader import *
    vs = VertexShader(data)
    fs = FragmentShader(data)
    program = createProgram(vs, fs)

    ...


@stability: unstable
"""

from pyglet import gl
import pyglet
import ctypes as c

from miru import imiru

from zope.interface import implements

def _shaderSource(text, shader_type=gl.GL_VERTEX_SHADER):
    buff = c.create_string_buffer(text)
    c_text = c.cast(c.pointer(c.pointer(buff)), c.POINTER(c.POINTER(gl.GLchar)))
    shader = gl.glCreateShader(shader_type)
    gl.glShaderSource(shader, 1, c_text, None)
    return shader


class GLSLException(Exception):
    """Thrown if shader compilation, linking or validation does not
    succeed
    """

def _infolog(handle, log_type='shader'):
    f = { 'shader' : gl.glGetShaderInfoLog, 'program' : gl.glGetProgramInfoLog }[log_type]
    log = (4096 * gl.GLchar)()
    f(handle, 4096, None, log)
    return log.value

class ShaderMixin:
    """Base shader class.  Do not instantiate me directly.
    """
    shader_type = None

    def __init__(self, source):
        self.shader_no = _shaderSource(source, shader_type=self.shader_type)
        gl.glCompileShader(self.shader_no)
        self.status = gl.GLint()
        gl.glGetShaderiv(self.shader_no, gl.GL_COMPILE_STATUS, self.status)
        if not self.status:
            raise gl.GLSLException(_infolog(self.shader_no))

class VertexShader(ShaderMixin):
    """Vertex shader.  Initialize with vertex shader source data (.vs)
    """
    shader_type = gl.GL_VERTEX_SHADER

class FragmentShader(ShaderMixin):
    """Fragment shader. Initialize with fragment shader source data (.fs)
    """
    shader_type = gl.GL_FRAGMENT_SHADER


_programs = {}

class Program:
    """The shader program.
    """

    link_status = gl.GLint(-1)
    validation_status = gl.GLint(-1)

    def __init__(self):
        self.program_no = gl.glCreateProgram()
        _programs[self.program_no] = self

    def attach(self, shader):
        gl.glAttachShader(self.program_no, shader.shader_no)

    def detach(self, shader):
        gl.glDetachShader(self.program_no, shader.shader_no)

    def link(self):
        gl.glLinkProgram(self.program_no)
        gl.glGetProgramiv(self.program_no, gl.GL_LINK_STATUS, self.link_status)
        if not self.link_status:
            raise gl.GLSLException(_infolog(self.program_no, log_type='program'))

    def validate(self):
        gl.glValidateProgram(self.program_no)
        self.validation_status = gl.GLint()
        gl.glGetProgramiv(self.program_no, gl.GL_VALIDATE_STATUS, self.validation_status)
        if not self.validation_status:
            raise gl.GLSLException(_infolog(self.program_no, log_type='program'))

    def enable(self):
        gl.glUseProgram(self.program_no)

def createProgram(*shaders):
    """Create a Program instance with given shader objects.
    
    @raises gl.GLSLException: If linkage or validation of program fails.
    """
    program = Program()
    for shader in shaders:
        program.attach(shader)
    program.link()
    program.validate()
    return program

def disableShaders():
    """Disable shader programs.  Equivalent to gl.glUseProgram(0)
    """
    gl.glUseProgram(0)

def currentProgram():
    """Get the current enabled program.
    """
    pno = gl.GLint()
    gl.glGetIntegerv(gl.GL_CURRENT_PROGRAM, pno)
    return _programs.get(pno.value)


class ShaderView:
    implements(imiru.IShaderRenderStage)

    def __init__(self, program=None, objects=None, camera=None):
        self.program = program
        self.camera = camera
        self.objects = (objects, [])[objects is None]

    def render(self):
        self.program.enable()
        self.camera.render(visible=self.objects)
        disableShaders()
    
    def add_object(self, obj):
        self.objects.append(obj)

    def remove_object(self, obj):
        self.objects.remove(obj)


class ShaderGroup(pyglet.graphics.Group):

    def __init__(self, program, parent=None):
        self.program = program
        pyglet.graphics.Group.__init__(self, parent=parent)
        self.set_state = self.program.enable
        self.unset_state = disableShaders


