
import pyglet.gl as gl

import ctypes


class NVLoadException(Exception):
    pass

def load_vertex_program(filename):
    vertex_program = gl.GLuint()
    gl.glGenProgramsNV( 1, ctypes.byref(vertex_program) )
    gl.glBindProgramNV( gl.GL_VERTEX_PROGRAM_NV, vertex_program )
    
    #LoadNV_vertex_program("normalmap00.txt", vertex_program)
    data = file(filename).read()
    data = (ctypes.c_ubyte * len(data))(
            *[ord(c) for c in data])

    gl.glLoadProgramNV( gl.GL_VERTEX_PROGRAM_NV,
            vertex_program, len(data), data)


    error_pos = gl.GLint()
    gl.glGetIntegerv( gl.GL_PROGRAM_ERROR_POSITION_NV, ctypes.byref(error_pos))

    if (error_pos.value != -1):
        raise NVLoadException, 'Something bad happened'

    return vertex_program

